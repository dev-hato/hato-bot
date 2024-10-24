"""
Pipfileに対して以下の修正を行う。

* Pipfileでのバージョン指定が「*」となっているパッケージについて、バージョン指定を実際にインストールされるものに修正する
* プロジェクト内のPythonファイルでimportされているがPipfile内には存在しないパッケージをPipfileの「packages」セクションに追加する
"""

import importlib.util
import re
import sys
from pathlib import Path
from typing import NoReturn, TypeGuard

import importlib_metadata
import toml

# Pipfileの「packages」「dev-packages」セクションのデータ型
PipfilePackages = dict[str, str | dict[str, str | list[str]]]

# Pipfileのいずれかのセクションのデータ型
PipfileValue = PipfilePackages | list[dict[str, str | bool]]

# Pipfileのデータ型
Pipfile = dict[str, PipfileValue]


def is_pipfile_packages(pipfile_value: PipfileValue) -> TypeGuard[PipfilePackages]:
    """
    PipfileValue型 のデータがPipfilePackages型であるかを判定する
    :param pipfile_value: 判定対象のデータ
    :return: PipfilePackages型であるか
    """
    if not isinstance(pipfile_value, dict):
        return False

    for k, v in pipfile_value.items():
        if not isinstance(k, str):
            return False

        if isinstance(v, str):
            continue

        for k2, v2 in v.items():
            if not isinstance(k2, str):
                return False

            if isinstance(v2, list):
                for v3 in v2:
                    if not isinstance(v3, str):
                        return False
            elif not isinstance(v2, str):
                return False

    return True


def get_package_version(package_name: str) -> str:
    """
    メタデータからパッケージのバージョンを取得する
    :param package_name: 取得対象のパッケージ名
    :return: パッケージのバージョン (「==X.Y.Z」形式)。バージョンを取得できなかった場合は「*」を返す。
    """
    try:
        dist = importlib_metadata.distribution(package_name)
    except importlib_metadata.PackageNotFoundError:
        return "*"

    return f"=={dist.version}"


def fix_package_version(packages: PipfilePackages) -> PipfilePackages:
    """
    Pipfileでのバージョン指定が「*」となっているパッケージについて、バージョン指定を実際にインストールされるものに修正する
    :param packages: パッケージ一覧
    :return: パッケージ一覧
    """
    for package_name in packages.keys():
        if packages[package_name] == "*":
            packages[package_name] = get_package_version(package_name)

    return packages


def is_std_or_local_lib(project_root: Path, package_name: str) -> bool:
    """
    与えられたパッケージが標準パッケージ or 独自に定義したものであるかを判定する
    :param project_root: プロジェクトのルートディレクトリのパス
    :param package_name: 判定対象のパッケージ名
    :return: 与えられたパッケージが標準パッケージ or 独自に定義したものであるか
    """
    # 与えられたパッケージがビルドインのモジュールならば標準パッケージと判定する
    if package_name in sys.builtin_module_names:
        return True

    package_spec = None

    # Finderを使ってパッケージ情報 (Spec) を取得する
    for finder in sys.meta_path:
        try:
            package_spec = finder.find_spec(package_name, ".")
        except (AttributeError, ValueError, ModuleNotFoundError):
            pass

        if package_spec:
            break

    if package_spec is None:
        try:
            package_spec = importlib.util.find_spec(package_name)
        except (AttributeError, ValueError, ModuleNotFoundError):
            pass

    # パッケージ情報がないならばPipfileによってインストールされたものと判定する
    if package_spec is None:
        return False

    # パッケージのファイルパス
    package_origin = package_spec.origin

    # パッケージのファイルパスが取得できないならばPipfileによってインストールされたものと判定する
    if not package_origin:
        return False

    # パッケージのファイルパスがプロジェクト内のものであれば独自に定義したものと判定する
    if project_root.resolve() in Path(package_origin).resolve().parents:
        return True

    # パッケージのファイルパスがPythonのシステムのパスと一致するならば標準パッケージと判定する
    if package_origin.startswith(sys.base_prefix):
        return True

    return False


