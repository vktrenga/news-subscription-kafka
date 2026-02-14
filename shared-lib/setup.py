from setuptools import setup, find_packages

setup(
    name="shared_lib",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "psycopg2-binary"
    ],
)
