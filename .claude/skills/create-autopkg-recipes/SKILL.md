---
name: create-autopkg-recipes
description: |
  Write AutoPkg recipes for a macOS app from a vendor URL, of any type:
  download, pkg, munki or install. Use whenever the user asks you to create,
  generate, add or set up AutoPkg recipes for an app.
  Keywords:
  - AutoPkg, autopkg
  - .download.recipe.yaml, .pkg.recipe.yaml, .munki.recipe.yaml, .install.recipe.yaml
  - YAML recipe, yaml-recipe
  - homebysix-recipes, Munki, pkg
  - code signature, CodeSignatureVerifier, strict verification, deep verification
  - EndOfCheckPhase, check phase, download cache, dmg mount
user-invocable: true
---

# Create AutoPkg recipes

Write YAML recipes for a macOS app, following the conventions in this repo.
Every recipe must check the code signature. This repo does not accept an
unsigned app. Every recipe must also leave the download closed until the check
phase ends, so a CI run can reuse a cached download. Test the download recipe
and the pkg recipe end to end before you hand the work over.

Follow the house style, [[plain-technical-english]], in every word of prose you
write. That covers the `Description` field, the comments in the YAML, your
report at step 9, and the commit message. Identifiers, processor names, input
keys and requirement strings are technical names, so they stay exact.

## 1. Check for a recipe that already exists

Run `autopkg search <AppName>.download`. Try the name with the vendor in front
as well, such as `Google<AppName>`.

A match in any repo means someone has done this work already. Report the match.
Ask the user before you build anything.

## 2. Gather the metadata

Collect the download URL, the appcast or GitHub releases page, the developer, a
description and the display name.

Do not download the whole file yet. Send a HEAD request with `curl -sIL`.

Never build a domain from a relative URL. Resolve it against the domain you
fetched.

A GitHub Pages site, such as `*.github.io`, often returns an HTML shell. It then
loads the content with JavaScript. Fetch those pages in full with `curl`.

Read the releases of the sibling GitHub repo as well, with
`gh release list -R <owner>/<repo>`. That is the quickest source of the version
and the asset names.

Stop and ask the user in 4 cases. Do not build, and do not drop the app quietly:

- the app is on the Mac App Store only
- the app is paid only, with no public trial dmg
- the app is on TestFlight or in beta only
- the vendor ships source only, with no prebuilt binary

## 3. Check the code signature

This repo accepts an app only when it carries a Developer ID signature you can
check. Download the artifact once. Confirm the signature is intact before you
write anything:

```
codesign --verify --strict --deep -vvv "<App>.app"      # or the .pkg
codesign -dvvv --requirements - "<App>.app" 2>&1        # designated requirement and Team ID
spctl -a -vvv "<App>.app"                                # Gatekeeper assessment
```

Take 2 things from the output: the designated requirement string, and the Team
ID from `subject.OU`. You pin both in the recipe. For a `.pkg`, run
`pkgutil --check-signature "<App>.pkg"` instead.

Stop in 3 cases: the app is unsigned, the app is ad-hoc signed, or it fails
strict or deep verification. Write no recipe. Never fall back to a weaker check.
Report the reason and let the user decide. An unsigned binary is outside what
this skill does.

## 4. Write the recipes

Recipes here are AutoPkg YAML, in files named `.recipe.yaml`. That format needs
`MinimumVersion: "2.3"` or higher. Model each new recipe on one in this repo
that ships the same way. A download recipe starts like this:

