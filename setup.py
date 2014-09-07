#!/usr/bin/env python
from setuptools import setup, Extension

# for CWB >= 3.0
extra_libs = ['pcre', 'glib-2.0']


def read(fname):
    return open(fname).read()

setup(
    name='cwb-python',
    description='CQP and CL interfaces for Python',
    author='Yannick Versley / Jorg Asmussen / Stefan Evert',
    version='0.1b',
    ext_modules=[Extension('CWB.CL', ['src/CWB/CL.cpp'],
                           include_dirs=['src'],
                           libraries=['cl'] + extra_libs),
                 ],
    py_modules=['PyCQP_interface'],
    packages=['CWB', 'CWB.tools'],
    long_description=read('README'),
    entry_points={
        'console_scripts': [
            'cqp2conll = CWB.tools.cqp2conll:main',
            'cqp_bitext = CWB.tools.make_bitext:main',
            'cqp_vocab = CWB.tools.cqp2vocab:cqp2vocab_main'
        ]},
    package_dir={'': 'py_src'})
