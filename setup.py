#!/usr/bin/env python
from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext as _build_ext
from distutils.dep_util import newer
import sys
import os.path

try:
    from Cython.Compiler.Main import CompilationOptions, \
        default_options as pyrex_default_options, \
        compile as cython_compile
    def compile_cython(sdir,fname,out_fname):
        old_dir=os.getcwd()
        os.chdir(sdir)
        if newer(fname,out_fname):
            print >>sys.stderr, "Cython %s => %s"%(fname,out_fname)
            options=CompilationOptions(pyrex_default_options,
                                       output_file=out_fname,
                                       cplus=True)
            result=cython_compile(fname,options)
            if result.num_errors!=0:
                raise ValueError,'Compilation failed!'
        os.chdir(old_dir)
except ImportError:
    def compile_cython(sdir,fname,out_fname):
        """dummy function that takes the existing .cpp"""
        pass

class build_ext(_build_ext):
    def swig_sources (self, sources, extension):
        """runs bison/flex for BisonModule/FlexModule sources"""
        sources=_build_ext.swig_sources(self,sources,extension)
        bison_sources=[source for source in sources if source.endswith('.y')]
        flex_sources=[source for source in sources if source.endswith('.l')]
        cython_sources=[source for source in sources if source.endswith('.pyx')]
        other_sources=[source for source in sources if not (
            source.endswith('.y') or source.endswith('.l') or
            source.endswith('.pyx'))]
        for source in cython_sources:
            source_dirname=os.path.dirname(source)
            source_basename=os.path.basename(source)
            c_source=replace_suffix(source,'.c')
            c_source_basename=os.path.basename(c_source)
            compile_cython(source_dirname,source_basename,c_source_basename)
            other_sources.append(c_source)
        return other_sources

def replace_suffix(path, new_suffix):
    return os.path.splitext(path)[0] + new_suffix


setup(name='cwb-python',
      description='CQP and CL interfaces for Python',
      author='Yannick Versley / Jorg Asmussen',
      version='0.1',
      cmdclass={'build_ext':build_ext},
      ext_modules=[Extension('CWB.CL',['src/CL.pyx'],
                             libraries=['cl']),
                   Extension('cmph',['src/cmph.pyx'],
                             libraries=['cmph'])
                   ],
      py_modules=['PyCQP_interface'],
      packages=['CWB'])
