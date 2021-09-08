from setuptools import Distribution
from setuptools.command.install import install

i = install(Distribution())
i.ensure_finalized()
print(i.install_scripts)
