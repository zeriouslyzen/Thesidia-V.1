#!/usr/bin/env python3
"""Setup script for Thesidia"""

from setuptools import setup, find_packages

setup(
    name="thesidia",
    version="1.0.0",
    description="Emergent Consciousness Engine - Thesidia",
    author="",
    packages=find_packages(),
    install_requires=[
        "ollama>=0.1.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    python_requires=">=3.8",
)
