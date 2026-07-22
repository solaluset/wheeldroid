import sys
import json
from urllib.request import urlopen
from packaging.version import Version
from packaging.requirements import Requirement


def txt_parser(content: str) -> list[str]:
    return [
        line
        for line in map(str.strip, content.splitlines())
        if line and not line.startswith(("#", "./", "-r "))
    ]


def get_current_version(requirement: Requirement) -> Version | None:
    if len(requirement.specifier) != 1:
        return None
    specifier = next(iter(requirement.specifier))
    if specifier.operator != "==":
        return None
    return Version(specifier.version)


def get_sdist_url(requirement: Requirement) -> str:
    with urlopen(f"https://pypi.org/pypi/{requirement.name}/json") as response:
        data = json.load(response)
    for file in data["releases"][str(get_current_version(requirement))]:
        if file["packagetype"] == "sdist":
            return file["url"]
    raise RuntimeError("sdist not found")


def main():
    with open("packages.txt", "r") as file:
        packages = [Requirement(req) for req in txt_parser(file.read())]
    json.dump([get_sdist_url(pkg) for pkg in packages], sys.stdout)


if __name__ == "__main__":
    main()
