# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="fairway",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "numpy",
        "inject",
        "pytest",
    ],
    license="MIT",
    scripts=["bin/fairway"],
)