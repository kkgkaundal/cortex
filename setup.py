from setuptools import setup, find_packages

setup(
    name="cortex",
    version="0.1.0",
    description="Event-Driven, Self-Learning, Portable System Agent with Tiered Memory & Sandbox PoC",
    author="Cortex Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pypdf>=3.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        'console_scripts': [
            'cortex=cortex.cli.main:cli',
        ],
    },
    python_requires='>=3.8',
)
