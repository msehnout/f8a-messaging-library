#!/usr/bin/python3

"""Project setup file for the release monitor project."""

import os

from setuptools import setup, find_packages


def get_requirements():
    """Gather requirements for the module."""
    requirements_txt = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    with open(requirements_txt) as fd:
        lines = fd.read().splitlines()

    return list(line for line in lines if not line.startswith('#'))


setup(
    name='f8a-messaging-library',
    version='0.1',
    packages=find_packages(),
    install_requires=get_requirements(),
    include_package_data=True,
    author='Martin Sehnoutka',
    author_email='msehnout@redhat.com',
    description='Library for interfacing with our messaging system',
    license='MIT',
    keywords='fabric8 analytics',
    url='https://github.com/msehnout/'
        'f8a-messaging-library',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
    ]
)