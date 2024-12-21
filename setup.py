#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pwa2native",
    version="0.1.0",
    author="Ismail Courr",
    author_email="contact@ismailcourr.com",
    description="Convert Progressive Web Apps to Native Applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ismailco/PWA2Native",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        'requests>=2.31.0',
        'colorama>=0.4.6',
        'pathlib>=1.0.1',
        'Pillow>=9.0.0',
        'beautifulsoup4>=4.12.0'
    ],
    entry_points={
        'console_scripts': [
            'pwa2native=pwa2native.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'pwa2native': [
            'templates/android/*',
            'templates/ios/*',
            'templates/macos/*',
            'templates/windows/*'
        ],
    },
)
