"""
Setup configuration for Screening Bot V2
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="screening-bot-v2",
    version="2.0.0",
    author="Davide",
    author_email="",
    description="Un bot automatizzato per l'analisi e il monitoraggio delle performance delle criptovalute",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dado-hash/Screening_bot_V2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "screening-bot=update_historical_datas:main",
        ],
    },
)
