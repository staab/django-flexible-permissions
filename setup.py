import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-flexible-permissions',
    version='1.0.3',
    packages=[
        'flexible_permissions',
        'flexible_permissions.migrations',
    ],
    include_package_data=True,
    license='MIT License',
    description=(
        "Django app that combines a permissions table with model "
        "relations to calculate complex object-level permissions."
    ),
    long_description=README,
    url='https://github.com/staab/django-flexible-permissions',
    author='Jon Staab',
    author_email='shtaab@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
