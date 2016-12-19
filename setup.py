from setuptools import setup, find_packages

setup(
    name="Text analysis service",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "goose-extractor==1.0.25",
        "falcon==1.1.0",
        "beautifulsoup4==4.5.1"
    ],
    test_suite="nose.collector",
    tests_require=[
        "nose==1.3.7"
    ],
    entry_points = {
        'console_scripts': ['tas-cli=tas.cli:main'],
    }
)
