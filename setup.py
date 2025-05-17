from setuptools import setup, find_packages

setup(
    name='db_api',
    version='0.1',
    description='A Python package for interacting with the Deutsche Bahn API',
    author='Kimon Beyer',
    packages=find_packages(),
    install_requires=[
        'requests',
        'xmltodict',
    ],
)