import json
import sys
from collections.abc import Iterable
from urllib.request import urlopen


def parse_cached_list(file) -> Iterable[tuple[str, str]]:
    for line in file.readlines():
        pkg, other = line.split("/")
        version = other.split("-")[1]
        yield pkg, version


def fetch_sdist_urls(
    package: str, versions: list[str]
) -> Iterable[tuple[tuple[str, str], str]]:
    with urlopen(f"https://pypi.org/pypi/{package}/json") as response:
        data = json.load(response)
    latest_version = data["info"]["version"]
    if latest_version not in versions:
        versions.append(latest_version)

    for version in versions:
        for file in data["releases"][version]:
            if file["packagetype"] == "sdist":
                yield (package, version), file["url"]
                break
        else:
            raise RuntimeError(f"sdist for {package} {version} not found")


def main():
    with open("packages.json", "r") as file:
        packages = json.load(file)
    with open("cached.txt", "r") as file:
        cached = list(parse_cached_list(file))

    urls = []
    for package, versions in packages.items():
        for info, url in fetch_sdist_urls(package, versions):
            if info not in cached:
                urls.append(url)

    with open("packages.json", "w") as file:
        json.dump(packages, file, indent=2)
    json.dump(urls, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
