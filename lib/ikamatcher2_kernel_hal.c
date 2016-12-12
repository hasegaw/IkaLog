#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

// http://docs.python.jp/3/howto/cporting.html

#include <Python.h>
#include "numpy/arrayobject.h"
#include <stdint.h>
#include "ikamatcher2_kernel_hal.h"

struct module_state {
    PyObject *error;
};

struct IkaMatHALObject {
  PyObject_HEAD
  uint32_t w, h;
  PyArrayObject* mask;
};

struct HAL_METHODS* hal;
struct HAL_METHODS* Kernel_init();

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static PyObject*
Ikamatcher2_hal_encode(struct IkaMatHALObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *src_pyobj;
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &src_pyobj)) {
     return NULL;
    }

    PyArrayObject* flat = (PyArrayObject*)PyArray_Ravel(src_pyobj, NPY_ANYORDER );
    if ( flat == NULL) {
      PyErr_SetString(PyExc_TypeError, "error converting to flat");
      return NULL;
    }
    PyObject* pyobj_dest = hal->encode(PyArray_BYTES(flat), PyArray_NBYTES(flat));

    Py_XDECREF(flat);
    return pyobj_dest;
}

static PyObject* Ikamatcher2_hal_decode(struct IkaMatHALObject* self, PyObject* args) {
  PyArrayObject *image_pyobj;

  if (!PyArg_ParseTuple(args,"O!", &PyArray_Type, &image_pyobj)) {
    return NULL;
  }

  PyObject* pyobj_dest = hal->decode(PyArray_BYTES(image_pyobj), PyArray_NBYTES(image_pyobj));
  return pyobj_dest;
}

static PyObject*
Ikamatcher2_hal_logical_and_popcount(struct IkaMatHALObject* self, PyObject* args)
{
  // get numpy.array([], numpy.uint8)
  PyArrayObject *image_pyobj;

  if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &image_pyobj)){
    return NULL;
  }

  uint32_t popcnt = hal->logical_and_popcount(PyArray_BYTES(image_pyobj), PyArray_BYTES(self->mask), self->w * self->h);

  return Py_BuildValue("i", popcnt);
}

static PyObject*
Ikamatcher2_hal_logical_or_popcount(struct IkaMatHALObject* self, PyObject* args)
{
  PyArrayObject *image_pyobj;

  if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &image_pyobj)){
      return NULL;
  }

  uint32_t popcnt = hal->logical_or_popcount(PyArray_BYTES(image_pyobj), PyArray_BYTES(self->mask), self->w * self->h );

  return Py_BuildValue("i", popcnt);
}

static PyObject* Ikamatcher2_hal_load_mask(struct IkaMatHALObject* self, PyObject* args) {
  PyArrayObject* mask_obj;

  if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &mask_obj)) {
    return Py_BuildValue("i",-1);
  }

  PyArrayObject* flat = (PyArrayObject*)PyArray_Flatten(mask_obj, NPY_CORDER);
  if ( flat == NULL) {
    PyErr_SetString(PyExc_TypeError, "error converting to flat");
    return Py_BuildValue("i",-1);
  }

  self->mask = (PyArrayObject*)hal->encode(PyArray_BYTES(flat), PyArray_NBYTES(flat));

  Py_XDECREF(flat);
  return Py_BuildValue("i",0);
}

static PyMethodDef IkaMatHAL_Methods[] = {
  {"encode", (PyCFunction)Ikamatcher2_hal_encode, METH_VARARGS},
  {"decode", (PyCFunction)Ikamatcher2_hal_decode, METH_VARARGS},
  {"load_mask", (PyCFunction)Ikamatcher2_hal_load_mask, METH_VARARGS},
  {"logical_and_popcnt", (PyCFunction)Ikamatcher2_hal_logical_and_popcount, METH_VARARGS},
  {"logical_or_popcnt", (PyCFunction)Ikamatcher2_hal_logical_or_popcount, METH_VARARGS},
  {NULL}, // sentinel
};

static void IkaMatHAL_dealloc(struct IkaMatHALObject* self) {
  Py_XDECREF(self->mask);
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* IkaMatHAL_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
  struct IkaMatHALObject* self;
  self = (struct IkaMatHALObject*)type->tp_alloc(type, 0);
  return (PyObject*)self;
}

static int IkaMatHAL_init(struct IkaMatHALObject* self, PyObject* args, PyObject* kwds) {
  static char*kwlist[] = {"width", "height", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "II", kwlist, &self->w, &self->h)) {
	  return -1;
  }

  return 0;
}

static PyTypeObject IkaMatHAL_type = {
  PyVarObject_HEAD_INIT(NULL,0)
  "ikamatcher2.HAL",
  sizeof(struct IkaMatHALObject),
  0,
  (destructor)IkaMatHAL_dealloc,
  0,                         /* tp_print */
  0,                         /* tp_getattr */
  0,                         /* tp_setattr */
  0,                         /* tp_reserved */
  0,                         /* tp_repr */
  0,                         /* tp_as_number */
  0,                         /* tp_as_sequence */
  0,                         /* tp_as_mapping */
  0,                         /* tp_hash  */
  0,                         /* tp_call */
  0,                         /* tp_str */
  0,                         /* tp_getattro */
  0,                         /* tp_setattro */
  0,                         /* tp_as_buffer */
      Py_TPFLAGS_DEFAULT |
  Py_TPFLAGS_BASETYPE,   /* tp_flags */
  "IkaMatcher HAL objects",           /* tp_doc */
  0,                         /* tp_traverse */
  0,                         /* tp_clear */
  0,                         /* tp_richcompare */
  0,                         /* tp_weaklistoffset */
  0,                         /* tp_iter */
  0,                         /* tp_iternext */
  IkaMatHAL_Methods,             /* tp_methods */
  0,             /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)IkaMatHAL_init,      /* tp_init */
  0,                         /* tp_alloc */
  IkaMatHAL_new,                 /* tp_new */
};

static struct PyModuleDef moduledef = {
  PyModuleDef_HEAD_INIT,
  "ikamatcher2_kernel_hal",
  "IkaMatcher2 HAL Wrapper",
  -1,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_ikamatcher2_kernel_hal(void)
{
  hal = Kernel_init();

  if(PyType_Ready(&IkaMatHAL_type) < 0) {
	return NULL;
  }

    PyObject *module = PyModule_Create(&moduledef);
	if (module == NULL) {
	  return NULL;
	}

	Py_INCREF(&IkaMatHAL_type);
	PyModule_AddObject(module, "HAL", (PyObject*)&IkaMatHAL_type);
	import_array();
	return module;
}
