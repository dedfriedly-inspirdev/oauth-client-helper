import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oauth-client-helper", # Replace with your own username
    version="0.2.0",
    author="Dedric Friedly",
    author_email="dedric.friedly@inspiredev-llc.com",
    description="A slightly silly implementation of an OAuth authorization web helper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)