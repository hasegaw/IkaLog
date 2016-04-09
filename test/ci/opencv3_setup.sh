#!/bin/sh
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the 'License');
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an 'AS IS' BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

#  Designed for Ubuntu 12.

BASEDIR=$PWD

git clone https://github.com/Itseez/opencv.git
# git clone --depth 1 https://github.com/Itseez/opencv_contrib.git

rm -rf opencv/build
mkdir -p opencv/build

cd opencv/build

git checkout 3.1.0

# Fixme: hard-coded path
cmake \
 -D CMAKE_INSTALL_PREFIX=${BASEDIR}/local \
 -D BUILD_opencv_python2=OFF \
 -D BUILD_opencv_python3=ON \
 -D PYTHON3LIBS_VERSION_STRING=3.4m \
 -D PYTHON3_LIBRARY=/opt/python/3.4.2/lib/libpython3.4m.so \
 -D PYTHON3_LIBRARIES=/opt/python/3.4.2/lib/libpython3.4m.so \
 -D PYTHON3_EXECUTABLE=/home/travis/virtualenv/python3.4.2/bin/python \
 -D PYTHON3_INCLUDE_DIR=/home/travis/virtualenv/python3.4.2/include/python3.4m \
 -D CMAKE_BUILD_TYPE=RELEASE \
 -D WITH_CUDA=OFF -D WITH_OPENCL=OFF -D WITH_OPENNI=OFF -D BUILD_TESTS=OFF -D BUILD_DOCS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF -D WITH_VTK=OFF -D WITH_1394=OFF ..

make -j 8 || exit 1
make install || exit 1

CV2PATH=`find ${BASEDIR}/local | grep '\/cv2'`
PYTHONPATH=`dirname ${CV2PATH}`
echo "export PYTHONPATH=$BASEDIR/ikalog:${PYTHONPATH}" > ${BASEDIR}/env.sh

exit 0
