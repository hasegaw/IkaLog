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

ls -l /opt/python/
ls -l /opt/python/3.?.?/lib/libpython*m.so
ls -l /opt/python/3.?.?/lib/libpython*m.so

PYTHON3_MAJOR_MINOR=3.4
PYTHON3_LIBRARY=`ls -1d /opt/python/${PYTHON3_MAJOR_MINOR}.?/lib/libpython?.?m.so`
PYTHON3_LIBRARIES=`ls -1d /opt/python/${PYTHON3_MAJOR_MINOR}.?/lib/libpython?.?m.so`
PYTHON3_EXECUTABLE=`ls -1d /home/travis/virtualenv/python${PYTHON3_MAJOR_MINOR}.?/bin/python`
PYTHON3_INCLUDE_DIR=`ls -1d /home/travis/virtualenv/python${PYTHON3_MAJOR_MINOR}.?/include/python?.?m`
VERSION_STRING_REGEXP="libpython([0-9]+\.[0-9]+m)\.so"
if [[ $PYTHON3_LIBRARY =~ $VERSION_STRING_REGEXP  ]]; then
    PYTHON3LIBS_VERSION_STRING=${BASH_REMATCH[1]}
else
    echo Failed to detect python version.
    exit 1
fi

cmake \
 -D CMAKE_INSTALL_PREFIX=${BASEDIR}/local \
 -D BUILD_opencv_python2=OFF \
 -D BUILD_opencv_python3=ON \
 -D PYTHON3LIBS_VERSION_STRING=$PYTHON3LIB_VERSION_STRING \
 -D PYTHON3_LIBRARY=$PYTHON3_LIBRARY \
 -D PYTHON3_LIBRARIES=$PYTHON3_LIBRARY \
 -D PYTHON3_EXECUTABLE=$PYTHON3_EXECUTABLE \
 -D PYTHON3_INCLUDE_DIR=$PYTHON3_INCLUDE_DIR \
 -D CMAKE_BUILD_TYPE=RELEASE \
 -D WITH_CUDA=OFF -D WITH_OPENCL=OFF -D WITH_OPENNI=OFF -D BUILD_TESTS=OFF -D BUILD_DOCS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF -D WITH_VTK=OFF -D WITH_1394=OFF ..

make -j 8 || exit 1
make install || exit 1

CV2PATH=`find ${BASEDIR}/local | grep '\/cv2'`
PYTHONPATH=`dirname ${CV2PATH}`
echo "export PYTHONPATH=$BASEDIR/ikalog:${PYTHONPATH}" > ${BASEDIR}/env.sh

exit 0
