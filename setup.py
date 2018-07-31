from setuptools import setup


setup(
    name="pytest-pdb",
    description='pytest plugin which adds pdb helper commands related to pytest.',
    long_description=open("README.rst").read(),
    license="MIT license",
    version='0.3.1',
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='https://github.com/fschulze/pytest-pdb',
    py_modules=["pytest_pdb"],
    entry_points={'pytest11': ['pytest_pdb = pytest_pdb']},
    install_requires=['pytest'],
    classifiers=[
        "Framework :: Pytest"])
