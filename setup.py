from setuptools import setup, find_packages

setup(
    name="rysolv_monitor",
    version="0.0.1",
    description="Monitor rysolv new issue",
    long_description="rtfm",
    url="https://github.com/manslaughter03/rysolv-monitor",
    author="b4nks@protonmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-telegram-bot==13.1",
        "requests==2.25.1",
        "pymongo==3.11.2"
    ]
)
