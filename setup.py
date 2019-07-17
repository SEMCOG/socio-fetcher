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

    install_requires=['pytest', 'pytest-mock', "pandas"],
    tests_require=['pytest', 'pytest-mock'],
    #extras_require={'mongo': 'pymongo'},

    entry_points={
        'console_scripts': [
            'tasks = tasks.cli:tasks_cli',
        ]
    },
)
