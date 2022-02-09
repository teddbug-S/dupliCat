from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="dupliCat",
    version="2.3.2",
    author="Divine Darkey (teddbug-S)",
    author_email="teddbug47@gmail.com",
    maintainer="Divine Darkey (teddbug-S)",
    maintainer_email="teddbug47@gmail.com",
    description="A simple package to hunt down file duplicates",
    long_description=long_description,
    description_content_type="text",
    long_description_content_type="text/markdown",
    url="https://github.com/teddbug-S/dupliCat",
    project_urls={
        "Issues": "https://github.com/teddbug-S/dupliCat/issues",
        "Pull Requests": "https://github.com/teddbug-S/dupliCat/pulls"
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.6",
    requires=["click"],
    entry_points={
        'console_scripts': [
            'dupliCat = dupliCat.__main__:main',
        ]
    }
)
