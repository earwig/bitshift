from setuptools import setup, find_packages

setup(
    name = "bitshift",
    version = "0.1.dev",
    packages = find_packages(),
    install_requires = [
        "Flask>=0.10.1", "gunicorn>=18.0", "pygments>=1.6", "requests>=2.2.0",
        "beautifulsoup4>=3.2.1", "oursql>=0.9.3.1", "mmh3>=2.3",
        "PyYAML>=3.11", "python-dateutil>=2.2"],
    author = "Benjamin Attal, Ben Kurtovic, Severyn Kozak",
    license = "MIT",
    url = "https://github.com/earwig/bitshift"
)
