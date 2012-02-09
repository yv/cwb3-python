#include "cmph.h"

cdef class CMPH:
  def __init__(self,fname):
      cdef FILE *f=fopen(fname,"rb")
      self.f=f
      self.hash_ptr=cmph_load(f)
      if not self.hash_ptr:
          raise IOError("Cannot load "+fname)
  def __getitem__(self,key):
      if not PyString_Check(key):
          raise TypeError
      return cmph_search(self.hash_ptr, key, PyString_Size(key))
  def __destroy__(self):
      cmph_destroy(self.hash_ptr)
      fclose(self.f)
