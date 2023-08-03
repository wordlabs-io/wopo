from setuptools import setup, find_packages
import os

VERSION = '0.0.1'
DESCRIPTION = 'wordlabs open prompt optimiser: Automatic prompt optimisation'
long_description = 'Non parametric plug and play prompt optimisation'

# Setting up
setup(
    name="wopo",
    version=VERSION,
    author="wordlabs.io",
    author_email="<tanishk.kithannae@wordlabs.io>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['tqdm', 'pandas'],
    keywords=['python', 'nlp', 'prompt', 'optimisation'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)