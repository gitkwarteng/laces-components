from setuptools import setup, find_packages

setup(
    name='components',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'Django>=4.0',
        'laces>=0.1.2',
    ],
    author='Antwi Kwarteng',
    description='Reusable Django components for building web applications',
    python_requires='>=3.8',
)
