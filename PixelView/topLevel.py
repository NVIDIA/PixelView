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


import os
import pUtils
from PixelView.utils.image import loadImage
from PixelView.utils.cli import pprint, COLOR
from PixelView.gui.mainWindow import launch, MAIN_WINDOW_MODE
from PixelView.imageContainers.rgb888Image import Rgb888Image
from PixelView.imageContainers.rgba8888Image import Rgba8888Image

VERSION = '.01'


def version(**kwargs):
    pprint('Version: ', color=COLOR.TEAL, endLine=False); pprint(VERSION)


def info(filePath, **kwargs):
    try:
        img = loadImage(filePath)
    except IOError as e:
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('[I/O] ({0}): {1}'.format(e.errno, e.strerror))
        exit(1)
    except Exception:
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('Unsupported image format')
        exit(1)

    pprint('-----------------------------------')
    pprint('srcFileName:   ' + os.path.basename(img.srcFilePath))
    pprint('mode:          ' + img.mode)
    pprint('size:          ' + str(img.width) + 'x' + str(img.height))
    pprint('srcFileFormat: ' + img.srcFileFormat)
    pprint('-----------------------------------')


def printVal(filePath, x, y, **kwargs):
    try:
        img = loadImage(filePath)
    except IOError as e:
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('[I/O] ({0}): {1}'.format(e.errno, e.strerror))
        exit(1)
    except Exception:
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('Unsupported image format')
        exit(1)

    start = (img.width * y + x) * img.bytesPerPixel
    pprint(pUtils.formatHex(img.data[start:start + img.bytesPerPixel]))


def genCanvas(outFilePath, red, green, blue, width, height, alpha, **kwargs):

    if os.path.exists(outFilePath):
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('File:')
        pprint('    %s' % outFilePath, color=COLOR.TEAL)
        pprint('Already exists')
        exit(1)

    if alpha is None:
        img = Rgb888Image(bytearray([red, green, blue] * width * height), width, height)
    else:
        img = Rgba8888Image(bytearray([red, green, blue, alpha] * width * height), width, height)

    img.save(outFilePath)
    pprint('DONE', color=COLOR.TEAL)


def genConfig(dirPath, configManager, **kwargs):
    pUtils.createDirectory(os.path.abspath(dirPath))

    filePath = os.path.join(dirPath, 'config1.json')
    if configManager.saveFullConfig(filePath) != 0:
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('File: %s already exists' % filePath)
        exit(1)

    filePath = os.path.join(dirPath, 'configMenu.json')
    if configManager.genMenuConfigFile(filePath, configName='config1', configPath='config1.json'):
        pprint('Error: ', color=COLOR.RED, endLine=False); pprint('File: %s already exists' % filePath)
        exit(1)

    pprint('DONE', color=COLOR.TEAL)


def setConfigStart(filePath, configManager, **kwargs):
    configManager.setConfigStart(filePath)


def clearConfigStart(configManager, **kwargs):
    configManager.clearConfigStart()


def view(filePathList, configManager, **kwargs):
    launch(configManager, filePathList, mode=MAIN_WINDOW_MODE.VIEW, **kwargs)


def compare(filePathList1, filePathList2, fList, configManager, **kwargs):
    launch(configManager, filePathList1, filePathList2, mode=MAIN_WINDOW_MODE.COMPARE, **kwargs)
