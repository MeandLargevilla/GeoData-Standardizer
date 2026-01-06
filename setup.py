"""Setup script for GeoData-Standardizer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#') and not line.startswith('-r')]

setup(
    name="geodata-standardizer",
    version="0.1.0",
    author="GeoData-Standardizer Contributors",
    author_email="",
    description="A Python tool for standardizing geophysical data formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MeandLargevilla/GeoData-Standardizer",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "minimal": read_requirements("requirements-minimal.txt"),
    },
    entry_points={
        "console_scripts": [
            "geodata-standardizer=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
