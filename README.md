# jrmfong-recipes

[AutoPkg](https://github.com/autopkg/autopkg) recipes for macOS software packaging, mostly apps that no other repo in the AutoPkg org covers.

Every recipe produces an installer `.pkg`, so the output goes straight into Jamf Pro, Munki, Intune or any other deployment tool.

## Usage

```sh
autopkg repo-add jrmfong-recipes
autopkg run -v com.github.jrmfong.pkg.SmoozePro
```

Identifiers follow a single pattern: `com.github.jrmfong.<type>.<Name>`, e.g. `com.github.jrmfong.download.SmoozePro` and `com.github.jrmfong.pkg.SmoozePro`.

### Requirements

- AutoPkg 2.3 or later for the YAML recipes. AutoPkg 2.9 or later for the ones that use `URLDownloaderPython`: Jamf Setup Checklist, MyDPD Customer, Smooze Pro and snowSQL.
- Parent repos. Recipes with an external parent need that repo added first:

  ```sh
  autopkg repo-add dataJAR-recipes    # Adobe Acrobat, Burp Suite, VeraCrypt
  autopkg repo-add nstrauss-recipes   # AWS Session Manager Plugin
  autopkg repo-add grahampugh-recipes # PkgInfoReader - Adobe Acrobat, AWS, VeraCrypt, snowSQL
  ```

  IntelliJ IDEA parents off `com.github.bnpl.autopkg.download.intellijidea`, which is not in the AutoPkg org. Add that repo by URL.

## Recipes

| Software | Recipes | `pkg` identifier | Parent (external) |
| --- | --- | --- | --- |
| Adobe Acrobat DC Unified Application | `pkg` | `com.github.jrmfong.pkg.AdobeAcrobatDCUnifiedApplication` | `com.github.dataJAR-recipes.download.Adobe Acrobat DC Unified Application` |
| AWS Session Manager Plugin | `pkg` | `com.github.jrmfong.pkg.AWSSessionManagerPlugin` | `com.github.nstrauss.download.AWSSessionManagerPlugin` |
| Burp Suite Professional | `pkg` | `com.github.jrmfong.pkg.BurpSuite` | `com.github.dataJAR-recipes.download.Burp Suite Professional` |
| CueTimer | `download`, `pkg` | `com.github.jrmfong.pkg.CueTimer` | |
| Ekahau Capture | `download`, `pkg` | `com.github.jrmfong.pkg.EkahauCapture` | |
| IntelliJ IDEA | `pkg` | `com.github.jrmfong.pkg.IntelliJIDEA` | `com.github.bnpl.autopkg.download.intellijidea` |
| Jamf Setup Checklist | `download`, `pkg` | `com.github.jrmfong.pkg.JamfSetupChecklist` | |
| MyDPD Customer | `download`, `pkg` | `com.github.jrmfong.pkg.MyDPDCustomer` | |
| Shure Designer 6 | `download`, `pkg` | `com.github.jrmfong.pkg.ShureDesigner6` | |
| Shure Update Utility | `download`, `pkg` | `com.github.jrmfong.pkg.ShureUpdateUtility` | |
| Smooze Pro | `download`, `pkg` | `com.github.jrmfong.pkg.SmoozePro` | |
| snowSQL | `download`, `pkg` | `com.github.jrmfong.pkg.snowSQL` | |
| VeraCrypt | `pkg` | `com.github.jrmfong.pkg.Veracrypt` | `com.github.dataJAR-recipes.download.VeraCrypt` |
| Yamaha TF Editor | `download`, `pkg` | `com.github.jrmfong.pkg.YamahaTFEditor` | |

A `download` recipe fetches the vendor release and checks its code signature. A `pkg` recipe builds the installer package from that download. Each app lives in its own directory. Older recipes use the plist format (`.recipe`) and newer ones use YAML (`.recipe.yaml`).

### Architecture overrides

Three recipes pin `DOWNLOAD_ARCH` to an Apple silicon build. Override the input to package for Intel:

| Recipe | `DOWNLOAD_ARCH` default |
| --- | --- |
| AWS Session Manager Plugin | `_arm64` |
| Burp Suite Professional | `MacOsArm64` |
| IntelliJ IDEA | `macM1` (Intel: `mac`) |

```sh
autopkg run -v com.github.jrmfong.pkg.IntelliJIDEA -k DOWNLOAD_ARCH=mac
```

Each parent download recipe defines the accepted values, not this repo. Check the parent for the Intel equivalent before you override.

snowSQL is Apple silicon only. Its download recipe matches the `darwin_arm64` package in the vendor page, so there is no input to switch it to Intel.

### Notes on individual recipes

- Jamf Setup Checklist comes from the [Jamf-Concepts/setup-checklist](https://github.com/Jamf-Concepts/setup-checklist) GitHub releases, read by `GitHubReleasesInfoProvider`.
- Shure Designer 6 ships as a nested ZIP holding an InstallBuilder app, not a drag-install `.app`. The `pkg` recipe wraps that installer and runs it unattended from a `postinstall` script. The package is a bootstrapper, not a copy of the payload.
- Shure Designer 6 file names drop the version, but the identifiers keep the `6` suffix (`...ShureDesigner6`).
- Shure Update Utility and Yamaha TF Editor already ship a signed flat `.pkg`. These recipes unpack it only to read a version number, then re-copy the vendor package.
- snowSQL also ships a signed flat `.pkg`. Its recipe reads the version with `PkgInfoReader`, then copies the vendor package under a versioned name.
- Jamf Setup Checklist, MyDPD Customer, Smooze Pro and snowSQL use `URLDownloaderPython` with a browser `User-Agent`, and stop early when the download is unchanged. Set `BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED=True` to run the rest of the recipe against a cached download.

## Contributing

The repo uses [pre-commit](https://pre-commit.com) with [pre-commit-macadmin](https://github.com/homebysix/pre-commit-macadmin) to lint recipes in `--strict` mode, enforce the `com.github.jrmfong.` identifier prefix, reject overrides and trust info, and format plists:

```sh
pre-commit install
pre-commit run --all-files
```

When adding a recipe:

1. Put it in a directory named after the software.
2. Prefix the identifier with `com.github.jrmfong.` and match the existing `download` / `pkg` naming.
3. Check the code signature in the `download` recipe. Pin the Team ID and bundle identifier, not just the anchor.
4. Set `MinimumVersion` to the lowest AutoPkg release the processors actually need.
5. Add the recipe to the table above.
