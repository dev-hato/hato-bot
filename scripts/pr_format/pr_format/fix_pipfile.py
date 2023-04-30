import importlib.util
import os
import re
import sys
from pathlib import Path
from typing import TypeGuard

import importlib_metadata
import toml

Packages = dict[str, str]
PipfilePackages = dict[str, str | Packages]
PipfileValue = list[dict[str, str | bool]] | PipfilePackages
Pipfile = dict[str, PipfileValue]


def is_pipfile_packages(pipfile_value: PipfileValue) -> TypeGuard[PipfilePackages]:
    if type(pipfile_value) is list:
        return False

    for k, v in pipfile_value.items():
        if not isinstance(k, str):
            return False

        if isinstance(v, str):
            continue

        for k2, v2 in v.items():
            if not isinstance(k2, str) or not isinstance(v2, str):
                return False

    return True


def get_package_version(package_name: str) -> str:
    try:
        dist = importlib_metadata.distribution(package_name)
    except importlib_metadata.PackageNotFoundError:
        return "*"

    return f"=={dist.version}"


def fix_package_version(packages: PipfilePackages) -> PipfilePackages:
    for package_name in packages.keys():
        if packages[package_name] == "*":
            packages[package_name] = get_package_version(package_name)

    return packages


def is_std_or_local_lib(project_root: Path, package_name: str) -> bool:
    if package_name in sys.builtin_module_names:
        return True

    try:
        module_spec = importlib.util.find_spec(package_name)
    except (AttributeError, ValueError, ModuleNotFoundError):
        module_spec = None

    if module_spec is None:
        for finder in sys.meta_path:
            try:
                module_spec = finder.find_spec(package_name, ".")
            except (AttributeError, ValueError, ModuleNotFoundError):
                pass

            if module_spec:
                break

    if module_spec is None:
        return False

    module_origin = module_spec.origin

    if not module_origin:
        return False

    if project_root.resolve() in Path(module_origin).resolve().parents:
        return True

    if module_origin.startswith(sys.base_prefix):
        return True

    return False


def get_imported_packages(project_root: Path) -> set[str]:
    imported_packages: set[str] = set()

    for dir_path, _, file_list in os.walk(project_root):
        if "node_modules" in dir_path:
            continue

        for file_name in file_list:
            if not file_name.endswith(".py"):
                continue

            with open(os.path.join(dir_path, file_name), "r") as python_file:
                for imported_package in re.findall(
                    r"^(?:import|from)\s+(\w+)", python_file.read(), re.MULTILINE
                ):
                    if not is_std_or_local_lib(project_root, imported_package):
                        imported_packages.add(imported_package)

    return imported_packages


def get_pipfile_packages(pipfile: Pipfile) -> set[str]:
    pipfile_packages: set[str] = set()

    for key in ["packages", "dev-packages"]:
        pipfile_packages |= set(pipfile[key].keys())

    return pipfile_packages


def exist_package_in_pipfile(packages: list[str], pipfile_packages: set[str]) -> bool:
    for package_name in packages:
        for pn in [package_name, package_name.lower()]:
            if pn in pipfile_packages:
                return True

    return False


def get_missing_packages(
    imported_packages: set[str], pipfile_packages: set[str]
) -> Packages:
    distributions = importlib_metadata.packages_distributions()
    missing_packages: Packages = dict()

    for imported_package in imported_packages:
        if imported_package not in distributions:
            raise ModuleNotFoundError(
                f"Package {imported_package} is not found. It maybe not installed."
            )

        packages = distributions[imported_package]

        if len(packages) == 0:
            raise ModuleNotFoundError(
                f"Package {imported_package} is not found. It maybe not installed."
            )

        if not exist_package_in_pipfile(packages, pipfile_packages):
            package_name: str = packages[0]
            missing_packages[package_name] = get_package_version(package_name)

    return missing_packages


def main():
    project_root: Path = Path.cwd()
    pipfile_path = project_root / "Pipfile"

    if not pipfile_path.exists():
        raise FileNotFoundError("Pipfile not found.")

    pipfile: Pipfile = toml.load(pipfile_path)

    for key in ["packages", "dev-packages"]:
        if is_pipfile_packages(pipfile[key]):
            pipfile[key] = fix_package_version(pipfile[key])

        if key == "packages":
            pipfile[key] |= get_missing_packages(
                get_imported_packages(project_root), get_pipfile_packages(pipfile)
            )

    with open(pipfile_path, "w") as f:
        toml.dump(pipfile, f)


if __name__ == "__main__":
    main()
