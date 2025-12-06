"""Setup configuration for Command Explainer."""

from setuptools import setup, find_packages

setup(
    name="cmdex",
    version="0.1.0",
    description="Terminal command generator and explainer powered by Ollama",
    author="Isaiah Myles",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.25.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "cmdex=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: System :: Shells",
    ],
)
