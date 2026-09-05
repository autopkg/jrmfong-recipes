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

- AutoPkg 2.3 or later. Every recipe is YAML, which needs 2.3 as a minimum. AutoPkg 2.9 or later for the ones that use `URLDownloaderPython`: CueTimer, Ekahau Capture, Jamf Setup Checklist, MyDPD Customer, Smooze Pro and snowSQL.
- Parent repos. Recipes with an external parent need that repo added first:

  ```sh
  autopkg repo-add dataJAR-recipes    # Adobe Acrobat, Burp Suite, VeraCrypt
  autopkg repo-add nstrauss-recipes   # AWS Session Manager Plugin
  autopkg repo-add grahampugh-recipes # PkgInfoReader - Adobe Acrobat, AWS, VeraCrypt, snowSQL, Yamaha TF Editor
  ```

  IntelliJ IDEA parents off `com.github.bnpl.autopkg.download.intellijidea`, which is not in the AutoPkg org. Add that repo by URL.

## Recipes

| Software | Recipes | `pkg` identifier | Parent (external) |
| --- | --- | --- | --- |
| Adobe Acrobat DC Unified Application | `pkg` | `com.github.jrmfong.pkg.AdobeAcrobatDCUnifiedApplication` | `com.github.dataJAR-recipes.download.Adobe Acrobat DC Unified Application` |
| AWS Session Manager Plugin | `pkg` | `com.github.jrmfong.pkg.AWSSessionManagerPlugin` | `com.github.nstrauss.download.AWSSessionManagerPlugin` |
| Burp Suite Professional | `pkg` | `com.github.jrmfong.pkg.BurpSuite` | `com.github.dataJAR-recipes.download.Burp Suite Professional` |
| CueTimer | `download`, `pkg` | `com.github.jrmfong.pkg.CueTimer` | |
| Eclipse Temurin JDK 25 | `download`, `pkg` | `com.github.jrmfong.pkg.EclipseTemurinJDK25` | |
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

A `download` recipe fetches the vendor release and checks its code signature. A `pkg` recipe builds the installer package from that download. Each app lives in its own directory. Every recipe uses YAML (`.recipe.yaml`).

### Architecture overrides

4 recipes default to an Apple silicon build. Override the input to package for Intel:

| Recipe | Input | Default | Intel value |
| --- | --- | --- | --- |
| AWS Session Manager Plugin | `DOWNLOAD_ARCH` | `_arm64` | see parent |
| Burp Suite Professional | `DOWNLOAD_ARCH` | `MacOsArm64` | see parent |
| Eclipse Temurin JDK 25 | `ARCH` | `aarch64` | `x64` |
| IntelliJ IDEA | `DOWNLOAD_ARCH` | `macM1` | `mac` |

```sh
autopkg run -v com.github.jrmfong.pkg.IntelliJIDEA -k DOWNLOAD_ARCH=mac
```

The parent download recipe defines the accepted `DOWNLOAD_ARCH` values, not this repo. Check the parent for the Intel equivalent before you override. Eclipse Temurin JDK 25 is defined here, and takes `aarch64` or `x64`.

snowSQL is Apple silicon only. Its download recipe matches the `darwin_arm64` package in the vendor page, so there is no input to switch it to Intel.

### Notes on individual recipes

- Jamf Setup Checklist comes from the [Jamf-Concepts/setup-checklist](https://github.com/Jamf-Concepts/setup-checklist) GitHub releases, read by `GitHubReleasesInfoProvider`.
- Shure Designer 6 ships as a nested ZIP holding an InstallBuilder app, not a drag-install `.app`. The `pkg` recipe wraps that installer and runs it unattended from a `postinstall` script. The package is a bootstrapper, not a copy of the payload.
- Shure Designer 6 file names drop the version, but the identifiers keep the `6` suffix (`...ShureDesigner6`).
- Shure Update Utility, Yamaha TF Editor and snowSQL already ship a signed flat `.pkg`. These recipes read a version number, then re-copy the vendor package under a versioned name.
- snowSQL and Yamaha TF Editor read that version with `PkgInfoReader`. Shure Update Utility cannot: its package declares `version="0"`, so the recipe unpacks the payload and reads the version from the app instead.
- CueTimer, Ekahau Capture, Jamf Setup Checklist, MyDPD Customer, Smooze Pro and snowSQL use `URLDownloaderPython` with a browser `User-Agent`.
- Every `download` recipe stops early when the vendor file is unchanged. The matching `pkg` recipe then builds nothing, because the chain stops first. Set `BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED=True` to run the rest against the cached download.

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