def get_imported_packages(project_root: Path) -> set[str]:
    """
    プロジェクト内のPythonファイルからimportされているパッケージの一覧 (標準パッケージや独自に定義したものを除く) を取得する
    :param project_root: プロジェクトのルートディレクトリのパス
    :return: プロジェクト内のPythonファイル内でimportされているパッケージの一覧 (標準パッケージや独自に定義したものを除く)
    """
    imported_packages: set[str] = set()

    for file in project_root.glob("**/*.py"):
        if str(file).endswith("setup.py") or "node_modules" in str(file):
            continue

        with open(str(file), "r") as python_file:
            for imported_package in re.findall(
                r"^(?:import|from)\s+(\w+)", python_file.read(), re.MULTILINE
            ):
                if imported_package != "sudden_death" and not is_std_or_local_lib(
                    project_root, imported_package
                ):
                    imported_packages.add(imported_package)

    return imported_packages


def get_pipfile_packages(pipfile: Pipfile) -> set[str] | NoReturn:
    """
    Pipfileからパッケージ一覧を取得する
    :param pipfile: Pipfileの中身
    :return: Pipfile内のパッケージ一覧
    """
    pipfile_packages: set[str] = set()

    for key in ["packages", "dev-packages"]:
        pipfile_value = pipfile[key]

        if not is_pipfile_packages(pipfile_value):
            raise TypeError("Failed to cast to PipfilePackages: " + str(pipfile_value))

        for package_name in pipfile_value.keys():
            pipfile_packages.add(package_name.lower().replace("_", "-"))

    return pipfile_packages


def exist_package_in_pipfile(packages: list[str], pipfile_packages: set[str]) -> bool:
    """
    与えられたパッケージ群のいずれかがPipfile内に存在するかを判定する
    :param packages: パッケージ群
    :param pipfile_packages: Pipfile内のパッケージ一覧
    :return: 与えられたパッケージ群のいずれかがPipfile内に存在するか
    """
    for package_name in packages:
        if package_name.lower().replace("_", "-") in pipfile_packages:
            return True

    return False


def get_missing_packages(
    imported_packages: set[str], pipfile_packages: set[str]
) -> dict[str, str] | NoReturn:
    """
    プロジェクト内のPythonファイルでimportされているがPipfile内には存在しないパッケージ一覧を取得する
    :param imported_packages: プロジェクト内のPythonファイルからimportされているパッケージ一覧
    :param pipfile_packages: Pipfile内のパッケージ一覧
    :return: プロジェクト内のPythonファイルでimportされているがPipfile内には存在しないパッケージ一覧。Pipfile内でのパッケージ名がkey、バージョンがvalueになっている。
    """
    # import時のパッケージ名とPipfile内でのパッケージ名の対応表
    distributions = importlib_metadata.packages_distributions()

    missing_packages: dict[str, str] = dict()

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
    project_root = Path.cwd()
    pipfile_path = project_root / "Pipfile"

    if not pipfile_path.exists():
        raise FileNotFoundError("Pipfile not found.")

    pipfile = toml.load(pipfile_path)

    for key in ["packages", "dev-packages"]:
        if not is_pipfile_packages(pipfile[key]):
            raise TypeError("Failed to cast to PipfilePackages: " + str(pipfile[key]))

        pipfile[key] = fix_package_version(pipfile[key])

        # プロジェクト内のPythonファイルでimportされているがPipfile内には存在しないパッケージをPipfileの「packages」セクションに追加する
        if key == "packages":
            pipfile[key] |= get_missing_packages(
                get_imported_packages(project_root), get_pipfile_packages(pipfile)
            )

    with open(pipfile_path, "w") as f:
        toml.dump(pipfile, f)


if __name__ == "__main__":
    main()
