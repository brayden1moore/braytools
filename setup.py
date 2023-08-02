from setuptools import setup, find_packages

setup(
    name='braytools',
    version='1.0.0',
    description='A module for validating contact data. For personal use.',
    author='Brayden Moore',
    author_email='brayden@braydenmoore.com',
    url='https://github.com/brayden1moore/braytools',
    scripts=['braytools.py'],
    packages=find_packages(),
    install_requires=[
        'pandas',
        'tqdm',
        'names_dataset'
    ]
)
