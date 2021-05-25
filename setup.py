from os import path

from setuptools import find_packages
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pykorm',
    version='0.54.0',
    description='Pykorm: a dead simple Kubernetes ORM',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Frankkkkk/pykorm',
    author='Frank Villaro-Dixon - Infomaniak Network SA',
    author_email='frank.villaro@infomaniak.com',
    license='GNU General Public License v3 (GPLv3)',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=['kubernetes>=11.0', 'dpath==2.0.1'])
