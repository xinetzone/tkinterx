import setuptools


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="tkinterx",  # Replace with your own username
    version="0.0.8",
    author="Xinwei Liu",
    author_email="735613050@qq.com",
    description="Use tkinter to create a handy GUI tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xinetzone/pychaos",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.7',
)

