#!/usr/bin/env python

from setuptools import setup, find_packages
import sys


with open('README.md') as f:
    readme = f.read()

install_requires = [
    'boto3',
    'future',
    'gnupg>=2.0.2',
    'seria',
    'python-gnupg',
    'pyyaml'
]

setup(
    name='figgypy',
    version='1.2.dev',
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
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Other/Proprietary License',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ],
)
