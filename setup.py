from setuptools import setup, find_packages

setup(
    name='dcpm',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'questionary',
    ],
    entry_points={
        'console_scripts': [
            'dcpm=dcpm.cli:main',
        ],
    },
)