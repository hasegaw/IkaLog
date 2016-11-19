#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>

//#include "ikamatcher_c.h"

#include <arm_neon.h>

int IkaMatcher2_encode(char *dest, char *src, int pixels)
{   
    uint8x16_t mask0 = (uint8x16_t)vdupq_n_u64(0x8040201008040201);
    uint8x16_t mask1 = mask0;
    uint8x16_t mask2 = mask0;
    uint8x16_t mask3 = mask0;

    for (uint32_t i = 0; i < pixels; i += 128){
        // convert 255:0 -> 1:0
        // load 128-pixel
        uint8x16_t input0 = vld1q_u8(src + i);
        uint8x16_t input1 = vld1q_u8(src + i + 16);
        uint8x16_t input2 = vld1q_u8(src + i + 32);
        uint8x16_t input3 = vld1q_u8(src + i + 48);
        uint8x16_t input4 = vld1q_u8(src + i + 64);
        uint8x16_t input5 = vld1q_u8(src + i + 80);
        uint8x16_t input6 = vld1q_u8(src + i + 96);
        uint8x16_t input7 = vld1q_u8(src + i + 112);
        
        // compress
        uint64x2_t c0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input0, mask0))));
        uint64x2_t c1 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input1, mask1))));
        uint64x2_t c2 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input2, mask2))));
        uint64x2_t c3 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input3, mask3))));
        uint64x2_t c4 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input4, mask0))));
        uint64x2_t c5 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input5, mask1))));
        uint64x2_t c6 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input6, mask2))));
        uint64x2_t c7 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vandq_u8(input7, mask3))));

        // collect
        uint8x8x2_t zip8_0 = vzip_u8((uint8x8_t)vget_low_u64(c0), (uint8x8_t)vget_high_u64(c0));
        uint8x8x2_t zip8_1 = vzip_u8((uint8x8_t)vget_low_u64(c1), (uint8x8_t)vget_high_u64(c1));
        uint8x8x2_t zip8_2 = vzip_u8((uint8x8_t)vget_low_u64(c2), (uint8x8_t)vget_high_u64(c2));
        uint8x8x2_t zip8_3 = vzip_u8((uint8x8_t)vget_low_u64(c3), (uint8x8_t)vget_high_u64(c3));
        uint8x8x2_t zip8_4 = vzip_u8((uint8x8_t)vget_low_u64(c4), (uint8x8_t)vget_high_u64(c4));
        uint8x8x2_t zip8_5 = vzip_u8((uint8x8_t)vget_low_u64(c5), (uint8x8_t)vget_high_u64(c5));
        uint8x8x2_t zip8_6 = vzip_u8((uint8x8_t)vget_low_u64(c6), (uint8x8_t)vget_high_u64(c6));
        uint8x8x2_t zip8_7 = vzip_u8((uint8x8_t)vget_low_u64(c7), (uint8x8_t)vget_high_u64(c7));

        uint16x4x2_t zip16_0 = vzip_u16((uint16x4_t)zip8_0.val[0], (uint16x4_t)zip8_1.val[0]);
        uint16x4x2_t zip16_1 = vzip_u16((uint16x4_t)zip8_2.val[0], (uint16x4_t)zip8_3.val[0]);
        uint16x4x2_t zip16_2 = vzip_u16((uint16x4_t)zip8_4.val[0], (uint16x4_t)zip8_5.val[0]);
        uint16x4x2_t zip16_3 = vzip_u16((uint16x4_t)zip8_6.val[0], (uint16x4_t)zip8_7.val[0]);
        
        uint32x2x2_t zip32_0 = vzip_u32((uint32x2_t)zip16_0.val[0], (uint32x2_t)zip16_1.val[0]);
        uint32x2x2_t zip32_1 = vzip_u32((uint32x2_t)zip16_2.val[0], (uint32x2_t)zip16_3.val[0]);
        
        uint32x2_t low =  zip32_0.val[0];
        uint32x2_t high =  zip32_1.val[0];

        uint32x4_t u128 = vcombine_u32(low, high);

        vst1q_u32((uint32_t *)(dest + (i / 8)), u128);
    }
}

/* http://www.nminoru.jp/~nminoru/programming/bitcount.html */

uint8_t popcount_table[256] = {
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8,
};


