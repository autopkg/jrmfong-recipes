# jrmfong-recipes

[AutoPkg](https://github.com/autopkg/autopkg) recipes for macOS software packaging — mostly apps not covered elsewhere in the AutoPkg org.

Every recipe produces an installer `.pkg`, so the output drops straight into Jamf Pro, Munki, Intune, or any other deployment tool.

## Usage

```sh
autopkg repo-add jrmfong-recipes
autopkg run -v com.github.jrmfong.pkg.SmoozePro
```

Identifiers follow a single pattern: `com.github.jrmfong.<type>.<Name>`, e.g. `com.github.jrmfong.download.SmoozePro` and `com.github.jrmfong.pkg.SmoozePro`.

### Requirements

- **AutoPkg 2.3+** for the YAML recipes; **2.9+** for the ones that use `URLDownloaderPython` (Jamf Setup Checklist, MyDPD Customer, Smooze Pro).
- **Parent repos.** Recipes with an external parent need that repo added first:

  ```sh
  autopkg repo-add dataJAR-recipes    # Adobe Acrobat, Burp Suite, VeraCrypt
  autopkg repo-add nstrauss-recipes   # AWS Session Manager Plugin
  autopkg repo-add grahampugh-recipes # PkgInfoReader — Adobe Acrobat, AWS, VeraCrypt
  ```

  IntelliJ IDEA parents off `com.github.bnpl.autopkg.download.intellijidea`, which is not in the AutoPkg org — add that repo by URL.

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
| VeraCrypt | `pkg` | `com.github.jrmfong.pkg.Veracrypt` | `com.github.dataJAR-recipes.download.VeraCrypt` |
| Yamaha TF Editor | `download`, `pkg` | `com.github.jrmfong.pkg.YamahaTFEditor` | |

`download` recipes fetch the vendor release and verify its code signature; `pkg` recipes build the installer package from it. Each app lives in its own directory, and recipes are written in both plist (`.recipe`) and YAML (`.recipe.yaml`) format.

### Architecture overrides

Three recipes pin `DOWNLOAD_ARCH` to an **Apple silicon** build. Override the input to package for Intel:

| Recipe | `DOWNLOAD_ARCH` default |
| --- | --- |
| AWS Session Manager Plugin | `_arm64` |
| Burp Suite Professional | `MacOsArm64` |
| IntelliJ IDEA | `macM1` (Intel: `mac`) |

```sh
autopkg run -v com.github.jrmfong.pkg.IntelliJIDEA -k DOWNLOAD_ARCH=mac
```

The accepted values are defined by each parent download recipe, not here — check the parent for the Intel equivalent before overriding.

### Notes on individual recipes

- **Jamf Setup Checklist** — sourced from the [Jamf-Concepts/setup-checklist](https://github.com/Jamf-Concepts/setup-checklist) GitHub releases via `GitHubReleasesInfoProvider`.
- **Shure Designer 6** — the vendor ships a nested ZIP containing an InstallBuilder app rather than a drag-install `.app`. The `pkg` recipe wraps that installer and runs it unattended from a `postinstall` script, so the resulting package is a bootstrapper, not a payload copy.
- **Shure Update Utility** and **Yamaha TF Editor** — the vendor already ships a signed flat `.pkg`. These recipes unpack it only to read a version number, then re-copy the original vendor package.
- **Jamf Setup Checklist**, **MyDPD Customer**, **Smooze Pro** — use `URLDownloaderPython` with a browser `User-Agent`, and stop early when the download is unchanged. Set `BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED=True` to force the rest of the recipe to run against a cached download.
- **Shure Designer 6** — the filenames drop the version, but the identifiers keep the `6` suffix (`...ShureDesigner6`).

## Contributing

The repo uses [pre-commit](https://pre-commit.com) with [pre-commit-macadmin](https://github.com/homebysix/pre-commit-macadmin) to lint recipes in `--strict` mode, enforce the `com.github.jrmfong.` identifier prefix, reject overrides and trust info, and format plists:

```sh
pre-commit install
pre-commit run --all-files
```

When adding a recipe:

1. Put it in a directory named after the software.
2. Prefix the identifier with `com.github.jrmfong.` and match the existing `download` / `pkg` naming.
3. Verify the code signature in the `download` recipe — pin the Team ID and bundle identifier, not just the anchor.
4. Set `MinimumVersion` to the lowest AutoPkg release the processors actually need.
5. Add the recipe to the table above.
