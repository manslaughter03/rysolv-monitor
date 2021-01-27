from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rysolv_monitor",
    version="0.0.2",
    description="Monitor rysolv new issue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manslaughter03/rysolv-monitor",
    author="b4nks@protonmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(),
    include_package_data=True,
    # Static file not in package
    data_files=[('changelog', ["CHANGELOG.md"])],
    install_requires=[
        "python-telegram-bot==13.1",
        "requests==2.25.1",
        "pymongo==3.11.2"
    ]
)