```yaml
Description: Downloads the latest version of AppName.
Identifier: com.github.jrmfong.download.AppName
MinimumVersion: "2.3"

Input:
  NAME: AppName
  DOWNLOAD_MISSING_FILE: "True"

Process:
  - Processor: URLDownloaderPython
    Arguments:
      download_missing_file: "%DOWNLOAD_MISSING_FILE%"
      url: https://example.com/AppName.dmg
      filename: "%NAME%.dmg"

  # The check phase ends here. Nothing above this line opens the dmg.
  - Processor: EndOfCheckPhase

  # The first step that mounts the dmg, and it sits after the marker.
  - Processor: CodeSignatureVerifier
    Arguments:
      input_path: "%pathname%/AppName.app"
      strict_verification: true
      deep_verification: true
      requirement: >-
        anchor apple generic and identifier "com.example.AppName" and
        (certificate leaf[field.1.2.840.113635.100.6.1.9] exists or
        certificate 1[field.1.2.840.113635.100.6.2.6] exists and
        certificate leaf[field.1.2.840.113635.100.6.1.13] exists and
        certificate leaf[subject.OU] = "7D2YX5DQ6M")
```

Always set both `strict_verification: true` and `deep_verification: true`.
Strict verification rejects a bundle that carries extra or unsealed files. Deep
verification checks the nested code, such as frameworks, helpers and XPC
services.

Only one of the 2 changes what codesign does. `deep_verification` already
defaults to `true` in `CodeSignatureVerifier`, so writing it is documentation.
`strict_verification` has no default, so codesign runs without `--strict` until
you set it. Leave it out and a bundle carrying extra or unsealed files passes.
Write both anyway, so the next reader sees which checks apply.

Most third-party download recipes set neither. Read the parent before you rely
on it, and say so in your report at step 9 when it runs without `--strict`.

The `requirement` is the designated requirement string you captured at step 3.
It is the strictest form, so use it rather than `expected_authority_names`.
Quote a `subject.OU` value, even one that starts with a digit. Keep the whole
requirement in a YAML block scalar, `>-`. That keeps it as one logical line.

Some downloads sit behind a page or an API. You can tell in 3 ways: a HEAD
request returns HTML, it returns a 4xx status, or JavaScript starts the
download. Chain `URLTextSearcher` steps to pull out the real URL. Feed that URL
to `URLDownloader` with `result_output_var_name: url`:

```yaml
  - Processor: URLTextSearcher
    Arguments:
      url: https://example.com/download
      re_pattern: 'href="(?P<url>https://[^"]+\.dmg)"'
      result_output_var_name: url
```

Write a custom processor for a structured API with tracks, locales or channels.
Name it `<Vendor><Purpose>InfoProvider.py`. Subclass `autopkglib.URLGetter`.
That keeps the same regular expression out of several recipes. For one URL
behind an API, `URLTextSearcher` is enough.

## 5. Order the process so CI can cache the download

Put `EndOfCheckPhase` straight after the download processor. Put every step that
opens the download after it. A CI run can then restore a cached download and do
no further work on an app that has not changed.

### The rule AutoPkg applies

`autopkg --check` does not stop at the first `EndOfCheckPhase`. It deletes steps
from the end of the merged chain until the last one left is the marker, in
`/Library/AutoPkg/autopkg` around line 2213:

```python
while (len(recipe["Process"]) >= 1
       and recipe["Process"][-1]["Processor"] != "EndOfCheckPhase"):
    del recipe["Process"][-1]
```

So every step before the last marker runs in the check phase, across the parent
recipe and the child recipe together.

A CI runner caches the download metadata, not the file. It leaves an empty
placeholder where the skipped download would be. Any step before the marker then
reads a file with no contents, and the recipe fails on the nights the cache
works. That reads as a broken recipe rather than a caching problem.

Mounting an empty placeholder is the usual symptom:

```
hdiutil: attach failed - image not recognized
```

A later step reports `is not mounted` for the same reason. In the caching
experiment of 15 September 2026 this was every failure: RubyMine, JabraDirect
and AdobeCreativeCloudInstallerUniversal, 3 recipes out of 71. Each one failed
only because its download had been skipped correctly.

### Rules for the marker

- write one `EndOfCheckPhase` in the whole chain, and write it in the download
  recipe only
- put it straight after the last download processor
- never add a second marker, such as a recipe that downloads twice. The trim
  keeps everything up to the last one, so the first download gets processed in
  the check phase
- never put a marker in a pkg, munki or install recipe. The parent already
  carries one, and a second marker pulls the parent's signature check into the
  check phase
- put nothing before the marker that opens the download

