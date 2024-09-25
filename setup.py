"""Script to install exam paper downloader."""
from setuptools import setup, find_packages

# Read the contents of your README file
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='exam_downloader',
    version='0.1.0',
    description='A script to download A-Level test papers and mark schemes from xtremepape.rs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fam007e/OandALvl-exam-paper-downloader',
    author='Faisal Ahmed Moshiur',
    author_email='faisalmoshiur+gitpy@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'beautifulsoup4>=4.9.3',
    ],
    entry_points={
        'console_scripts': [
            'exam-downloader=DWNFDCleaner.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
