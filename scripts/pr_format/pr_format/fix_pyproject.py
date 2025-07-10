"""
pyproject.tomlに対して以下の修正を行う。

* pyproject.tomlでのバージョン指定がないパッケージについて、バージョン指定を実際にインストールされるものに修正する
* プロジェクト内のPythonファイルでimportされているがpyproject.toml内には存在しないパッケージをpyproject.tomlの「project.dependencies」セクションに追加する
"""

import importlib.util
import re
import sys
from pathlib import Path
from typing import NoReturn, TypeGuard

import importlib_metadata
import tomlkit

# pyproject.tomlのproject.dependenciesやdependency-groups.devのデータ型
PyProjectDependencies = list[str]

# pyproject.tomlのデータ型
PyProject = dict[str, dict[str, PyProjectDependencies]]

version_operator_pattern = re.compile(r"[\\[<=>@]")


def is_pyproject_dependencies(
    pyproject_dependencies,
) -> TypeGuard[PyProjectDependencies]:
    """
    データがPyProjectDependencies型であるかを判定する
    :param pyproject_dependencies: 判定対象のデータ
    :return: PyProjectDependencies型であるか
    """
    if not isinstance(pyproject_dependencies, list):
        return False

    for v in pyproject_dependencies:
        if not isinstance(v, str):
            return False

    return True


def get_package_version(package_name: str) -> str:
    """
    メタデータからパッケージのバージョンを取得する
    :param package_name: 取得対象のパッケージ名
    :return: パッケージのバージョン (「package_name==X.Y.Z」形式)。バージョンを取得できなかった場合はpackage_nameを返す。
    """
    try:
        package_data = version_operator_pattern.split(package_name)
        dist = importlib_metadata.distribution(package_data[0])
    except importlib_metadata.PackageNotFoundError:
        return package_name

    return f"{package_name}=={dist.version}"


def fix_package_version(packages: PyProjectDependencies) -> PyProjectDependencies:
    """
    project.tomlでのバージョン指定がないパッケージについて、バージョン指定を実際にインストールされるものに修正する
    :param packages: パッケージ一覧
    :return: パッケージ一覧
    """
    for i in range(len(packages)):
        if not re.findall(r"[<=>@]", packages[i]):
            packages[i] = get_package_version(packages[i])

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

    # パッケージ情報がないならばpyproject.tomlによってインストールされたものと判定する
    if package_spec is None:
        return False

    # パッケージのファイルパス
    package_origin = package_spec.origin

    # 次のいずれかならばpyproject.tomlによってインストールされたものと判定する
    # * パッケージのファイルパスが取得できない
    # * パッケージのファイルパス内に「.venv」を含む
    if not package_origin or ".venv" in package_origin:
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
        if (
            str(file).endswith("setup.py")
            or "node_modules" in str(file)
            or ".venv" in str(file)
        ):
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


def get_pyproject_packages(pyproject: PyProject) -> set[str] | NoReturn:
    """
    pyproject.tomlからパッケージ一覧を取得する
    :param pyproject: pyproject.tomlの中身
    :return: pyproject.toml内のパッケージ一覧
    """
    pyproject_packages: set[str] = set()

    for pyproject_dependencies in [
        pyproject["project"]["dependencies"],
        pyproject["dependency-groups"]["dev"],
    ]:
        if not is_pyproject_dependencies(pyproject_dependencies):
            raise TypeError(
                "Failed to cast to PyProjectDependencies: "
                + str(pyproject_dependencies)
            )

        for pyproject_dependency in pyproject_dependencies:
            package_data = version_operator_pattern.split(pyproject_dependency)
            pyproject_packages.add(package_data[0].strip().lower().replace("_", "-"))

    return pyproject_packages


def exist_package_in_pyproject(
    packages: list[str], pyproject_packages: set[str]
) -> bool:
    """
    与えられたパッケージ群のいずれかがpyproject.toml内に存在するかを判定する
    :param packages: パッケージ群
    :param pyproject_packages: pyproject.toml内のパッケージ一覧
    :return: 与えられたパッケージ群のいずれかがpyproject.toml内に存在するか
    """
    for package_name in packages:
        if package_name.lower().replace("_", "-") in pyproject_packages:
            return True

    return False


def get_missing_packages(
    imported_packages: set[str], pyproject_packages: set[str]
) -> PyProjectDependencies | NoReturn:
    """
    プロジェクト内のPythonファイルでimportされているがpyproject.toml内には存在しないパッケージ一覧を取得する
    :param imported_packages: プロジェクト内のPythonファイルからimportされているパッケージ一覧
    :param pyproject_packages: pyproject.toml内のパッケージ一覧
    :return: プロジェクト内のPythonファイルでimportされているがpyproject.toml内には存在しないパッケージ一覧。pyproject.toml内でのパッケージ名がkey、バージョンがvalueになっている。
    """
    # import時のパッケージ名とpyproject.toml内でのパッケージ名の対応表
    distributions = importlib_metadata.packages_distributions()

    missing_packages: PyProjectDependencies = list()

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

        if not exist_package_in_pyproject(packages, pyproject_packages):
            package_name: str = packages[0]
            missing_packages.append(get_package_version(package_name))

    return missing_packages


def main():
    project_root = Path.cwd()
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found.")

    with open(pyproject_path) as f:
        pyproject = tomlkit.load(f)

    if not is_pyproject_dependencies(pyproject["project"]["dependencies"]):
        raise TypeError(
            "Failed to cast to PyProjectDependencies: "
            + str(pyproject["project"]["dependencies"])
        )

    pyproject["project"]["dependencies"] = fix_package_version(
        pyproject["project"]["dependencies"]
    )

    # プロジェクト内のPythonファイルでimportされているがpyproject.toml内には存在しないパッケージをpyproject.tomlの「project.dependencies」セクションに追加する
    pyproject["project"]["dependencies"] += get_missing_packages(
        get_imported_packages(project_root), get_pyproject_packages(pyproject)
    )

    if not is_pyproject_dependencies(pyproject["dependency-groups"]["dev"]):
        raise TypeError(
            "Failed to cast to PyProjectDependencies: "
            + str(pyproject["dependency-groups"]["dev"])
        )

    pyproject["dependency-groups"]["dev"] = fix_package_version(
        pyproject["dependency-groups"]["dev"]
    )

    with open(pyproject_path, "w") as f:
        tomlkit.dump(pyproject, f)


if __name__ == "__main__":
    main()
