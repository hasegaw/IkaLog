#pragma once

#include <stdint.h>

void IkaMatcher2_encode(char *dest, char *src, int pixels);
uint32_t logical_and_popcount(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_and_popcount_neon_128(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_and_popcount_neon_256(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_and_popcount_neon_512(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_or_popcount(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_or_popcount_neon_128(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_or_popcount_neon_256(uint8_t *image, uint8_t *mask, uint32_t pixels);
uint32_t logical_or_popcount_neon_512(uint8_t *image, uint8_t *mask, uint32_t pixels);
