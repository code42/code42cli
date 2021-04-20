from codecs import open
from os import path

from setuptools import find_packages
from setuptools import setup

here = path.abspath(path.dirname(__file__))

about = {}
with open(path.join(here, "src", "code42cli", "__version__.py"), encoding="utf8") as fh:
    exec(fh.read(), about)

with open(path.join(here, "README.md"), "r", "utf-8") as f:
    readme = f.read()

setup(
    name="code42cli",
    version=about["__version__"],
    url="https://github.com/code42/py42",
    project_urls={
        "Issue Tracker": "https://github.com/code42/code42cli/issues",
        "Documentation": "https://clidocs.code42.com/",
        "Source Code": "https://github.com/code42/code42cli",
    },
    description="The official command line tool for interacting with Code42",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=[
        "click>=7.1.1",
        "click_plugins>=1.1.1",
        "colorama>=0.4.3",
        "c42eventextractor==0.4.1",
        "keyring==18.0.1",
        "keyrings.alt==3.2.0",
        "pandas>=1.1.3",
        "py42>=1.11.1",
    ],
    extras_require={
        "dev": [
            "flake8==3.8.3",
            "pytest==4.6.11",
            "pytest-cov==2.10.0",
            "pytest-mock==2.0.0",
            "tox>=3.17.1",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["code42=code42cli.main:cli"]},
)