uint32_t popcount(uint32_t t) {
    uint32_t popcnt = 0;
    popcnt += popcount_table[t & 0xff];
    t >>= 8;
    popcnt += popcount_table[t & 0xff];
    t >>= 8;
    popcnt += popcount_table[t & 0xff];
    t >>= 8;
    popcnt += popcount_table[t & 0xff];
    t >>= 8;
    return popcnt;
}


int IkaMatcher2_popcnt128_sw(char *src, int pixels) {
    uint32_t *s = (uint32_t *) src;
    int r = 0;

    while (pixels >= 32) {
        r += popcount(*s);
        s += 1;
        pixels -= 32;
    }
    return r;
}

/**
 * @brief AND masking and popcount function
 * 
 * @description 
 * @param[in] image image
 * @param[in] mask mask
 * @param[in] pixels image size(X * Y pixel)
 * @return popcount value
 */
uint32_t logical_and_popcount(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    uint32_t *image_u32 = (uint32_t *)image;
    uint32_t *mask_u32 = (uint32_t *)mask;
    uint32_t popcnt = 0;
    pixels = pixels / 8;
#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (uint32_t i = 0; i < (pixels / sizeof(uint32_t)); i+=4) {
        // process 128bit at once
        uint32_t tmp0 = image_u32[i + 0] & mask_u32[i + 0]; 
        uint32_t tmp1 = image_u32[i + 1] & mask_u32[i + 1];
        uint32_t tmp2 = image_u32[i + 2] & mask_u32[i + 2];
        uint32_t tmp3 = image_u32[i + 3] & mask_u32[i + 3];
        uint32_t popcnt0 = popcount(tmp0);
        uint32_t popcnt1 = popcount(tmp1);
        uint32_t popcnt2 = popcount(tmp2);
        uint32_t popcnt3 = popcount(tmp3);
#ifdef _OPENMP
    #pragma omp atomic
#endif
        popcnt += popcnt3 + popcnt2 + popcnt1 + popcnt0;
    }
    return popcnt;
}


/**
 * @brief neon version AND masking and popcount function
 * 
 * @description 
 * @param[in] image image
 * @param[in] mask mask
 * @param[in] pixels image size(X * Y pixel)
 * @return popcount value
 */
uint32_t logical_and_popcount_neon_128(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    uint64x2_t popcnt0 = {0};
    pixels = pixels / 8;
    for (uint32_t i = 0; i < pixels; i+=(16 * 1)) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));

        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img0, msk0)))));
        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
    }

    uint64x1_t popcnt_neon = vadd_u64(vget_low_u64(popcnt0), vget_high_u64(popcnt0));
    uint32_t popcnt = vget_lane_u32((uint32x2_t)popcnt_neon, 0);
    return popcnt;
}

uint32_t logical_and_popcount_neon_256(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    uint64x2_t popcnt0 = {0};
    uint64x2_t popcnt1 = {0};
    pixels = pixels / 8;

    uint32_t pre = pixels % (16 * 2); // get 16 or 0
    pixels = pixels - pre;
    for (uint32_t i = 0; i < pre; i+=16) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img0, msk0)))));
        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
    }

    for (uint32_t i = pre; i < pixels; i+=(16 * 2)) {
        // process 256bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        uint8x16_t img1 = vld1q_u8((image + i + 16));
        uint8x16_t msk1 = vld1q_u8((mask + i + 16));

        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img0, msk0)))));
        uint64x2_t popcnt_tmp1 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img1, msk1)))));

        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
        popcnt1 = vaddq_u64(popcnt1, popcnt_tmp1);
    }
    uint64x1_t popcnt_sum0 = vadd_u64(vget_low_u64(popcnt0), vget_high_u64(popcnt0));
    uint64x1_t popcnt_sum1 = vadd_u64(vget_low_u64(popcnt1), vget_high_u64(popcnt1));
    uint64x1_t popcnt_neon = vadd_u64(popcnt_sum0, popcnt_sum1);
    uint32_t popcnt = vget_lane_u32((uint32x2_t)popcnt_neon, 0);
    return popcnt;
}

