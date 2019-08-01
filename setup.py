from setuptools import setup, find_packages

setup(
    name='socioFetcher',
    version='0.1.0',
    license='TBD',
    description='Socio-economic data fetcher',

    author='Tian Xie',
    author_email='xie@semcog.org',
    url='https://semcog.org',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=[
        "requests>=2.21.0",
        'pytest>=5.0.1',
        "pandas>=0.23.4",
        "tqdm>=4.32.0",
        "ipyleaflet>=0.11.0"
        "ipywidgets>=7.5.0",
        "sphinx>=2.1.2"
    ],
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'tasks = tasks.cli:tasks_cli',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
