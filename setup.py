from codecs import open
from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

about = {}
with open(path.join(here, "src", "code42cli", "__version__.py"), encoding="utf8") as fh:
    exec(fh.read(), about)

with open(path.join(here, "README.md"), "r", "utf-8") as f:
    readme = f.read()

setup(
    name="code42cli",
    version=about["__version__"],
    description="The official command line tool for interacting with Code42",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    install_requires=[
        "c42eventextractor==0.3.2",
        "keyring==18.0.1",
        "keyrings.alt==3.2.0",
        "py42>=1.2.0",
    ],
    license="MIT",
    include_package_data=True,
    zip_safe=False,
    extras_require={
        "dev": [
            "pre-commit",
            "pytest==4.6.5",
            "pytest-cov == 2.8.1",
            "pytest-mock==2.0.0",
            "recommonmark",
            "sphinx",
            "sphinx_rtd_theme",
            "tox==3.14.3",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    scripts=["bin/code42cli_completer"],
    entry_points={"console_scripts": ["code42=code42cli.main:main"]},
)
