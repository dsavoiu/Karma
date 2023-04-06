#!/usr/bin/env python

import os
import errno
import subprocess
import sys

from setuptools import find_packages, setup
from setuptools.command.develop import develop


# -- helper functions

def mkdirs_exist_ok(dir_name):
    """
    Ensure a directory and all intermediate directories exist.
    """
    try:
        os.makedirs(dir_name)
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


def create_if_not_exists(path, directory=False):
    """
    Create an empty file (or directory if `directory` is True)
    at `path` if it does not exist.
    """
    if os.path.exists(path):
        return

    if directory:
        mkdirs_exist_ok(path)
    else:
        # ensure parent directory exists
        mkdirs_exist_ok(os.path.dirname(path))
        # create file
        open(path, 'a').close()


def iter_intermediate_paths(path):
    """
    Generator to yield all intermediate paths.
    """
    other_ancestors, inner_dir = os.path.split(path)
    if other_ancestors:
        for ancestor in iter_ancestors(other_ancestors):
            yield ancestor
    yield inner_dir


def ensure_dir_exists_importable(dir_path, check_intermediate=False):
    """
    Ensure a directory (and optionally all intermediate directories) is
    importable as a Python package.
    """
    # ensure directory exists
    create_if_not_exists(dir_path, directory=True)
    create_if_not_exists('{}/__init__.py'.format(dir_path))

    if not check_intermediate:
        return

    # ensure it (and all intermediate diretories) are importable
    for intermediate_path in iter_intermediate_paths(dir_path):
        create_if_not_exists('{}/__init__.py'.format(intermediate_path))


# -- custom install routine to ensure the creation of an importable
#    package path

class CustomDevelopCommand(develop):
    """Custom handler for 'develop' command."""

    STANDALONE_PACKAGE_DIR = "Karma/PostProcessing"

    def run(self):
        print('custom_develop!')

        # ensure importable directory hierarchy up to STANDALONE_PACKAGE_DIR
        last_intermediate_path, _ = os.path.split(self.STANDALONE_PACKAGE_DIR)
        ensure_dir_exists_importable(last_intermediate_path, check_intermediate=True)

        # ensure a relative symlink that points to the 'python' directory
        # exists at the STANDALONE_PACKAGE_DIR
        if not os.path.exists(self.STANDALONE_PACKAGE_DIR):
            link = os.path.relpath("python", last_intermediate_path)
            os.symlink(link, self.STANDALONE_PACKAGE_DIR)

        # call super
        develop.run(self)

        # ensure STANDALONE_PACKAGE_DIR is importable
        ensure_dir_exists_importable(self.STANDALONE_PACKAGE_DIR)


def get_version():
    '''try to determine version via git'''
    try:
        # is git available?
        subprocess.call('git', shell=False, stdout=subprocess.PIPE)
    except OSError:
        # 'git' not available
        return "dev"

    try:
        # in git repo?
        subprocess.check_output('git status', shell=True)
    except subprocess.CalledProcessError:
        # not a 'git' repo
        version = "dev"
    else:
        # git repo found -> get release from git

        # is 'git describe' working>
        try:
            # git describe working -> use output
            version = subprocess.check_output('git describe', shell=True).strip().decode()
        except subprocess.CalledProcessError:
            # git describe not working -> use commit hash
            version = 'git-' + subprocess.check_output('git log -1 --format=%h', shell=True).strip().decode()

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
        'PyYaml',
        'unittest2',
    ]

    if sys.version_info[0] == 2:
        _basic_requirements += ['enum']
    elif sys.version_info[0] == 3:
        _basic_requirements += []

    return _basic_requirements


__version__ = get_version()

setup(
    name='Karma',
    version=__version__,
    description='Toolset for HEP analyses with multithreading support.',
    author='Daniel Savoiu',
    author_email='daniel.savoiu@cern.ch',
    url='http://github.com/dsavoiu/Karma',
    packages=['Karma.PostProcessing.{}'.format(_pkg) for _pkg in find_packages('python')],
    package_dir = {
        'Karma.PostProcessing': './python',
    },
    scripts=['scripts/lumberjack.py', 'scripts/palisade.py'],
    keywords = "data analysis cms cern",
    license='MIT',
    install_requires=get_requirements(),

    cmdclass={
        'develop': CustomDevelopCommand,
    },

 )
