from setuptools import setup, find_packages
import io

# Read long description from README file with explicit encoding
with io.open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fluttercraft",
    version="0.1.2.dev0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all]",
        "pyfiglet",
        "colorama",
        "rich",
    ],
    entry_points="""
        [console_scripts]
        fluttercraft=fluttercraft.main:app
    """,
    python_requires=">=3.10",
    author="UTTAM-VAGHASIA",
    description="Automate your Flutter app setup like a pro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UTTAM-VAGHASIA/fluttercraft",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
) 