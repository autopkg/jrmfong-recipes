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
  - code signature, CodeSignatureVerifier, strict verification
user-invocable: true
---

# Create AutoPkg recipes

Hand-author YAML recipes for a macOS app, following the conventions in this
repo. Every recipe must check the code signature strictly. This repo does not
accept an unsigned app. Test the download recipe and the pkg recipe end to end
before you hand the work over.

The prose you write alongside a recipe follows the house style,
[[plain-technical-english]]. That covers the `Description` field, comments in the
YAML, your report at step 8, and the commit message. Identifiers, processor
names, input keys and code signature requirement strings are technical names, so
they stay exact.

## 1. Check for a recipe that already exists

Run `autopkg search <AppName>.download`. Try the vendor-prefixed name too, such
as `Google<AppName>`.

A match in any repo means someone has done this work. Report the match and ask
the user before you build anything.

## 2. Gather the metadata

Collect the download URL, appcast or GitHub releases page, the developer, a
description and the display name.

Do not download the whole file yet. Send a HEAD request with `curl -sIL`.

Never build a domain from a relative URL. Resolve it against the domain you
actually fetched.

A GitHub Pages site, such as `*.github.io`, often returns an HTML shell and
loads the content with JavaScript. Fetch the page in full with `curl` for those.
Read the releases of the sibling GitHub repo as well, with
`gh release list -R <owner>/<repo>`. That is the quickest source of the version
and the asset names.

Four things mean you stop and ask. Do not build, and do not drop the app
quietly:

- the app is on the Mac App Store only
- the app is paid only, with no public trial dmg
- the app is on TestFlight or in beta only
- the vendor ships source only, with no prebuilt binary

## 3. Confirm the code signature

This repo accepts an app only when it carries a Developer ID signature that you
can check. Download the artifact once and confirm the signature is intact before
you write anything:

```
codesign --verify --strict --deep -vvv "<App>.app"      # or the .pkg
codesign -dvvv --requirements - "<App>.app" 2>&1        # capture designated requirement + Team ID
spctl -a -vvv "<App>.app"                                # Gatekeeper assessment
```

Take two things from the output: the designated requirement string, and the Team
ID from `subject.OU`. You pin both in the recipe. For a `.pkg`, run
`pkgutil --check-signature "<App>.pkg"` instead.

Stop if the app is unsigned, if it is ad-hoc signed, or if it fails strict
verification. Write no recipe, and never fall back to a weaker check. Report the
reason and let the user decide. This is not a question you can answer with yes.
An unsigned binary is outside what this skill does.

## 4. Write the recipes

Recipes here are AutoPkg YAML, in files named `.recipe.yaml`. That format needs
`MinimumVersion: "2.3"` or higher. Model each new recipe on a recipe in this repo
that ships the same way. A download recipe starts like this:

```yaml
Description: Downloads the latest version of AppName.
Identifier: com.github.homebysix.download.AppName
MinimumVersion: "2.3"

Input:
  NAME: AppName

Process:
  - Processor: URLDownloader
    Arguments:
      url: https://example.com/AppName.dmg
      filename: "%NAME%.dmg"

  - Processor: EndOfCheckPhase

  - Processor: CodeSignatureVerifier
    Arguments:
      input_path: "%pathname%/AppName.app"
      strict_verification: true
      requirement: >-
        anchor apple generic and identifier "com.example.AppName" and
        (certificate leaf[field.1.2.840.113635.100.6.1.9] exists or
        certificate 1[field.1.2.840.113635.100.6.2.6] exists and
        certificate leaf[field.1.2.840.113635.100.6.1.13] exists and
        certificate leaf[subject.OU] = "7D2YX5DQ6M")
```

The `requirement` is the designated requirement string you captured at step 3. It
is the strictest form, so use it rather than `expected_authority_names`. Always
set `strict_verification: true`. Quote a `subject.OU` value, even one that starts
with a digit. Keep the whole requirement in a YAML block scalar, `>-`, so it
stays one logical line.

