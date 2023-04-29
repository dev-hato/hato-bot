import importlib.util
import os
import pathlib
import re
import sys

import importlib_metadata
import toml


def is_std_or_local_lib(project_root, package_name):
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

    if project_root.resolve() in pathlib.Path(module_origin).resolve().parents:
        return True

    if module_origin.startswith(sys.base_prefix):
        return True

    return False


def get_imported_packages(project_root):
    imported_packages = set()

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


def get_pipfile_packages(pipfile):
    pipfile_packages = set()

    for key in ["packages", "dev-packages"]:
        pipfile_packages |= set(pipfile[key].keys())

    return pipfile_packages


def exist_package_in_pipfile(packages, pipfile_packages):
    for package_name in packages:
        for pn in [package_name, package_name.lower()]:
            if pn in pipfile_packages:
                return True

    return False


def get_missing_packages(imported_packages, pipfile_packages):
    distributions = importlib_metadata.packages_distributions()
    missing_packages = dict()

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
            package_name = packages[0]

            try:
                dist = importlib_metadata.distribution(package_name)
            except importlib_metadata.PackageNotFoundError:
                missing_packages[package_name] = "*"
                continue

            missing_packages[package_name] = dist.version

    return missing_packages


def main():
    project_root = pathlib.Path.cwd()
    pipfile_path = project_root / "Pipfile"

    if not pipfile_path.exists():
        raise FileNotFoundError("Pipfile not found.")

    pipfile = toml.load(pipfile_path)
    pipfile["packages"] |= get_missing_packages(
        get_imported_packages(project_root), get_pipfile_packages(pipfile)
    )

    with open(pipfile_path, "w") as f:
        toml.dump(pipfile, f)


if __name__ == "__main__":
    main()
