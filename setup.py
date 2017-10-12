from setuptools import setup, find_packages

setup(
    name="Text analysis service",
    version="0.3.0",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "falcon==1.1.0",
        "beautifulsoup4==4.5.1",
        "python-consul==0.7.0",
        "gunicorn==19.7.1",
        "Sphinx==1.6.2",
        "newspaper3k==0.2.2",
        "statsd==3.2.1",
        "jsonschema==2.6.0"
    ],
    test_suite="nose.collector",
    tests_require=[
        "nose==1.3.7",
        "requests==2.12.4"
    ],
    entry_points = {
        'console_scripts': ['tas-cli=tas.cli:main'],
    }
)
