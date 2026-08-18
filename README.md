# jrmfong-recipes

[AutoPkg](https://github.com/autopkg/autopkg) recipes for macOS software packaging, mostly apps not covered elsewhere in the AutoPkg org.

All recipe identifiers use the prefix `com.github.jrmfong.`.

## Usage

```sh
autopkg repo-add jrmfong-recipes
autopkg run -v com.github.jrmfong.pkg.SmoozePro
```

Recipes are written in both plist (`.recipe`) and YAML (`.recipe.yaml`) format. YAML recipes require AutoPkg 2.3 or newer; some require 2.9.

## Recipes

| Software | Recipes | Notes |
| --- | --- | --- |
| Adobe Acrobat DC Unified Application | `pkg` | Parent: `com.github.dataJAR-recipes.download.Adobe Acrobat DC Unified Application` |
| AWS Session Manager Plugin | `pkg` | Parent: `com.github.nstrauss.download.AWSSessionManagerPlugin` |
| CueTimer | `download`, `pkg` | |
| Ekahau Capture | `download`, `pkg` | |
| IntelliJ IDEA (JetBrains) | `pkg` | Parent: `com.github.bnpl.autopkg.download.intellijidea` |
| Jamf Setup Checklist | `download`, `pkg` | |
| MyDPD Customer | `download`, `pkg` | |
| Shure Designer | `download`, `pkg` | |
| Shure Update Utility | `download`, `pkg` | |
| Smooze Pro | `download`, `pkg` | |
| Yamaha TF Editor | `download`, `pkg` | |

`download` recipes fetch and code-signature-verify the vendor release; `pkg` recipes build an installer package from it. Recipes with an external parent depend on that repo being added first (`autopkg repo-add <repo>`).
