from setuptools import setup, find_packages

setup(
    name='components',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'Django>=4.0',
        'laces>=0.1.2',
        'django-widget-tweaks>=1.5.1',
    ],
    author='Antwi Kwarteng',
    description='Reusable Django components for building web applications',
    python_requires='>=3.8',
)
