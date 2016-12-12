#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

// http://docs.python.jp/3/howto/cporting.html

#include <Python.h>
#include "numpy/arrayobject.h"

#include <stdint.h>
#include "ikamatcher2_kernel_hal.h"
#include "ikamatcher2_neon_hal.h"

#define ENCODE_SRC_ALIGN 128
#define ENCODE_DEST_ALIGN 64

static PyObject*
NEON_encode(const uint8_t* src, uint32_t src_size)
{
  // get numpy.array([], numpy.uint8)
  npy_intp dims[1];
  uint8_t *a_src, *a_dest;
  uint8_t need_free = 0;
  uint32_t a_src_size;
  uint32_t a_dest_size;

  a_src_size = src_size;
  a_src = (uint8_t*)src;
  if ((uint32_t)a_src_size & (ENCODE_SRC_ALIGN-1)) {
    a_src_size += (ENCODE_SRC_ALIGN - (a_src_size & (ENCODE_SRC_ALIGN-1)));
    a_src = aligned_alloc(ENCODE_SRC_ALIGN, a_src_size);
    if (a_src == NULL) {
      PyErr_SetString(PyExc_MemoryError, "not enough memory");
      return NULL;
    }
    memmove(a_src, src, a_src_size);
    memset(a_src + src_size, 0, a_src_size - src_size); // clear padding
    need_free = 1;
  }

  a_dest_size = a_src_size / 8;
  if (a_dest_size & (ENCODE_DEST_ALIGN-1)) {
    a_dest_size += (ENCODE_DEST_ALIGN - (a_dest_size & (ENCODE_DEST_ALIGN-1)));
  }

  a_dest = aligned_alloc(ENCODE_DEST_ALIGN, a_dest_size);

  if (a_dest == NULL) {
    PyErr_SetString(PyExc_MemoryError, "not enough memory");
    return NULL;
  }

  if (a_dest_size != a_src_size/8) {
    memset(a_dest+(a_src_size/8), 0, a_dest_size - (a_src_size/8)); // clear padding
  }

  IkaMatcher2_encode(a_dest, a_src, a_src_size);

  dims[0] = a_dest_size;
  PyArrayObject* pyobj_a_dest = (PyArrayObject*)PyArray_SimpleNewFromData(1, dims, NPY_UINT8, a_dest);
  if (pyobj_a_dest == NULL ) {
    PyErr_SetString(PyExc_TypeError,"error creating PyArrayObject");
    return NULL;
  }
  PyArray_UpdateFlags(pyobj_a_dest, NPY_ARRAY_OWNDATA);

  if (need_free) {
    free(a_src);
  }

  return (PyObject*)PyArray_Return(pyobj_a_dest);
}

static PyObject* NEON_decode(const uint8_t* sec, uint32_t src_size) {
  return (PyObject*)Py_None;
}

static uint32_t
NEON_logical_and_popcount(const uint8_t* img, const uint8_t* mask, uint32_t pixels)
{
  // TODO: image and mask buffer need rebuild aligned buffer?
  return logical_and_popcount_neon_512((uint8_t*)img, (uint8_t*)mask, pixels);
}

static uint32_t
NEON_logical_or_popcount(const uint8_t* img, const uint8_t* mask, uint32_t pixels)
{
  return logical_or_popcount_neon_512((uint8_t*)img, (uint8_t*)mask, pixels);
}

static struct HAL_METHODS methods = {
  NEON_encode,
  NEON_decode,
  NEON_logical_and_popcount,
  NEON_logical_or_popcount
};

struct HAL_METHODS* Kernel_init() {
  import_array();
  return &methods;
}
