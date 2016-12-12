#ifndef __IKAMATCHER2_KERNEL_HAL_H__
#define __IKAMATCHER2_KERNEL_HAL_H__

#include <Python.h>
#include <stdint.h>

struct HAL_METHODS {
  PyObject* (*encode)(const uint8_t*, uint32_t);
  PyObject* (*decode)(const uint8_t*, uint32_t);
  uint32_t (*logical_and_popcount)(const uint8_t*, const uint8_t*, uint32_t);
  uint32_t (*logical_or_popcount)(const uint8_t*, const uint8_t*, uint32_t);
};

#endif