### A third-party parent may break the cache

A pkg recipe here can name a `ParentRecipe` from another repo, such as
`com.github.dataJAR-recipes.download.VeraCrypt`. You do not control where that
parent puts its marker, and the trim runs over the merged chain. Read the parent
before you rely on it:

```
autopkg info -p <App>/<App>.pkg.recipe.yaml
```

Check 2 things: the parent holds one marker, and no step that opens the download
sits above it. When it fails either check, say so. The fix is to fork the parent
into this repo with the marker moved above every step that opens the download.
Nothing is weakened by the move, because a full build still runs every step.

### Processors that open the download

Keep all of these after the marker:

| Processor | What it does to the download |
|-----------|------------------------------|
| `AppDmgVersioner` | mounts the dmg |
| `CodeSignatureVerifier` | mounts the dmg when `input_path` starts with `%pathname%` |
| `Unarchiver` | reads the zip |
| `Versioner` | mounts the dmg to read `Info.plist` |
| `Copier` | mounts the dmg to copy out of it |
| `DmgCreator` | reads the source |
| `FlatPkgUnpacker` | expands the pkg |
| `PkgPayloadUnpacker` | reads the payload |
| `AppPkgCreator`, `PkgCopier` | read the app or the pkg |
| `FileFinder`, `FileMover`, `PathDeleter` | read or move the file |
| `XarExtractSingleFile`, `XPathParser` | read inside the file |

A `URLTextSearcher`, a `GitHubReleasesInfoProvider` or a custom info provider is
safe before the download. Each one reads a web page or an API, not the
downloaded file.

### The safe order for each shape

| Shape | Order |
|-------|-------|
| dmg | `URLDownloaderPython`, `EndOfCheckPhase`, `CodeSignatureVerifier`, `Versioner` |
| zip | `URLDownloaderPython`, `EndOfCheckPhase`, `Unarchiver`, `CodeSignatureVerifier`, `Versioner` |
| pkg | `URLDownloaderPython`, `EndOfCheckPhase`, `CodeSignatureVerifier` |
| URL behind a page | `URLTextSearcher`, `URLDownloaderPython`, `EndOfCheckPhase`, then as above |

A Sparkle appcast can enclose a zip rather than a dmg. Read the type of the
enclosure URL in the appcast before you assume a dmg. A zip needs `Unarchiver`
between the marker and `CodeSignatureVerifier`.

### Which downloader CI can cache

AutoPkg has 2 downloaders, and they record the download differently:

- `URLDownloader` writes the ETag and Last-Modified as extended attributes on
  the file. `tar` drops those on macOS by default, so a restored file is ignored
  and the download happens again
- `URLDownloaderPython` writes a `.info.json` beside the file. That survives any
  `tar`, but the CI cache must hold the sidecar as well as the metadata

This repo uses `URLDownloaderPython`. Tell whoever runs the CI job to cache
`AutoPkg/Cache/*/downloads/*.info.json` alongside the metadata cache. Without
the sidecar the downloader reports `missing download info (FileNotFoundError)`
and downloads the file again.

### Do not add a StopProcessingIf guard

You will see this pattern in other repos, and in this repo's own history. Do not
add it to a new recipe:

```yaml
  - Processor: StopProcessingIf
    Arguments:
      predicate: "download_changed == False AND %BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED% == False"
```

It is meant to skip the mount, the unarchive, the signature check and the copy
when the vendor file has not changed. That is 1 to 2 seconds on a typical recipe
here, and 3 other mechanisms already cover it:

| Mechanism | What it skips |
| --- | --- |
| the check phase and the metadata cache | the whole run |
| an ETag or Last-Modified match in the downloader | the download body |
| `PkgCreator` finding the same version and identifier | the package build |

The guard also sits below `EndOfCheckPhase`, so it never runs during the check
phase at all. It cannot speed up the part a CI cache speeds up.

