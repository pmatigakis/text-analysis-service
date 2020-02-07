from setuptools import setup, find_packages


def get_requirements():
    with open("requirements.txt") as f:
        requirements = [
            line.strip()
            for line in f
            if not line.startswith("-e")
        ]

    return requirements


def get_test_requirements():
    with open("requirements-test.txt") as f:
        requirements = [
            line.strip()
            for line in f
        ]

    return requirements


setup(
    name="Text analysis service",
    version="0.10.3",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=get_requirements(),
    test_suite="nose.collector",
    tests_require=get_test_requirements(),
    entry_points={
        'console_scripts': ['tas-cli=tas.cli:main'],
    }
)
