#!/usr/bin/env python

import os
import six
import subprocess
import sys

from setuptools import find_packages, setup


def get_version():
    '''try to determine version via git'''
    try:
        # is git available?
        subprocess.call('git', stdout=subprocess.PIPE)
    except IOError:
        # 'git' not available
        version = "dev"  # the short X.Y version.
    else:
        # 'git' found -> get release from git

        # is 'git describe' working
        try:
            # git describe working -> use output
            version = subprocess.check_output(['git', 'describe']).strip().decode()
        except subprocess.CalledProcessError:
            # git describe not working -> use commit hash
            version = 'git-' + subprocess.check_output(['git', 'log', '-1', '--format=%h']).strip().decode()

    return version


def get_requirements():
    _basic_requirements = [
        'NumPy',
        'Scipy',
        'matplotlib',
        'sphinx',
        'mock',
        'tqdm',
        'pandas',
    ]

    if six.PY2:
        _basic_requirements += ['enum']
    elif six.PY3:
        _basic_requirements += []

    return _basic_requirements

def ensure_standalone_package_path(final_symlink_path):
    '''ensure that a dummy prefix path exists which is importable as a package'''

    _final_symlink_path_split = final_symlink_path.split('/')

    _cumulated_paths = ''
    for _i in range(len(_final_symlink_path_split)-1):
        _cumulated_path = os.path.join(*_final_symlink_path_split[:_i+1])
        # create directory
        if not os.path.exists(_cumulated_path):
            os.mkdir(_cumulated_path)
        # 'touch' __init__ file to ensure it exists
        _initfile_path = '{}/__init__.py'.format(_cumulated_path)
        if not os.path.exists(_initfile_path):
            open(_initfile_path, 'a').close()

    if not os.path.exists(final_symlink_path):
        os.symlink(os.path.join(*(['..']*(len(_final_symlink_path_split)-1)+['python'])), final_symlink_path)

# create 'dummy' path with '__init__' files and symlink to '/python'
ensure_standalone_package_path('Karma/PostProcessing')

__version__ = get_version()

setup(
    name='Karma',
    version=__version__,
    description='Toolset for HEP analyses with multithreading support.',
    author='Daniel Savoiu',
    author_email='daniel.savoiu@cern.ch',
    url='http://github.com/dsavoiu/Karma',
    packages=find_packages(),
    scripts=['scripts/lumberjack.py', 'scripts/palisade.py'],
    keywords = "data analysis cms cern",
    license='MIT',
    install_requires=get_requirements(),
 )
