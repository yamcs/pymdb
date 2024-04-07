import io

import setuptools

with io.open("README.md", encoding="utf-8") as f:
    readme = f.read()

setuptools.setup(
    name="yamcs-pymdb",
    version="1.0.5",
    description="Generate XTCE for use with Yamcs",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/yamcs/pymdb",
    author="Space Applications Services",
    author_email="yamcs@spaceapplications.com",
    license="LGPL",
    packages=setuptools.find_namespace_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords=["packet telemetry ccsds xtce yamcs"],
    platforms="Posix; MacOS X; Windows",
    include_package_data=True,
    zip_safe=False,
)
