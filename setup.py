# Third-party libraries
from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="turkey_bowl",
    version="2020.2",
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
        "numpy~=1.19.3",
        "pandas~=1.1.4",
        "PyQt5",
        "requests~=2.24",
        "tqdm~=4.51.0",
        "traits",
        "traitsui" "typer",
        "XlsxWriter~=1.3.7",
        "xlrd~=1.2.0",
    ],
    extra_require={
        "dev": [
            "black>=20.8b1",
            "bump2version>=1.0.1",
            "check-manifest>=0.45",
            "codecov>=2.1.10",
            "pre-commit>=2.8.2",
            "pytest>=6.1.2",
            "pytest-cov>=2.10.1",
            "pytest-freezegun>=0.4.2",
            "responses>=0.12.0",
        ]
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
