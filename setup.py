from pathlib import Path

from setuptools import setup

current_dir = Path(__file__).parent.resolve()

with open(current_dir / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="inspectortiger",
    version="0.4.2",
    packages=["inspectortiger"],
    url="https://github.com/thg-consulting/inspectortiger",
    author="thg",
    install_requires=["reportme"],
    description="Inspector Tiger is a common non-pythonic pattern checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["inspectortiger = inspectortiger.__main__:main"]},
    include_package_data=True,
    package_data={"inspectortiger": ["inspectortiger/*.ini"]},
)