Worse, a 2-phase runner turns it into a silent failure. The check phase
downloads the file, so the runner sees a new download and starts the full run.
The full run finds that same file in the cache, so `download_changed` is `False`
and the guard stops the recipe before it packages. Nothing is staged, and the job
still reports success. A single-phase local `autopkg run` never reaches that
point, so the recipe packages fine on your machine.

That is why every consumer ends up switching it back off. In the pipeline that
runs these recipes, 24 of 72 overrides carry
`BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED: 'True'` for no other reason.

Leave the guard out and leave its input key out. A recipe you inherit that has
one is worth cleaning up.

## 6. Conventions

Follow these conventions in every recipe:

- name the directory after the app, or after the developer when a directory for
  them exists
- use no spaces in a filename, even when `Input/NAME` has one
- write the identifier as `com.github.jrmfong.<type>.<App>`, with no spaces
- match `MinimumVersion`, `Input/NAME`, `ParentRecipe` and the processor order
  to the recipes next to it
- set `MinimumVersion` to the highest AutoPkg version the whole chain needs, and
  never below `"2.3"`
- give every download recipe a `CodeSignatureVerifier` step, which is required
  rather than optional
- set both `strict_verification: true` and `deep_verification: true` on every
  `CodeSignatureVerifier` step
- take the `requirement` string from steps 3 and 4
- put `EndOfCheckPhase` straight after the download
- add no `StopProcessingIf` guard, for the reason in step 5
- add a `Comment:` to a step whose reason is not obvious from its arguments
- set both `unattended_install` and `unattended_uninstall` to `true` in a munki
  `pkginfo`
- write the munki `description` as one plain sentence of fact, with no marketing
  copy and no emoji

The app "Tight Studio" gets `TightStudio.pkg.recipe.yaml`. The pre-commit hooks
catch a `MinimumVersion` mismatch.

Never leave the munki `description` empty. Check it against the app itself if
you are unsure: mount the dmg, read `Info.plist`, or run `strings` over the
binary.

`plutil -lint` cannot parse YAML. Run `autopkg audit <recipe>` or a YAML linter
instead. Then confirm the recipe loads with `autopkg info <recipe>`.

Some apps ship one build per architecture. Put `%ARCH%` in `asset_regex`,
`re_pattern` or `url`. Default `Input/ARCH` to `arm64`. Say in the `Description`
what the other values are.

Do not set the munki `supported_architectures` from `%ARCH%`. The vendor and
munki often use different names for an architecture. Setting it also stops
Rosetta for no reason. Set it only when the binary cannot run under Rosetta.

You will see 2 things in other repos. Recognise them, but do not add them unless
the user asks:

- a pseudo-universal pkg that merges the 2 architecture builds, where a true
  universal build or 2 recipes is better
- a third-party aggregator such as Homebrew or MacUpdate as the source of the
  binary or the version

Go to the vendor direct. Every extra hop is someone else to trust.

## 7. Hard stops for security

Stop and report in these cases:

- the app has no code signature you can check
- the app has an ad-hoc signature
- the app fails strict or deep verification at step 3
- the download URL or the appcast uses HTTP rather than HTTPS

The first 3 cases are not negotiable. For HTTP, explain the risk to the user and
wait. Carry on only when they say yes.

## 8. Test the recipes end to end

```
autopkg run -vvq <App>/<App>.download.recipe.yaml <App>/<App>.pkg.recipe.yaml
```

The install and munki recipes write to `/Applications` and to the munki repo, so
do not run them.

A trust-info warning on an uncommitted recipe is normal.

A `CodeSignatureVerifier` failure here means the recipe cannot ship. Fix the
requirement string or the input path, or reject the app.

Test the check phase as well, because a single-phase run hides the caching
problem at step 5:

```
autopkg run --check -vv <App>/<App>.download.recipe.yaml
```

The output must stop at `EndOfCheckPhase`. No mount, no signature check and no
`Unarchiver` line may appear before it.

## 9. Report

Say what you created. Say what tested clean. Name any caveat, such as unusual
signing, a developer name that does not match, or a test you skipped.

Do not commit or push unless the user asks.

## Related

- house style for every word of prose you write: [[plain-technical-english]]
