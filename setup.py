import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ftt",
    version="0.1",
    author="mumubebe",
    description="Transer files between tmux panes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mumubebe/ftt/",
    project_urls={
        "Bug Tracker": "https://github.com/mumubebe/ftt/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    setup_requires=["wheel"],
    entry_points={
        "console_scripts": [
            "ftt=ttf.cli:main",
        ],
    },
)