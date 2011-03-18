import os
from setuptools import setup, find_packages

from lbtagging import VERSION


f = open(os.path.join(os.path.dirname(__file__), 'README.txt'))
readme = f.read()
f.close()

setup(
    name='django-lbtagging',
    version=".".join(map(str, VERSION)),
    description='django-lbtagging is a reusable Django application for simple tagging.',
    long_description=readme,
    author='Alex Gaynor',
    author_email='alex.gaynor@gmail.com',
    url='http://github.com/alex/django-lbtagging/tree/master',
    packages=find_packages(),
    zip_safe=False,
    package_data = {
        'lbtagging': [
            'locale/*/LC_MESSAGES/*',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    test_suite='lbtagging.tests.runtests.runtests'
)

