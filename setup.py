#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
        name='API',
        version='1.0.0',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'flask',
            'flask-cors',
            'flask-SQLAlchemy',
            'psycopg2-binary',
            'Flask-Migrate',
            'Flask-Script',
            'Flask-Mail',
            'pytest',
            'Flask-JWT-Extended',
            'selenium',
            'gunicorn',
            'boto3'
        ],
    )
