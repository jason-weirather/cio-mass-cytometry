from setuptools import setup, find_packages
from codecs import open
from os import path

this_folder = path.abspath(path.dirname(__file__))
with open(path.join(this_folder, 'README.md'), encoding='utf-8') as inf:
    long_description = inf.read()

setup(
    name='cio_mass_cytometry',
    version='0.1.4',
    description='Check the assumptions of inputs for pythologist ahead of reading',
    long_description=long_description,
    test_suite='nose2.collector.collector',
    tests_require=['nose2'],
    url='https://github.com/jason-weirather/cio-mass-cytometry',
    author='Jason L Weirather',
    author_email='jason.weirather@gmail.com',
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
    ],
    keywords='bioinformatics',
    packages=find_packages(exclude=['data']),  # exclude non-Python packages like 'data'
    install_requires=['jsonschema', 'importlib_resources', 'XlsxWriter', 'openpyxl'],
    include_package_data=True,
    package_data={
        'cio_mass_cytometry': [
            'schemas/*.json',
            'data/*.fcs',
            'data/*.xlsx',
            'catalyst_wrapper/*.R',
        ]
    },
    entry_points={
        'console_scripts': [
            'masscytometry-templates=cio_mass_cytometry.cli:main'
        ]
    }
)

