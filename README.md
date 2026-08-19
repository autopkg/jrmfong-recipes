# jrmfong-recipes

[AutoPkg](https://github.com/autopkg/autopkg) recipes for macOS software packaging, mostly apps not covered elsewhere in the AutoPkg org.

All recipe identifiers start with `com.github.jrmfong.`, though a few use a longer prefix (`com.github.jrmfong.recipes.`, `com.github.jrmfong.autopkg.`) — see the identifiers in the table below.

## Usage

```sh
autopkg repo-add jrmfong-recipes
autopkg run -v com.github.jrmfong.pkg.SmoozePro
```

Recipes are written in both plist (`.recipe`) and YAML (`.recipe.yaml`) format. All YAML recipes require AutoPkg 2.3 or newer; the ones that use YAML-only features require 2.9.

## Recipes

| Software | Recipes | `pkg` identifier | Parent (external) |
| --- | --- | --- | --- |
| Adobe Acrobat DC Unified Application | `pkg` | `com.github.jrmfong.recipes.pkg.AdobeAcrobatDCUnifiedApplication` | `com.github.dataJAR-recipes.download.Adobe Acrobat DC Unified Application` |
| AWS Session Manager Plugin | `pkg` | `com.github.jrmfong.recipes.pkg.AWSSessionManagerPlugin` | `com.github.nstrauss.download.AWSSessionManagerPlugin` |
| Burp Suite Professional | `pkg` | `com.github.jrmfong.pkg.BurpSuite` | `com.github.dataJAR-recipes.download.Burp Suite Professional` |
| CueTimer | `download`, `pkg` | `com.github.jrmfong.pkg.CueTimer` | |
| Ekahau Capture | `download`, `pkg` | `com.github.jrmfong.pkg.EkahauCapture` | |
| IntelliJ IDEA (JetBrains) | `pkg` | `com.github.jrmfong.autopkg.pkg.IntelliJIDEA` | `com.github.bnpl.autopkg.download.intellijidea` |
| Jamf Setup Checklist | `download`, `pkg` | `com.github.jrmfong.pkg.JamfSetupChecklist` | |
| MyDPD Customer | `download`, `pkg` | `com.github.jrmfong.pkg.MyDPDCustomer` | |
| Shure Designer | `download`, `pkg` | `com.github.jrmfong.pkg.ShureDesigner6` | |
| Shure Update Utility | `download`, `pkg` | `com.github.jrmfong.pkg.ShureUpdateUtility` | |
| Smooze Pro | `download`, `pkg` | `com.github.jrmfong.pkg.SmoozePro` | |
| Yamaha TF Editor | `download`, `pkg` | `com.github.jrmfong.pkg.YamahaTFEditor` | |

`download` recipes fetch and code-signature-verify the vendor release; `pkg` recipes build an installer package from it. Recipes with an external parent depend on that repo being added first (`autopkg repo-add <repo>`).

Notes on individual recipes:

- **Shure Designer** — recipe filenames drop the version, but the identifiers are still suffixed `ShureDesigner6`.
- **Burp Suite Professional** — defaults to `DOWNLOAD_ARCH: MacOsArm64` (Apple silicon). Override that input for Intel.
- **Jamf Setup Checklist** — sourced from GitHub releases via `GitHubReleasesInfoProvider`.

## Contributing

The repo uses [pre-commit](https://pre-commit.com) with [pre-commit-macadmin](https://github.com/homebysix/pre-commit-macadmin) to lint recipes (`--strict`), enforce the `com.github.jrmfong.` prefix, reject overrides and trust info, and format plists:

```sh
pre-commit install
pre-commit run --all-files
```
