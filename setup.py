from setuptools import setup
from setuptools import find_packages

setup(
    name='pykorm',
    version='0.43',
    description='Pykorm: a dead simple Kubernetes ORM',
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=['kubernetes'])

