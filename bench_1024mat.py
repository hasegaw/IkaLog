from ikalog.utils.ikamatcher2.reference import Numpy_uint8, Numpy_uint8_fast
from ikalog.utils.ikamatcher2.arm_neon import NEON
import numpy as np
import time

def generate_img():
    img1 = np.random.randint(2, size=(1024, 1024))
    img2 = np.array(img1, dtype=np.uint8)
    return img2



def test(kernel):
    img_mask = generate_img()
    img_test = generate_img()

    a = kernel(1024, 1024)
    a.load_mask(img_mask)

    t1 = time.time()
    for i in range(100):
        img_test_encoded = a.encode(img_test)
    t2 = time.time()
    for i in range(100):
        a.logical_and_popcnt(img_test_encoded)
        a.logical_or_popcnt(img_test_encoded)
    t3 = time.time()

    print('encode %0.9fs logical_and_popcnt %0.9fs total %0.9fs %s' % (t2 - t1, t3 - t2, t3 - t1, kernel))

#test(Numpy_uint8)
#test(Numpy_uint8_fast)
test(NEON)

