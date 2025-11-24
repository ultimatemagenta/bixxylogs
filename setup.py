from setuptools import setup, find_packages

setup(
    name="bixxylogs",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    author="ultimatemagenta",
    description="A colorful, category-based logging library with emoji indicators",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ultimatemagenta/bixxylogs",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
