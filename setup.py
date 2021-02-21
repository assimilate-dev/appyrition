import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="appyrition",
    version="0.0.9010",
    author="Michael Treadwell",
    author_email="mich@eltreadwell.com",
    packages=["appyrition"],
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/assimilate-dev/appyrition",
    license="mit",
    python_requires=">=3.9",
    install_requires=[
        "PyJWT>=2.0.0",
        "requests>=2.25.1",
        "Markdown>=3.3.3"
    ]
)
