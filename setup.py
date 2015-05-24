from setuptools import setup, find_packages

import visitingTimes

setup(
    name='visitingTimes',
    version=visitingTimes.__version__,
    author='',
    author_email='',
    packages=find_packages(exclude=['test']),
    description='Museum Visiting Times',
    long_description=open('README.md').read(),
    url='',
)
