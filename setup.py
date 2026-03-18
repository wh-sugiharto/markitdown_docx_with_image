#!/usr/bin/env python3
"""
Setup script untuk MarkItDown Image Recovery Tool
Install dengan: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="markitdown-image-recovery",
    version="1.0.0",
    description="Convert DOCX to Markdown with image recovery from legacy folders",
    author="",
    author_email="your.email@example.com",
    py_modules=["fix_markitdown_images"],  # file fix_markitdown_images.py akan di-import
    install_requires=[
        "markitdown",  # dependency utama
    ],
    entry_points={
        "console_scripts": [
            "markitdownimage=fix_markitdown_images:main",  # command name = module:function
        ],
    },
    python_requires=">=3.7",
)
