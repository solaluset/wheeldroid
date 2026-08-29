import json
import re
import sys
from collections.abc import Iterable
from urllib.request import urlopen

import jsonc


def parse_cached_list(file) -> Iterable[tuple[str, str]]:
    for line in file.readlines():
        pkg, other = line.split("/")
        version = other.split("-")[1]
        yield normalize_name(pkg), version


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.lower())


def fetch_sdist_info(
    package: str, data: dict
) -> Iterable[tuple[str, str, str, str, str]]:
    package = normalize_name(package)

    with urlopen(f"https://pypi.org/pypi/{package}/json") as response:
        pypi_data = json.load(response)
    latest_version = pypi_data["info"]["version"]
    if latest_version not in data["versions"]:
        data["versions"].append(latest_version)

    source = data.get("source", "pypi")
    for version in data["versions"]:
        if source == "pypi":
            for file in pypi_data["releases"][version]:
                if file["packagetype"] == "sdist":
                    yield package, version, source, file["url"], ""
                    break
            else:
                raise RuntimeError(f"sdist for {package} {version} not found")
        elif source == "git":
            yield (
                package,
                version,
                source,
                data["git-url"],
                data["git-tag-format"].format(version=version),
            )
        else:
            raise ValueError(f"unknown source: {source}")


def main():
    with open("packages.json5", "r") as file:
        packages = jsonc.load(file)
    with open("cached.txt", "r") as file:
        cached = list(parse_cached_list(file))

    to_build = []
    for package, data in packages.items():
        for info in fetch_sdist_info(package, data):
            if (info[0], info[1]) not in cached:
                to_build.append(" ".join(info))

    # sort alphabetically
    packages = {
        k: v for k, v in sorted(packages.items(), key=lambda item: item[0].lower())
    }
    with open("packages.json5", "w") as file:
        jsonc.dump(packages, file, indent=2, trailing_comma=True)
        file.write("\n")
    json.dump(to_build, sys.stdout)


if __name__ == "__main__":
    main()
