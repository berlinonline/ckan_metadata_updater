from distutils.core import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Application name:
    name="CKAN Metadata Updater",

    # Version number (initial):
    version="0.1.0",

    description='''A public API for CKAN's validator functions''',
    long_description=long_description,

    # Application author details:
    author="Knud Möller",
    author_email="knud.moeller@berlinonline.de",

    # What does your project relate to?
    keywords='''CKAN tool metadata open_data''',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(include=['berlinonline', 'berlinonline*']),

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/berlinonline/ckan_metadata_updater",

    #
    # license="LICENSE.txt",

    # Dependent packages (distributions)
    install_requires=[
        "ckanapi",
    ],
)
