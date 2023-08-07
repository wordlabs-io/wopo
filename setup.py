from setuptools import setup, find_packages
import os
from pathlib import Path
VERSION = '0.0.2'
DESCRIPTION = 'wordlabs open prompt optimiser: Automatic prompt optimisation'
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="wopo",
    version=VERSION,
    author="wordlabs.io",
    author_email="<tanishk.kithannae@wordlabs.io>",
    url="https://github.com/wordlabs-io/wopo",
    license='LICENSE.txt',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['tqdm', 'pandas'],
    keywords=['python', 'nlp', 'prompt', 'optimisation'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
