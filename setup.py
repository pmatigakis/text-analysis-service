from setuptools import setup, find_packages

setup(
    name="Text analysis service",
    version="0.2.0",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "goose-extractor==1.0.25",
        "falcon==1.1.0",
        "beautifulsoup4==4.5.1",
        "opengraph==0.5",
        "uWSGI==2.0.14"
    ],
    test_suite="nose.collector",
    tests_require=[
        "nose==1.3.7",
        "requests==2.12.4",
        "mock==2.0.0"
    ],
    entry_points = {
        'console_scripts': ['tas-cli=tas.cli:main'],
    }
)