uint32_t logical_and_popcount_neon_512(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    uint64x2_t popcnt0 = {0};
    uint64x2_t popcnt1 = {0};
    uint64x2_t popcnt2 = {0};
    uint64x2_t popcnt3 = {0};
    pixels = pixels / 8;

    uint32_t pre = pixels % (16 * 2); // get 16 or 0
    pixels = pixels - pre;
    for (uint32_t i = 0; i < pre; i+=16) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img0, msk0)))));
        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
    }

    for (uint32_t i = pre; i < pixels; i+=(16 * 4)) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        uint8x16_t img1 = vld1q_u8((image + i + 16));
        uint8x16_t msk1 = vld1q_u8((mask + i + 16));
        uint8x16_t img2 = vld1q_u8((image + i + 32));
        uint8x16_t msk2 = vld1q_u8((mask + i + 32));
        uint8x16_t img3 = vld1q_u8((image + i + 48));
        uint8x16_t msk3 = vld1q_u8((mask + i + 48));

        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img0, msk0)))));
        uint64x2_t popcnt_tmp1 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img1, msk1)))));
        uint64x2_t popcnt_tmp2 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img2, msk2)))));
        uint64x2_t popcnt_tmp3 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vandq_u8(img3, msk3)))));

        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
        popcnt1 = vaddq_u64(popcnt1, popcnt_tmp1);
        popcnt2 = vaddq_u64(popcnt2, popcnt_tmp2);
        popcnt3 = vaddq_u64(popcnt3, popcnt_tmp3);
    }
    uint64x1_t popcnt_sum0 = vadd_u64(vget_low_u64(popcnt0), vget_high_u64(popcnt0));
    uint64x1_t popcnt_sum1 = vadd_u64(vget_low_u64(popcnt1), vget_high_u64(popcnt1));
    uint64x1_t popcnt_sum2 = vadd_u64(vget_low_u64(popcnt2), vget_high_u64(popcnt2));
    uint64x1_t popcnt_sum3 = vadd_u64(vget_low_u64(popcnt3), vget_high_u64(popcnt3));
    uint64x1_t popcnt_sum01 = vadd_u64(popcnt_sum0, popcnt_sum1);
    uint64x1_t popcnt_sum23 = vadd_u64(popcnt_sum2, popcnt_sum3); 
    uint64x1_t popcnt_neon = vadd_u64(popcnt_sum01, popcnt_sum23);

    uint32_t popcnt = vget_lane_u32((uint32x2_t)popcnt_neon, 0);
    return popcnt;
}



/**
 * @brief OR masking and popcount function
 * 
 * @description 
 * @param[in] image image
 * @param[in] mask mask
 * @param[in] pixels image size(X * Y pixel)
 * @return popcount value
 */
uint32_t logical_or_popcount(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    uint32_t *image_u32 = (uint32_t *)image;
    uint32_t *mask_u32 = (uint32_t *)mask;
    uint32_t popcnt = 0;
    pixels = pixels / 8;

#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (uint32_t i = 0; i < (pixels / sizeof(uint32_t)); i+=4) {
        // process 128bit at once
        uint32_t tmp0 = image_u32[i + 0] | mask_u32[i + 0]; 
        uint32_t tmp1 = image_u32[i + 1] | mask_u32[i + 1];
        uint32_t tmp2 = image_u32[i + 2] | mask_u32[i + 2];
        uint32_t tmp3 = image_u32[i + 3] | mask_u32[i + 3];
        uint32_t popcnt0 = popcount(tmp0);
        uint32_t popcnt1 = popcount(tmp1);
        uint32_t popcnt2 = popcount(tmp2);
        uint32_t popcnt3 = popcount(tmp3);
#ifdef _OPENMP
    #pragma omp atomic
#endif
        popcnt += popcnt3 + popcnt2 + popcnt1 + popcnt0;
    }
    return popcnt;
}


/**
 * @brief neon version OR masking and popcount function
 * 
 * @description 
 * @param[in] image image
 * @param[in] mask mask
 * @param[in] pixels image size(X * Y pixel)
 * @return popcount value
 */
uint32_t logical_or_popcount_neon_128(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    uint64x2_t popcnt0 = {0};
    pixels = pixels / 8;
    for (uint32_t i = 0; i < pixels; i+=(16 * 1)) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));

        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img0, msk0)))));
        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
    }

    uint64x1_t popcnt_neon = vadd_u64(vget_low_u64(popcnt0), vget_high_u64(popcnt0));
    uint32_t popcnt = vget_lane_u32((uint32x2_t)popcnt_neon, 0);
    return popcnt;
}

