from setuptools import setup

with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

setup(
    name='ig_dl',
    version='0.1',
    license='MIT',
    author="famgz",
    author_email='famgz@proton.me',
    packages=['ig_dl'],
    package_dir={'ig_dl': 'src/ig_dl'},
    url='https://github.com/famgz/ig-dl',
    install_requires=REQUIREMENTS
)
