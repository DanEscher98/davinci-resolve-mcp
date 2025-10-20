"""
DaVinci Resolve MCP Server Setup
Python package configuration for PyPI distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().splitlines()
    # Filter out comments and empty lines
    requirements = [
        req.strip() for req in requirements
        if req.strip() and not req.startswith('#')
    ]

setup(
    name="davinci-resolve-mcp",
    version="2.0.0",
    author="Samuel Gursky",
    author_email="samuel@example.com",
    description="Model Context Protocol server for DaVinci Resolve",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samuelgursky/davinci-resolve-mcp",
    project_urls={
        "Bug Tracker": "https://github.com/samuelgursky/davinci-resolve-mcp/issues",
        "Documentation": "https://github.com/samuelgursky/davinci-resolve-mcp#readme",
        "Source Code": "https://github.com/samuelgursky/davinci-resolve-mcp",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Non-Linear Editor",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resolve-mcp-server=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "davinci-resolve",
        "mcp",
        "model-context-protocol",
        "video-editing",
        "automation",
        "ai-assistant",
        "color-grading",
        "post-production",
    ],
)