uint32_t logical_or_popcount_neon_256(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    pixels /= 8;
    uint64x2_t popcnt0 = {0};
    uint64x2_t popcnt1 = {0};


    uint32_t pre = pixels % (16 * 2); // get 16 or 0
    pixels = pixels - pre;
    for (uint32_t i = 0; i < pre; i+=16) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img0, msk0)))));
        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
    }

    for (uint32_t i = pre; i < pixels; i+=(16 * 2)) {
        // process 256bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        uint8x16_t img1 = vld1q_u8((image + i + 16));
        uint8x16_t msk1 = vld1q_u8((mask + i + 16));

        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img0, msk0)))));
        uint64x2_t popcnt_tmp1 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img1, msk1)))));

        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
        popcnt1 = vaddq_u64(popcnt1, popcnt_tmp1);
    }
    uint64x1_t popcnt_sum0 = vadd_u64(vget_low_u64(popcnt0), vget_high_u64(popcnt0));
    uint64x1_t popcnt_sum1 = vadd_u64(vget_low_u64(popcnt1), vget_high_u64(popcnt1));
    uint64x1_t popcnt_neon = vadd_u64(popcnt_sum0, popcnt_sum1);
    uint32_t popcnt = vget_lane_u32((uint32x2_t)popcnt_neon, 0);
    return popcnt;
}

uint32_t logical_or_popcount_neon_512(uint8_t *image, uint8_t *mask, uint32_t pixels)
{
    pixels /= 8;
    uint64x2_t popcnt0 = {0};
    uint64x2_t popcnt1 = {0};
    uint64x2_t popcnt2 = {0};
    uint64x2_t popcnt3 = {0};

    uint32_t pre = pixels % (16 * 2); // get 16 or 0
    pixels = pixels - pre;
    for (uint32_t i = 0; i < pre; i+=16) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img0, msk0)))));
        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
    }

    for (uint32_t i = pre; i < pixels; i+=(16 * 4)) {
        // process 128bit at once
        // load
        uint8x16_t img0 = vld1q_u8((image + i));
        uint8x16_t msk0 = vld1q_u8((mask + i));
        uint8x16_t img1 = vld1q_u8((image + i + 16));
        uint8x16_t msk1 = vld1q_u8((mask + i + 16));
        uint8x16_t img2 = vld1q_u8((image + i + 32));
        uint8x16_t msk2 = vld1q_u8((mask + i + 32));
        uint8x16_t img3 = vld1q_u8((image + i + 48));
        uint8x16_t msk3 = vld1q_u8((mask + i + 48));

        // AND mask and popcnt
        uint64x2_t popcnt_tmp0 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img0, msk0)))));
        uint64x2_t popcnt_tmp1 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img1, msk1)))));
        uint64x2_t popcnt_tmp2 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img2, msk2)))));
        uint64x2_t popcnt_tmp3 = vpaddlq_u32(vpaddlq_u16(vpaddlq_u8(vcntq_u8(vorrq_u8(img3, msk3)))));

        // sum
        popcnt0 = vaddq_u64(popcnt0, popcnt_tmp0);
        popcnt1 = vaddq_u64(popcnt1, popcnt_tmp1);
        popcnt2 = vaddq_u64(popcnt2, popcnt_tmp2);
        popcnt3 = vaddq_u64(popcnt3, popcnt_tmp3);
    }
    uint64x1_t popcnt_sum0 = vadd_u64(vget_low_u64(popcnt0), vget_high_u64(popcnt0));
    uint64x1_t popcnt_sum1 = vadd_u64(vget_low_u64(popcnt1), vget_high_u64(popcnt1));
    uint64x1_t popcnt_sum2 = vadd_u64(vget_low_u64(popcnt2), vget_high_u64(popcnt2));
    uint64x1_t popcnt_sum3 = vadd_u64(vget_low_u64(popcnt3), vget_high_u64(popcnt3));
    uint64x1_t popcnt_sum01 = vadd_u64(popcnt_sum0, popcnt_sum1);
    uint64x1_t popcnt_sum23 = vadd_u64(popcnt_sum2, popcnt_sum3); 
    uint64x1_t popcnt_neon = vadd_u64(popcnt_sum01, popcnt_sum23);

    uint32_t popcnt = vget_lane_u32((uint32x2_t)popcnt_neon, 0);
    return popcnt;
}

/* test junk code */
int main() {
    uint8_t src[720][1280];
    uint8_t dest[720][1280 / 8];

    int pixels = 1280 * 720;
    IkaMatcher2_encode((char *)&dest, (char *)&src, pixels);    
    
    printf("unsigned long long = %lu\n", sizeof(unsigned long long));
}

