#!/usr/local/autopkg/python
"""
Find the newest SnowSQL installer package in the Snowflake package repository.

The SnowSQL download page on snowflake.com sits behind a Cloudflare challenge,
so a scraper gets a 403. The package repository at
sfc-repo.snowflakecomputing.com has no such block. It serves an HTML index
per directory, with one directory per minor version, such as 1.5/, and one
package per patch inside, such as 1.5/darwin_arm64/snowsql-1.5.5-darwin_arm64.pkg.

The indexes are sorted as text, not as numbers. In the 1.2 directory the
1.2.9 package comes after 1.2.32, and a 1.10 directory would come before 1.5.
So a regular expression that takes the first or the last entry picks the
wrong file once a number reaches 10. This processor reads every entry and
compares the numbers instead.
"""

import re

from autopkglib import ProcessorError, URLGetter

__all__ = ["SnowSQLInfoProvider"]

DEFAULT_BASE_URL = "https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/"
DEFAULT_PLATFORM = "darwin_arm64"

MINOR_RE = re.compile(r'href="(\d+)\.(\d+)/index\.html"')


class SnowSQLInfoProvider(URLGetter):
    """
    Find the URL and the version of the newest SnowSQL package for a platform.
    """

    description = __doc__
    input_variables = {
        "base_url": {
            "required": False,
            "default": DEFAULT_BASE_URL,
            "description": (
                "The bootstrap directory of the Snowflake package repository. "
                f"Defaults to {DEFAULT_BASE_URL}"
            ),
        },
        "platform": {
            "required": False,
            "default": DEFAULT_PLATFORM,
            "description": (
                "The platform directory to read, which is also the suffix of "
                "the package name. Snowflake publishes darwin_arm64 and "
                f"darwin_x86_64. Defaults to {DEFAULT_PLATFORM}"
            ),
        },
    }
    output_variables = {
        "url": {"description": "The URL of the newest package for the platform."},
        "version": {"description": "The version in the name of that package."},
    }

    def minor_versions(self, base_url):
        """
        Read the bootstrap index and return its minor versions, newest first.
        """
        index = self.download(base_url + "index.html", text=True)
        found = {(int(major), int(minor)) for major, minor in MINOR_RE.findall(index)}
        return sorted(found, reverse=True)

    def newest_package(self, directory_url, platform):
        """
        Read one platform index and return (version, package name), or None.

        A 404 comes back as an HTML page with no package in it. curl exits 0
        on it, so a missing directory reads as a directory with no packages.
        """
        pattern = re.compile(
            r'href="(snowsql-(\d+)\.(\d+)\.(\d+)-' + re.escape(platform) + r'\.pkg)"'
        )
        index = self.download(directory_url + "index.html", text=True)
        found = [
            ((int(major), int(minor), int(patch)), name)
            for name, major, minor, patch in pattern.findall(index)
        ]
        if not found:
            return None
        numbers, name = max(found)
        return ".".join(str(n) for n in numbers), name

    def main(self):
        """
        Walk the minor versions from the newest and stop at the first package.
        """
        base_url = self.env.get("base_url", DEFAULT_BASE_URL).rstrip("/") + "/"
        platform = self.env.get("platform", DEFAULT_PLATFORM)

        minors = self.minor_versions(base_url)
        if not minors:
            raise ProcessorError(f"No version directories found at {base_url}")
        self.output(
            "Minor versions: " + ", ".join(f"{a}.{b}" for a, b in minors),
            verbose_level=2,
        )

        for major, minor in minors:
            directory_url = f"{base_url}{major}.{minor}/{platform}/"
            found = self.newest_package(directory_url, platform)
            if found is None:
                self.output(f"No {platform} package under {directory_url}", verbose_level=2)
                continue
            version, name = found
            self.env["version"] = version
            self.env["url"] = directory_url + name
            self.output(f"Found SnowSQL {version} at {self.env['url']}")
            return

        raise ProcessorError(f"No {platform} package found under {base_url}")


if __name__ == "__main__":
    PROCESSOR = SnowSQLInfoProvider()
    PROCESSOR.execute_shell()
