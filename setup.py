#!/usr/bin/env python3
"""
Setup script for Screeny - High-quality screenshot capture tool
"""

from setuptools import setup, find_packages

setup(
    name="screeny",
    version="1.0.0",
    description="High-quality full-page screenshot capture tool",
    author="AI Assistant",
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0"
    ],
    py_modules=["screeny"],
    entry_points={
        "console_scripts": [
            "screeny=screeny:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)