Some downloads sit behind a page or an API. You can tell because a HEAD request
returns HTML or a 4xx status, or because JavaScript starts the download. Chain
`URLTextSearcher` steps to pull out the real URL, then feed it to `URLDownloader`
with `result_output_var_name: url`:

```yaml
  - Processor: URLTextSearcher
    Arguments:
      url: https://example.com/download
      re_pattern: 'href="(?P<url>https://[^"]+\.dmg)"'
      result_output_var_name: url
```

Write a custom processor for a structured API with tracks, locales or channels.
Name it `<Vendor><Purpose>InfoProvider.py` and subclass `autopkglib.URLGetter`.
That keeps the same regular expression out of several recipes. For one URL behind
an API, `URLTextSearcher` is enough.

## 5. Conventions

- name the directory after the app, or after the developer when a directory for
  them exists
- use no spaces in a filename, even when `Input/NAME` has one. The app "Tight
  Studio" gets `TightStudio.pkg.recipe.yaml`
- write the identifier as `com.github.homebysix.<type>.<App>`, with no spaces
- match `MinimumVersion`, `Input/NAME`, `ParentRecipe` and the processor order to
  the recipes next to it
- set `MinimumVersion` to the highest AutoPkg version the whole recipe chain
  needs, and never below `"2.3"` for YAML. The pre-commit hooks catch a mismatch
- give every download recipe a `CodeSignatureVerifier` step, with
  `strict_verification: true` and a `requirement` string from steps 3 and 4. This
  is required, not optional
- order a zip with no appcast as `URLDownloader`, `EndOfCheckPhase`,
  `Unarchiver`, `CodeSignatureVerifier`, `Versioner`
- a Sparkle appcast can enclose a zip rather than a dmg, which also needs
  `Unarchiver` between `EndOfCheckPhase` and `CodeSignatureVerifier`. Read the
  type of the enclosure URL in the appcast before you assume a dmg
- set both `unattended_install` and `unattended_uninstall` to `true` in a munki
  `pkginfo`
- write the munki `description` as one plain sentence of fact. No marketing
  copy, no emoji, and never leave it empty. Check it against the app itself if
  you are unsure: mount the dmg, read `Info.plist`, or run `strings` over the
  binary
- `plutil -lint` cannot parse YAML. Run `autopkg audit <recipe>` or a YAML
  linter, then confirm the recipe loads with `autopkg info <recipe>`

Handle an app that ships one build per architecture by hand. Put `%ARCH%` in
`asset_regex`, `re_pattern` or `url`, and default `Input/ARCH` to `arm64`. Say in
the `Description` what the other values are.

Do not set the munki `supported_architectures` from `%ARCH%`. The vendor and
munki often name an architecture differently, and it stops Rosetta for no reason.
Set it only when the binary really cannot run under Rosetta.

Three things exist in other repos, so recognise them. Do not add them unless the
user asks:

- `StopProcessingIf` after `EndOfCheckPhase`, which gains little because the
  download step already skips
- a pseudo-universal pkg that merges the two architecture builds. Prefer a true
  universal build, or two recipes
- a third-party aggregator such as Homebrew or MacUpdate as the source of the
  binary or the version. Go to the vendor direct, because every extra hop is
  someone else to trust

## 6. Hard stops for security

Stop and report in both of these cases:

- the app has no code signature you can check, or an ad-hoc signature, or it
  fails strict verification at step 3. This one is not negotiable
- the download URL or the appcast uses HTTP rather than HTTPS. Explain the risk
  to the user and wait. Carry on only when they say yes

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

Say what you created, and what tested clean. Name any caveat, such as unusual
signing, a developer name that does not match, or a test you skipped.

Do not commit or push unless the user asks.

## Related

- house style for every word of prose you write: [[plain-technical-english]]
