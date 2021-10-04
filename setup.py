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
    url="https://github.com/loganthomas/turkey-bowl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "click-spinner",
        "numpy~=1.19.3",  # pin due to openpyxl error
        "pandas~=1.1.4",  # pin due to openpyxl error
        "requests",
        "tqdm",
        "typer",
        "XlsxWriter~=1.3.7",  # pin due to openpyxl error
        "xlrd~=1.2.0",  # pin due to openpyxl error
    ],
    extra_require={
        "dev": [
            "black",
            "bump2version",
            "check-manifest",
            "codecov",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "pytest-freezegun",
            "responses",
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
    entry_points={
        "console_scripts": ["turkey_bowl = turkey_bowl.turkey_bowl_runner:main"]
    },
)
