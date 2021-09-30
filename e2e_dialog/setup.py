import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="e2e_dialog",
    version="0.0.1",
    author="Yam",
    author_email="haoshaochun@gmail.com",
    description="Humanly Deeplearning NLP.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hscspring",
    packages=['e2e_dialog.damd', 'e2e_dialog.simpletod'],
    package_dir={},
    install_requires=[
    ],
    package_data={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
