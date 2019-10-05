from pathlib import Path

from setuptools import find_packages, setup

name = "inspectortiger"
current_dir = Path(__file__).parent.resolve()

with open(current_dir / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=f"{name}",
    version="0.7.0",
    packages=find_packages(),
    url="https://github.com/thg-consulting/inspectortiger",
    author="thg",
    description="Modern python code review tool / framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": [f"{name} = {name}.__main__:main"]},
)
