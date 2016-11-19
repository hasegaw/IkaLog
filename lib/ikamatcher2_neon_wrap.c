#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

// http://docs.python.jp/3/howto/cporting.html

#include <Python.h>
#include "numpy/arrayobject.h"

#include <stdint.h>
//#include "ikamatcher_c.h"
#include "ikamatcher2_neon_hal.h"

struct module_state {
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static PyObject*
IkaMatcher2_encode_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *dest_pyobj, *src_pyobj;
  char *dest, *src;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;
  int nd = 1; //number_of_dimensions

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &dest_pyobj, 
              &PyArray_Type, &src_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &dest_pyobj, (void *)&dest, dims, nd, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &src_pyobj, (void *)&src, dims, nd, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  IkaMatcher2_encode(dest, src, pixels);

  return PyArray_Return(dest_pyobj);
}

static PyObject*
logical_and_popcount_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_and_popcount(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_and_popcount_neon_128_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_and_popcount_neon_128(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_and_popcount_neon_256_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_and_popcount_neon_256(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_and_popcount_neon_512_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_and_popcount_neon_512(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_or_popcount_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_or_popcount(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_or_popcount_neon_128_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_or_popcount_neon_128(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_or_popcount_neon_256_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_or_popcount_neon_256(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyObject*
logical_or_popcount_neon_512_wrap(PyObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj, *mask_pyobj;
  char *image, *mask;
  PyArray_Descr *descr;
  npy_intp dims[1];
  int pixels;

  if (!PyArg_ParseTuple(args, "O!O!i", 
              &PyArray_Type, &image_pyobj, 
              &PyArray_Type, &mask_pyobj,
              &pixels)){
      return NULL;
  }

  descr = PyArray_DescrFromType(NPY_UINT8);

  if (PyArray_AsCArray((PyObject **) &image_pyobj, (void *)&image, dims, 1, descr) < 0 ||
          PyArray_AsCArray((PyObject **) &mask_pyobj, (void *)&mask, dims, 1, descr) < 0) {
      PyErr_SetString(PyExc_TypeError, "error converting to c array");
      return NULL;
  }
  
  uint32_t popcnt = logical_or_popcount_neon_512(image, mask, pixels);

  return Py_BuildValue("i", popcnt);
}


static PyMethodDef IkaMatcher2methods[] = {
  {"encode", IkaMatcher2_encode_wrap, METH_VARARGS},
  {"logical_and_popcount", logical_and_popcount_wrap, METH_VARARGS},
  {"logical_and_popcount_neon_128", logical_and_popcount_neon_128_wrap, METH_VARARGS},
  {"logical_and_popcount_neon_256", logical_and_popcount_neon_256_wrap, METH_VARARGS},
  {"logical_and_popcount_neon_512", logical_and_popcount_neon_512_wrap, METH_VARARGS},
  {"logical_or_popcount", logical_or_popcount_wrap, METH_VARARGS},
  {"logical_or_popcount_neon_128", logical_or_popcount_neon_128_wrap, METH_VARARGS},
  {"logical_or_popcount_neon_256", logical_or_popcount_neon_256_wrap, METH_VARARGS},
  {"logical_or_popcount_neon_512", logical_or_popcount_neon_512_wrap, METH_VARARGS},
  {NULL}, // sentinel
};

static int ikamatcher2_neon_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int ikamatcher2_neon_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "ikamatcher2_neon_hal",
        NULL,
        sizeof(struct module_state),
        IkaMatcher2methods,
        NULL,
        ikamatcher2_neon_traverse,
        ikamatcher2_neon_clear,
        NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_ikamatcher2_neon_hal(void)
{
    PyObject *module = PyModule_Create(&moduledef);

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("ikamatcher2_neon_hal.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    import_array();

    return PyModule_Create(&moduledef);
}
