#ifndef __PYX_HAVE__src__CWB__CL
#define __PYX_HAVE__src__CWB__CL


#ifndef __PYX_HAVE_API__src__CWB__CL

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyObject) *registry;

#endif /* !__PYX_HAVE_API__src__CWB__CL */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initCL(void);
#else
PyMODINIT_FUNC PyInit_CL(void);
#endif

#endif /* !__PYX_HAVE__src__CWB__CL */
