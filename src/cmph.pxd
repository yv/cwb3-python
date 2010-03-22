cdef extern from "Python.h":
  ctypedef int Py_ssize_t
  int PyString_Check(object o)
  Py_ssize_t PyString_Size(object string)
  char* PyString_AsString(object string)

cdef extern from "stdio.h":
  struct FILE
  FILE *fopen(char *fname, char *mode)
  void fclose(FILE *)

cdef extern from "cmph.h":
  struct cmph_t
  cmph_t *cmph_load(FILE *f)
  void cmph_destroy(cmph_t *mphf)
  int cmph_search(cmph_t *, char *, int)

cdef class CMPH:
  cdef cmph_t *hash_ptr
  cdef FILE *f
