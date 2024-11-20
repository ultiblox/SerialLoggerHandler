from setuptools import setup, find_packages

setup(
    name="SerialLoggerHandler",
    version="1.0.0",
    description="A Python module for managing serial communication with Arduino devices.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pyserial"
    ],
)