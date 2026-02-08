from setuptools import setup, find_packages

setup(
    name="py2mcu",
    version="0.1.0",
    description="Python to MCU C compiler with automatic memory management",
    author="py2mcu Contributors",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'py2mcu=py2mcu.cli:main',
        ],
    },
    python_requires='>=3.8',
)
