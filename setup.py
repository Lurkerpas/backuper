from setuptools import find_packages, setup

setup(
    name="backuper",
    version="0.1.0",
    description="Console backup utility",
    packages=find_packages(include=["backuper", "backuper.*"]),
    include_package_data=True,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "backuper = backuper.cli:main",
        ],
    },
)
