# coding: utf-8
import io
import os
import re

from setuptools import find_packages, setup


CWD = os.path.dirname(os.path.abspath(__file__))

about = {}
with open(os.path.join(CWD, 'logparser', '__version__.py')) as f:
    exec(f.read(), about)

with io.open("README.md", 'r', encoding='utf-8') as f:
    long_description = re.sub(r':\w+:\s', '', f.read())  # Remove emojis


setup(
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    description=about['__description__'],

    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(exclude=("tests", )),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    install_requires=[
        "pexpect >= 4.7.0",  # Apr 7, 2019
        "six >= 1.12.0",  # Dec 10, 2018
    ],

    entry_points={
        "console_scripts": {
            "logparser = logparser.run:main"
        }
    },

    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
