'''SETUP File copied from http://flask.pocoo.org/docs/tutorial/'''
'''Only made modifications to add extra dependencies'''

import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='app',
    version='1.0.0',
    url='http://flask.pocoo.org/docs/tutorial/',
    license='BSD',
    maintainer='Pallets team',
    maintainer_email='contact@palletsprojects.com',
    description='The basic blog app built in the Flask tutorial.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'lxml',
        'flask-restplus'
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
