from setuptools import setup
import addicty

SHORT='Addicty is a dictionary whose items can be set using both attribute and item syntax.'
LONG=('Addicty is a module that exposes a dictionary subclass that allows items to be set like attributes. '
     'Values are gettable and settable using both attribute and item syntax. '
     'For more info check out the README at \'github.com/jpn--/addicty\'.')

setup(
    name='addicty',
    version=addicty.__version__,
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
    package_data={'': ['LICENSE']}
)
