from setuptools import setup

setup(
    name='PARSEC',
    url='https://github.com/jgkawell/parsec',
    author='Jack Kawell',
    author_email='jack.kawell@outlook.com',
    packages=['parsec'],
    install_requires=[
        'pyyaml==5.3',
        'numpy==1.16.6',
        'nltk==3.4.5'
    ],
    version='0.1',
    license='MIT',
    description='A Python implementation of the PARSEC (Plan Augmentation and Repair through SEmantic Constraints) algorithm',
    long_description=open('README.md').read(),
)
