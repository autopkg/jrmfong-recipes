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

- AutoPkg 3.0 or above, which is what this repo recommends. On 3.0 both downloaders keep a `.info.json` sidecar beside each download and skip an unchanged file, and the download check in [Running in CI](#running-in-ci) runs on 3.0, so a local run behaves the same way. The hard minimums are lower: 2.3 for the YAML format, and 2.9 for the recipes that use `URLDownloaderPython`: CueTimer, Ekahau Capture, fuse-t, Jamf Setup Checklist, MyDPD Customer, Smooze Pro, SnowSQL and the VeraCrypt FUSE-T build.
- Parent repos. Recipes with an external parent need that repo added first:

  ```sh
  autopkg repo-add dataJAR-recipes    # Adobe Acrobat, Burp Suite, iODBC SDK, VeraCrypt
  autopkg repo-add nstrauss-recipes   # AWS Session Manager Plugin
  autopkg repo-add patgmac-recipes    # Netskope Client
  autopkg repo-add grahampugh-recipes # PkgInfoReader - Adobe Acrobat, AWS, Netskope, VeraCrypt, SnowSQL, Yamaha TF Editor
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
| fuse-t | `download`, `pkg` | `com.github.jrmfong.pkg.FuseT` | |
| Google Web Designer | `pkg` | `com.github.jrmfong.pkg.GoogleWebDesigner` | `com.github.peshay.download.GoogleWebDesigner` |
| iODBC SDK | `pkg` | `com.github.jrmfong.pkg.iODBCSDK` | `com.github.dataJAR-recipes.download.iODBC SDK` |
| IntelliJ IDEA | `pkg` | `com.github.jrmfong.pkg.IntelliJIDEA` | `com.github.bnpl.autopkg.download.intellijidea` |
| Jamf Setup Checklist | `download`, `pkg` | `com.github.jrmfong.pkg.JamfSetupChecklist` | |
| LastPass for Desktop | `download`, `pkg` | `com.github.jrmfong.pkg.LastPassForDesktop` | |
| MyDPD Customer | `download`, `pkg` | `com.github.jrmfong.pkg.MyDPDCustomer` | |
| RustRover | `pkg` | `com.github.jrmfong.pkg.RustRover` | `com.github.bnpl.autopkg.download.rustrover` |
| Netskope Client | `pkg` | `com.github.jrmfong.pkg.Netskope` | `com.github.patgmac.download.Netskope` |
| PaperCut Hive | `download`, `pkg` | `com.github.jrmfong.pkg.PaperCutHive` | |
| Printix Client | `download`, `pkg` | `com.github.jrmfong.pkg.PrintixClient` | |
| Shure Designer 6 | `download`, `pkg` | `com.github.jrmfong.pkg.ShureDesigner6` | |
| Shure Update Utility | `download`, `pkg` | `com.github.jrmfong.pkg.ShureUpdateUtility` | |
| Smooze Pro | `download`, `pkg` | `com.github.jrmfong.pkg.SmoozePro` | |
| SnowSQL | `download`, `pkg` | `com.github.jrmfong.pkg.SnowSQL` | |
| VeraCrypt | `pkg` | `com.github.jrmfong.pkg.Veracrypt` | `com.github.dataJAR-recipes.download.VeraCrypt` |
| VeraCrypt (FUSE-T build) | `download`, `pkg` | `com.github.jrmfong.pkg.VeraCryptFuseT` | |
| Yamaha TF Editor | `download`, `pkg` | `com.github.jrmfong.pkg.YamahaTFEditor` | |

A `download` recipe fetches the vendor release and checks its code signature. A `pkg` recipe builds the installer package from that download. Each app lives in its own directory. Every recipe uses YAML (`.recipe.yaml`).

### Architecture overrides

5 recipes default to an Apple silicon build. Override the input to package for Intel:

| Recipe | Input | Default | Intel value |
| --- | --- | --- | --- |
| AWS Session Manager Plugin | `DOWNLOAD_ARCH` | `_arm64` | see parent |
| Burp Suite Professional | `DOWNLOAD_ARCH` | `MacOsArm64` | see parent |
| Eclipse Temurin JDK 25 | `ARCH` | `aarch64` | `x64` |
| IntelliJ IDEA | `DOWNLOAD_ARCH` | `macM1` | `mac` |
| RustRover | `ARCH_TYPE` | `macM1` | `mac` |

```sh
autopkg run -v com.github.jrmfong.pkg.IntelliJIDEA -k DOWNLOAD_ARCH=mac
```

The parent download recipe defines the accepted `DOWNLOAD_ARCH` and `ARCH_TYPE` values, not this repo. Check the parent for the Intel equivalent before you override. Eclipse Temurin JDK 25 is defined here, and takes `aarch64` or `x64`.

SnowSQL is Apple silicon only. Its download recipe matches the `darwin_arm64` package in the vendor page, so there is no input to switch it to Intel.

### Notes on individual recipes

- Jamf Setup Checklist comes from the [Jamf-Concepts/setup-checklist](https://github.com/Jamf-Concepts/setup-checklist) GitHub releases, read by `GitHubReleasesInfoProvider`.
- Google Web Designer ships its app directory as mode 750 and its CodeResources file as 640. A package installs it as root:admin, so a standard user cannot open it and Finder reports it as damaged. The `pkg` recipe sets every entry under Applications to 0755 through PkgCreator's `chown`, which the code signature does not cover.
- fuse-t comes from the [macos-fuse-t/fuse-t](https://github.com/macos-fuse-t/fuse-t) GitHub releases. Each release holds one universal package, and the version comes from the release tag rather than the package, because the vendor ships a distribution package with no product version of its own.
- VeraCrypt ships 2 macOS builds per release. `Veracrypt.pkg` takes the macFUSE one through the dataJAR parent. `VeracryptFuseT.pkg` takes `VeraCrypt_FUSE-T_<version>.dmg` through a download recipe of its own, because the parent's `asset_regex` requires a digit straight after `VeraCrypt_` and an override cannot change a `Process` argument.
- The VeraCrypt FUSE-T build needs fuse-t installed first. Its installer checks for `/usr/local/lib/libfuse-t.dylib` and refuses to run without it, so deploy `com.github.jrmfong.pkg.FuseT` ahead of it. It also needs macOS 12 or later.
- Both VeraCrypt builds carry the package identifier `com.idrix.pkg.veracrypt` and the same version, so install only one of the 2 on a Mac. The built file names differ, because `Input/NAME` does.
- LastPass for Desktop writes its version with a dash, such as `2.2.0-2`, and the package name keeps it: `LastPass for Desktop-2.2.0-2.pkg`. A tool that reads the version after the last dash of a file name reads `2`, so rename the package first.
- Netskope Client downloads from your own tenant, at `https://<HOSTNAME>/dlr/mac/get`. The parent's default `HOSTNAME`, `download-company.goskope.com`, is a placeholder, so set `HOSTNAME` in an override before you run the recipe.
- PaperCut Hive comes from the 2 public update feeds that an installed edge node and print client poll, not from PaperCut's bulk installer, which the Hive admin console only offers behind a signed link. The feeds carry the same signed binaries, but the edge node feed can trail the bulk installer by a few weeks. An installed edge node updates itself from the feed every 12 hours.
- The PaperCut Hive package stages the bulk installer's layout in `/Library/Application Support/PaperCut Hive Installer`, with an `install.sh` that takes the same 3 arguments: the system key, the region and the org ID. The package has no postinstall and installs nothing, because the system key is private to the organisation and does not belong in a package. Run `install.sh` from a policy script after the package, passing the 3 values as policy parameters. `install.sh` needs a logged-in user, because the print client installs into that user's Library.
- PaperCut writes versions such as `2026-08-21-0157`. The PaperCut Hive recipe sets `version` to the dotted form, `2026.08.21.0157`, and keeps PaperCut's own in `edgenode_version` and `client_version`.
- Printix Client downloads from your own tenant. Set `PRINTIX_TENANT_ID`, the tenant UUID in the admin console's download link, and `PRINTIX_TENANT_DOMAIN`, such as `acme.printix.net`, in an override. Both are empty here so that no tenant ends up in this repo.
- The Printix Client reads its tenant from the name of the installer that ran it, `CLIENT_{<tenant domain>}_{<tenant id>}.pkg`, so a renamed package signs in to no tenant in particular. The `pkg` recipe carries the vendor package, signed and unchanged, in its scripts under that name, and its postinstall runs it with `installer`. The package can then take any name.
- The Printix tenant's software listing can report an older version than the file its download link serves, so the `pkg` recipe reads the version from the app.
- Shure Designer 6 ships as a nested ZIP holding an InstallBuilder app, not a drag-install `.app`. The `pkg` recipe wraps that installer and runs it unattended from a `postinstall` script. The package is a bootstrapper, not a copy of the payload.
- Shure Designer 6 file names drop the version, but the identifiers keep the `6` suffix (`...ShureDesigner6`).
- Shure Update Utility, Yamaha TF Editor and SnowSQL already ship a signed flat `.pkg`. These recipes read a version number, then re-copy the vendor package under a versioned name.
- SnowSQL and Yamaha TF Editor read that version with `PkgInfoReader`. Shure Update Utility cannot: its package declares `version="0"`, so the recipe unpacks the payload and reads the version from the app instead.
- CueTimer, Ekahau Capture, Jamf Setup Checklist, MyDPD Customer, Smooze Pro and SnowSQL use `URLDownloaderPython` with a browser `User-Agent`. fuse-t uses the same downloader without one, because GitHub needs no such header.

## Running in CI

Every recipe here is written so a CI job can restore a cached download and skip
the work that follows. Three things matter: where the marker sits, what the job
caches, and what the recipes deliberately leave out. A GitHub Actions workflow
in this repo uses that to check every download recipe twice a week. See
[the download check on GitHub Actions](#the-download-check-on-github-actions).

### The check phase stops at the download

`autopkg --check` keeps every step up to the last `EndOfCheckPhase` in the merged
parent chain, then deletes the rest. Every recipe here puts that marker straight
after its download processor, so the check phase does nothing but fetch. The
steps that mount a dmg, unzip an archive or check a signature all sit below it.

This matters because a runner restores the download metadata, not the file. It
leaves an empty placeholder where the skipped download would be. A step above the
marker then reads a file with no contents, and mounting an empty placeholder
gives:

```
hdiutil: attach failed - image not recognized
```

The recipe fails on the runs where the cache works, which reads as a broken
recipe rather than a caching problem. `scripts/lint_check_phase.py` checks the
whole merged chain, external parents included, and the pre-commit hook runs it on
every commit.

Check a chain by hand:

```sh
autopkg run --check -v com.github.jrmfong.pkg.MyDPDCustomer
```

The output must stop at `EndOfCheckPhase`. No mount, no unarchive and no
signature check may appear before it.

### What the job has to cache

On AutoPkg 3.0, `URLDownloader` and `URLDownloaderPython` record a download
the same way: a `.info.json` sidecar beside the file, holding the server's
`ETag`, `Last-Modified` and `Content-Length`. Both compare the next response
against that sidecar, and both take `DOWNLOAD_MISSING_FILE`, which decides
whether a file that has gone missing while the server is unchanged gets
fetched again.

Cache `AutoPkg/Cache/*/downloads/*.info.json` along with the metadata cache.
Without the sidecars, every recipe fetches its file again on every run.

Two details still matter to a runner that keeps no files. The downloader
sends the conditional headers only when a file sits beside the sidecar, and it
compares the server's `Content-Length` with the size of that file rather than
with the sidecar. So the runner has to put back a sparse placeholder of the
recorded size, which is what the workflow does. A placeholder of any other
size reads as a changed download.

### No recipe stops itself early

No `download` recipe here carries a `StopProcessingIf` guard, and none declares
`BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED`. Nothing has to be bypassed to
make a full run package anything.

The guard used to sit after `EndOfCheckPhase` in every download recipe. It was
removed because it saved nothing that the check phase, the downloader's ETag
match and `PkgCreator` do not already save, and because a 2-phase runner turns it
into a silent failure. The check phase downloads the file, the runner sees a new
download and starts the full run, and the full run then finds that same file in
the cache. `download_changed` is `False`, the chain stops before it builds
anything, and the job still reports success.

An override that still sets `BYPASS_STOP_PROCESSING_IF_DOWNLOAD_UNCHANGED` keeps
working. The key is simply unused now, so you can drop it at your leisure.

### The download check on GitHub Actions

`.github/workflows/weekly-download-check.yml` runs the check phase of every
recipe in `scripts/check_downloads.txt` on a Linux runner, on Monday and
Thursday at 7am UTC. The list holds the 14 download recipes and the 5 `pkg`
recipes with a parent in another repo. Netskope and Printix Client are left
out, because each needs a tenant of your own.

The runner keeps only the `.info.json` sidecars between runs, and puts a
sparse placeholder of the recorded size beside each one before the run. That
makes AutoPkg send the stored ETag, so an unchanged file is never fetched
again. AutoPkg 3.0.0 compares the server's Content-Length with the file on
disk, so a placeholder of any other size reads as changed. The whole run takes
about a minute. A new vendor release downloads once, so its sidecar updates.

A broken recipe does 3 things:

- fails the job, so GitHub emails whoever last committed the workflow
- appears in the job summary at the top of the run page, with its error
- gets an issue titled `Download recipe broken: <identifier>`, holding the
  error and a link to the run. A later failure adds a comment to that issue,
  and it closes itself on the first run where the recipe passes

Run the workflow by hand from the Actions tab with Run workflow, or with
`gh workflow run weekly-download-check.yml`. Both need the file on `main`.
A pull request that changes the workflow, anything in `scripts/`, or a recipe
runs the check as well, from the pull request's own copy of the file, so a
change is tested before it merges. The issue logic lives in
`scripts/flag_broken_recipes.py`, and
`python3 scripts/test_flag_broken_recipes.py` tests it without touching
GitHub.

### Troubleshoot a broken recipe locally

1. Run the same check on your Mac. `scripts/check_downloads.sh` runs the whole
   list, and `scripts/check_downloads.sh com.github.jrmfong.download.SnowSQL`
   runs one recipe. The script passes the recipe files in this working copy to
   `autopkg run --check -v`, so an uncommitted fix is what gets tested. A
   parent from another repo still comes from your cloned repos.
2. Read the error. The table below covers the common ones.
3. Add `-vv` to the `autopkg run --check` command for the HTTP headers and the
   text the regex ran against.
4. After the fix, run the full chain with `autopkg run -vv` on the download
   and the `pkg` recipe files. The check phase stops at the download, so it
   never sees the signature check or the package build.
5. Commit the fix. The next scheduled run closes the issue, or run the
   workflow by hand.

| Error | Likely cause | Where to look |
| --- | --- | --- |
| `HTTP Error 404: Not Found` | the vendor moved the file | `DOWNLOAD_URL`, or the `url` argument of the downloader |
| `No match found on URL` | the download page changed, so `re_pattern` no longer matches | `curl -sL <page>` and test the pattern against it |
| `No releases found` or `No release assets were found` | the asset name or the tag format changed, or the latest release is a pre-release | `gh release list -R <owner>/<repo>` and `gh release view --json assets` |
| `API rate limit exceeded` | anonymous GitHub API calls, 60 an hour | set the `GITHUB_TOKEN` preference |
| `CERTIFICATE_VERIFY_FAILED` | a proxy or TLS inspection on your network | `SSL_CERT_FILE`, or run the check from another network |

A recipe can pass on your Mac and fail on the runner. The runner uses AutoPkg
3.0.0 on Linux, where only the check phase works, and it has no overrides. So
a `pkg` recipe whose parent needs an override, such as Netskope, cannot run
there, and a step that opens the download before `EndOfCheckPhase` fails on
Linux as well as on the Mac.

### Known limits

- Eclipse Temurin JDK 25 and Jamf Setup Checklist read the GitHub releases API, as does the VeraCrypt parent. Give the job a token, through the `GITHUB_TOKEN` preference or the file at `GITHUB_TOKEN_PATH`, or it meets the anonymous rate limit.
- The Yamaha TF Editor download returns no `ETag` and no `Last-Modified`, so `URLDownloader` falls back to matching on file size. That does not prove the build is unchanged.

## Contributing

The repo uses [pre-commit](https://pre-commit.com) with [pre-commit-macadmin](https://github.com/homebysix/pre-commit-macadmin) to lint recipes in `--strict` mode, enforce the `com.github.jrmfong.` identifier prefix, reject overrides and trust info, and format plists:

```sh
pre-commit install
pre-commit run --all-files
```

A local hook, `scripts/lint_check_phase.py`, also checks that no recipe opens its download before `EndOfCheckPhase`, for the reason given in [Running in CI](#running-in-ci). Run it by hand with `python3 scripts/lint_check_phase.py`, which needs PyYAML.

When adding a recipe:

1. Put it in a directory named after the software.
2. Prefix the identifier with `com.github.jrmfong.` and match the existing `download` / `pkg` naming.
3. Check the code signature in the `download` recipe. Pin the Team ID and bundle identifier, not just the anchor.
4. Set `MinimumVersion` to the lowest AutoPkg release the processors actually need.
5. Put `EndOfCheckPhase` straight after the download processor, and every step that mounts or unpacks the download after it.
6. Add no `StopProcessingIf` guard. See [Running in CI](#running-in-ci) for why.
7. Add the recipe to the table above.
8. Add the identifier to `scripts/check_downloads.txt`, so the download check
   covers it. Add a `pkg` recipe there only when its parent lives in another
   repo, because that chain has no download recipe here.
