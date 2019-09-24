#!/usr/bin/env python

from setuptools import setup, find_packages
import sys


with open('README.md') as f:
    readme = f.read()

install_requires = [
    'boto3',
    'future',
    'pretty-bad-protocol',
    'seria',
    'pyyaml'
]

setup(
    name='figgypy',
    version='1.1.9',
    description='Simple configuration tool. Get config from yaml, json, or xml.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Adam Sherwood',
    author_email='theherk@gmail.com',
    url='https://github.com/theherk/figgypy',
    download_url='https://github.com/theherk/figgypy/archive/1.2.dev.zip',
    packages=find_packages(),
    platforms=['all'],
    license='MIT',
    install_requires=install_requires,
    test_suite='tests'
)
