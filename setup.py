# Third-party libraries
from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="turkey_bowl",
    version="2021.1",
    license="MIT",
    description="Turkey Bowl - Thanksgiving Day Draft Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Logan Thomas",
    author_email="logan.thomas005@gmail.com",
    url="https://loganthomas.dev/turkey_bowl/",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "click-spinner",
        "numpy",
        "openpyxl",
        "pandas",
        "PyQt5",
        "requests",
        "tqdm",
        "traits",
        "traitsui",
        "typer",
        "XlsxWriter",
        "xlrd",
    ],
    extra_require={
        "dev": [
            "black",
            "bump2version",
            "check-manifest",
            "codecov",
            "flake8",
            "mypy",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "pytest-freezegun",
            "responses",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: MacOS X",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7",
    entry_points={"console_scripts": ["turkey-bowl = turkey_bowl.cli:app"]},
)
