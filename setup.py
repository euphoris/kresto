try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='kresto',
    packages=['kresto'],
    description='a personal chrestomathy manager',
    author='Jae-Myoung Yu',
    author_email='euphoris@gmail.com',
    maintainer='Jae-Myoung Yu',
    maintainer_email='euphoris@gmail.com',
    url='https://github.com/euphoris/kresto',
    tests_require=['pytest'],
    install_requires=[
        'numpy>=1.8.0',
        'nltk>=2.0.4',
        'html2text==3.200.3',
        'pdfminer==20131113',
        'sqlalchemy>=0.9',
    ],
    entry_points={
        'console_scripts': [
            'kresto = kresto.scripts:run_command',
        ]
    },
)