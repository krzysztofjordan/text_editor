#!/usr/bin/env python
import sys
import yaml

try:
    import tomllib
except ImportError:
    # For Python < 3.11
    import tomli as tomllib


def get_pyproject_dev_dependencies(filepath="pyproject.toml"):
    """Parses dev dependencies from pyproject.toml."""
    with open(filepath, "rb") as f:
        data = tomllib.load(f)

    dev_deps = []
    optional_deps = data.get("project", {}).get("optional-dependencies", {})
    if "dev" in optional_deps:
        for dep_str in optional_deps["dev"]:
            # Basic parsing: name only, ignore version for simplicity here
            # More robust parsing might use packaging.requirements
            dep_name = dep_str.split(">=")[0].split("==")[0].split("<=")[0].split("!=")[0].split("~=")[0]
            dev_deps.append(dep_name.strip())
    return set(dev_deps)


def get_environment_yml_dependencies(filepath="environment.yml"):
    """Parses dependencies from environment.yml."""
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    env_deps = []
    if "dependencies" in data:
        for item in data["dependencies"]:
            if isinstance(item, str):
                # Basic parsing: name only
                dep_name = item.split("=")[0]
                env_deps.append(dep_name.strip())
            # Could handle complex dict items if needed
    return set(env_deps)


def main():
    pyproject_deps = get_pyproject_dev_dependencies()
    env_yml_deps = get_environment_yml_dependencies()

    # We are primarily interested if dev dependencies from pyproject.toml
    # are listed in environment.yml.
    # Python itself is a special case managed differently.
    pyproject_deps.discard("python")
    env_yml_deps.discard("python")

    missing_in_env = pyproject_deps - env_yml_deps

    if missing_in_env:
        print("ERROR: Dependencies from pyproject.toml [project.optional-dependencies.dev] " "are missing in environment.yml:")
        for dep in sorted(list(missing_in_env)):
            print(f"- {dep}")
        print("\nPlease update environment.yml to include these dependencies.")
        sys.exit(1)

    print("SUCCESS: environment.yml contains all dev dependencies from pyproject.toml.")
    sys.exit(0)


if __name__ == "__main__":
    main()
