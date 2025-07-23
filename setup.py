from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mobile_pro/__init__.py
from mobile_pro import __version__ as version

setup(
    name="mobile_pro",
    version=version,
    description="Comprehensive business management platform for cellphone stores",
    author="Mobile Pro Team",
    author_email="support@mobilepro.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=[],
)