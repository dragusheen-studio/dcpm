from setuptools import setup, find_packages

setup(
    name='dcpm',
    version='1.0.0',
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
