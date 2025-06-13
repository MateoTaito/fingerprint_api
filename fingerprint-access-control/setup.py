from setuptools import setup, find_packages

setup(
    name='fingerprint-access-control',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A fingerprint access control system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/fingerprint-access-control',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pydbus',
        'gi',
        'flask',  # Add any other dependencies your project requires
        'sqlalchemy',
        'pydantic',
        'pytest',  # For testing
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)