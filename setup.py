from setuptools import setup

setup(
    name='app',
    version='0.0.1',
    package_dir={
        "": "sss"
    },
    install_requires=[
        'boto3',
    ],
)