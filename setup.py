from setuptools import setup
import re
import os

SHORT='Addicty is a dictionary whose items can be set using both attribute and item syntax.'
LONG=('Addicty is a module that exposes a dictionary subclass that allows items to be set like attributes. '
     'Values are gettable and settable using both attribute and item syntax. '
     'For more info check out the README at \'github.com/jpn--/addicty\'.')

with open('requirements.txt') as f:
    requirements_lines = f.readlines()
install_requires = [r.strip() for r in requirements_lines]

def version(path):
    """Obtain the packge version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, path), encoding='utf-8') as f:
        version_file = f.read()
    version_match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

VERSION = version('addicty/__init__.py')

setup(
    name='addicty',
    version=VERSION,
    packages=['addicty'],
    url='https://github.com/jpn--/addicty',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    description=SHORT,
    long_description=LONG,
    test_suite='test_addict',
    package_data={'': ['LICENSE']},
    install_requires=install_requires,
)
