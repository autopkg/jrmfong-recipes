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
user-invocable: true
---

# Create AutoPkg recipes

Write YAML recipes for a macOS app, following the conventions in this repo.
Every recipe must check the code signature. This repo does not accept an
unsigned app. Test the download recipe and the pkg recipe end to end before you
hand the work over.

Follow the house style, [[plain-technical-english]], in every word of prose you
write. That covers the `Description` field, the comments in the YAML, your
report at step 8, and the commit message. Identifiers, processor names, input
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
  BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED: "False"

Process:
  - Processor: URLDownloader
    Arguments:
      url: https://example.com/AppName.dmg
      filename: "%NAME%.dmg"

  - Processor: EndOfCheckPhase

  - Processor: StopProcessingIf
    Arguments:
      predicate: "download_changed == False AND %BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED% == False"

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
services. Leave either one out and a tampered bundle can pass.

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

## 5. Conventions

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
- add a `StopProcessingIf` guard after `EndOfCheckPhase`, and declare its input
  key
- order a zip with no appcast as `URLDownloader`, `EndOfCheckPhase`,
  `Unarchiver`, `CodeSignatureVerifier`, `Versioner`
- set both `unattended_install` and `unattended_uninstall` to `true` in a munki
  `pkginfo`
- write the munki `description` as one plain sentence of fact, with no marketing
  copy and no emoji

The app "Tight Studio" gets `TightStudio.pkg.recipe.yaml`. The pre-commit hooks
catch a `MinimumVersion` mismatch.

A Sparkle appcast can enclose a zip rather than a dmg. That also needs
`Unarchiver` between `EndOfCheckPhase` and `CodeSignatureVerifier`. Read the
type of the enclosure URL in the appcast before you assume a dmg.

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

### Stop early when the download is unchanged

An undeclared input breaks the recipe on every run, so declare the input key
first. NSPredicate reads the leading `%B` as a format specifier, and the run
fails with "Too few arguments for format string". Add this to `Input`:

```yaml
  BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED: "False"
```

Then add the guard straight after `EndOfCheckPhase`:

```yaml
  - Processor: StopProcessingIf
    Arguments:
      predicate: "download_changed == False AND %BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED% == False"
```

Know what the guard does and does not save. `URLDownloader` already skips the
download body on an ETag or Last-Modified match. `PkgCreator` already skips the
build when a package of the same version and identifier exists. The guard
removes the work between those 2 skips: the mount, the unarchive, the signature
check and the copy. That is 1 to 2 seconds on a typical recipe here.

The guard pays for itself when the chain uploads or imports, such as a
`MunkiImporter` step or a Jamf upload. Weigh 2 costs against it.
`CodeSignatureVerifier` stops running on a cached artifact. The whole chain also
stops, so a pkg recipe builds nothing until you set
`BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED=True`.

## 6. Hard stops for security

Stop and report in these cases:

- the app has no code signature you can check
- the app has an ad-hoc signature
- the app fails strict or deep verification at step 3
- the download URL or the appcast uses HTTP rather than HTTPS

The first 3 cases are not negotiable. For HTTP, explain the risk to the user and
wait. Carry on only when they say yes.

## 7. Test the recipes end to end

```
autopkg run -vvq <App>/<App>.download.recipe.yaml <App>/<App>.pkg.recipe.yaml
```

The install and munki recipes write to `/Applications` and to the munki repo, so
do not run them.

A trust-info warning on an uncommitted recipe is normal.

A `CodeSignatureVerifier` failure here means the recipe cannot ship. Fix the
requirement string or the input path, or reject the app.

## 8. Report

Say what you created. Say what tested clean. Name any caveat, such as unusual
signing, a developer name that does not match, or a test you skipped.

Do not commit or push unless the user asks.

## Related

- house style for every word of prose you write: [[plain-technical-english]]
