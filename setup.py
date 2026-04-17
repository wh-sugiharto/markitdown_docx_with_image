#!/usr/bin/env python3
"""
Setup script untuk markitdownimage
Install dengan: pip install -e .
Kemudian panggil: markitdownimage file.docx
"""

from setuptools import setup

setup(
    name="markitdownimage",
    version="1.1.0",
    description="Convert DOCX to Markdown with embedded image extraction",
    author="",
    author_email="",
    python_requires=">=3.10",
    py_modules=["markitdownimage"],   # merujuk ke markitdownimage.py
    install_requires=[
        "markitdown",
    ],
    entry_points={
        "console_scripts": [
            # perintah CLI → module:function
            "markitdownimage=markitdownimage:main",
        ],
    },
)
