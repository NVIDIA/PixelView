# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pUtils
from PIL import Image
from io import BytesIO
from PySide2.QtGui import QImage, QPixmap
from PixelView.imageContainers.rgb888Image import Rgb888Image
from PixelView.imageContainers.rgba8888Image import Rgba8888Image


def loadImage(filePath, nullColor=None):

    def genPlaceHolder():
        # If we couldn't load  an image we generate a placeholder
        # This is necessary since we may be dealing with a list of images
        # and we can't just end the application when one 'unloadable' image
        # is found.
        # By generating a place holder instead, we allow the user to keep
        # reviewing the images on the list as well as indicating something
        # went wrong.

        width = 100
        height = 100
        t = Rgba8888Image(bytearray(nullColor + [0]) * width * height, width, height)
        t.srcFileFormat = 'nullImage'
        return t

    try:
        data = pUtils.quickFileRead(filePath, 'rb')
    except Exception:
        if nullColor: return genPlaceHolder()
        raise

    try:
        img = Rgba8888Image()
        img.load(filePath, data=data)
        return img
    except Exception: pass

    try:
        img = Rgb888Image()
        img.load(filePath, data=data)
        return img
    except Exception: pass

    try:
        img = Image.open(BytesIO(data))
    except Exception:
        raise Exception('Unable to identify image format')

    try:
        if img.format != 'PNG': raise Exception('Unsupported image format ' + img.format)

        width, height = img.size
        data = bytearray(img.tobytes())
        if img.mode == 'RGBA':
            t = Rgba8888Image(data, width, height)
        elif img.mode == 'RGB':
            t = Rgb888Image(data, width, height)
        else:
            raise Exception('Unknown Image mode')
        t.srcFilePath = filePath
        t.srcFileFormat = 'PNG'
        return t
    except Exception:
        if nullColor: return genPlaceHolder()
        raise


def dropAlpha(img):
    if isinstance(img, Rgb888Image):
        return img

    if isinstance(img, Rgba8888Image):
        data = img.data
        red   = data[0::4]
        green = data[1::4]
        blue  = data[2::4]

        newData = bytearray([0, 0, 0] * int(len(data) / 4))
        newData[0::3] = red
        newData[1::3] = green
        newData[2::3] = blue
        return Rgb888Image(newData, img.width, img.height)

    raise Exception('Invalid input parameter type')


def getAlphaImage(img):
    if isinstance(img, Rgb888Image):
        return None

    if isinstance(img, Rgba8888Image):
        data = img.data
        alpha = data[3::4]

        newData = bytearray([alpha[i // 3] for i in range(len(alpha) * 3)])
        return Rgb888Image(newData, img.width, img.height)

    raise Exception('Invalid input parameter type')


def widgetDisplayImage(widget, img):
    imgFormat = QImage.Format_RGB888

    img = dropAlpha(img)
    displayImage = QImage(img.data,
                          img.width, img.height,
                          imgFormat)

    displayImagePix = QPixmap.fromImage((displayImage))
    widget.setPixmap(displayImagePix)
