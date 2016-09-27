# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)


def get_requirements(requirements_file):
    with open(requirements_file) as f:
        required = [line.split('#')[0] for line in f.read().splitlines()]
    return required


def extract_version():
    context = {}
    init_path = 'src/async_rest/__init__.py'
    with open(os.path.join(ROOT, init_path)) as fd:
        code = fd.read()
        exec(compile(code, init_path, "exec"), context)
    return context.get('__version__')


setup(
    name="django-async-rest",
    version=extract_version(),
    license='GPLv3',
    description="A RESTful way of dealing with asynchronous tasks",
    author='P.A. Schembri',
    author_email='pa.schembri@netsach.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Netsach/django-async-rest',
    include_package_data=True,
    install_requires=get_requirements(os.path.join(ROOT, 'requirements.txt'))
)
