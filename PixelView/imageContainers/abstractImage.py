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
from copy import deepcopy
from .common import Geometry, COMPARE_TYPE


class AbstractImage(object):
    def __init__(self, data, width, height):
        self.data = bytearray(data)

        self.width = width
        self.height = height
        self.mode = None
        self.srcFilePath = None
        self.srcFileFormat = None

    def getImageInfo(self):
        t = deepcopy(self.__dict__)
        t.pop('data')
        return t

    def getImageName(self):
        if self.filePath: return os.path.basename(self.filePath)
        return None

    def validateGeometry(self, geometry):
        return (geometry.width  + geometry.x <= self.width and
                geometry.height + geometry.y <= self.height)

    def getDiff(self, other, geometry1=None, geometry2=None, stopOnDiff=False, compareType=COMPARE_TYPE.FULL, returnFailPixelList=False, colorDict=None):
        """
        Compares two images: self vs other

        Args:
            other: image object to compare (against self)
            geometry1: The rectangular area within the 'self' image to compare
            geometry2: The rectangular area within the 'other' image to compare
            stopOnDiff: If True, return as soon as the first pixel difference is detected.
                        If False, continue comparing the image until the end
            compareType: What type of comparison to perform for details see the
                         COMPARE_TYPE enum above
            returnFailPixelList: If true, return a list with information for every pixel
                                 that was found different in the comparison.
                                 If false, don't return nor collect this data.
            colorDict: A dictionary with the colors to use for the deltaImages.

        Returns:
            A dictionary that always has the item 'isDiff', and additional data depending
            the case.
            If the areas of the images within its respective geometries are equal, then
            isDiff=False if not isdiff=True.
            Also if the geometries are invalid (e.g. the area specified by the geometry is
             beyond the image) or the geometries does not have the same area, then
            isDiff=True.

            The following items are included in the return dictionary if the image
            comparison reaches the end:

                'deltaImageRgbData':   Delta image for the RGB channels
                'deltaImageAlphaData': Delta image for the alpha channel
                'img1AlphaData':       Image for the alpha channel of the 'self' image
                'img2AlphaData':       Image for the alpha channel of the 'other' image

                'pixelDiffCount':     How may pixels were different
                'absDiffCount':       The sum of the differences per channel of every pixel comapred
                'maxChannelDelta':    The max difference found in a channel
                'diffPixelRgbList':   The list of pixels that were different for the RGB channels
                'diffPixelAlphaList': The list of pixels that were different for the alpha channel
        """
        if geometry1 is None:
            geometry1 = Geometry(0, 0, self.width, self.height)
        else:
            geometry1 = Geometry(geometry1)

        if geometry2 is None:
            geometry2 = Geometry(0, 0, other.width, other.height)
        else:
            geometry2 = Geometry(geometry2)

        if not geometry1.isAreaEqual(geometry2):
            return {'isDiff': True, 'debugData': {'msg': 'Geometry mismatch', 'geometry1': str(geometry1), 'geometry2': str(geometry2)}}

        if (not self.validateGeometry(geometry1) or not other.validateGeometry(geometry2)):
            return {'isDiff': True, 'debugData': {'msg': 'Invalid geometry',
                                                  'geometry1': str(geometry1), 'geometry2': str(geometry2),
                                                  'width1': str(self.width), 'width2': str(other.width),
                                                  'height1': str(self.height), 'height2': str(other.height)}}

        if (((compareType is COMPARE_TYPE.ALPHA_HI1 or compareType is COMPARE_TYPE.ALPHA_LO1) and self.bytesPerPixel != 4) or
            ((compareType is COMPARE_TYPE.ALPHA_HI2 or compareType is COMPARE_TYPE.ALPHA_LO2) and other.bytesPerPixel != 4)):
            return {'isDiff': True, 'debugData': {'msg': 'Invalid image format and comparison type combo',
                                                  'compareType': str(compareType),
                                                  'bytesPerPixel1': self.bytesPerPixel, 'bytesPerPixel2': other.bytesPerPixel}}

        flagCompareAlpha = False
        if compareType is COMPARE_TYPE.FULL:
            if (self.bytesPerPixel == 4)  != (other.bytesPerPixel == 4): return {'isDiff': True}
            if (self.bytesPerPixel == 4) and (other.bytesPerPixel == 4): flagCompareAlpha = True

        deltaImageRgb   = bytearray(b'\x00\x00\x00' * geometry1.width * geometry1.height)
        deltaImageAlpha = bytearray(b'\x00\x00\x00' * geometry1.width * geometry1.height)
        img1Alpha       = bytearray(b'\x00\x00\x00' * geometry1.width * geometry1.height)
        img2Alpha       = bytearray(b'\x00\x00\x00' * geometry1.width * geometry1.height)

        maxChannelDelta = 0
        pixelDiffCount = 0     # Total pixels that differ
        absDiffCount = 0       # The sum of the absolute valuies of all bytes differences for all pixels
        absDiffCountPixel = 0  # The abs diff count of a single pixel
        diffPixelRgbList = []
        diffPixelAlphaList = []
        for j in range(0, geometry1.height):
            for i in range(0, geometry1.width):
                outputPixelIndex = (j * geometry1.width + i) * 3
                inputPixelIndex1 = ((j + geometry1.y) * self.width  + i + geometry1.x) * self.bytesPerPixel
                inputPixelIndex2 = ((j + geometry2.y) * other.width + i + geometry2.x) * other.bytesPerPixel

                if compareType is COMPARE_TYPE.ALPHA_HI1 and  self.data[inputPixelIndex1 + 3] != 0xFF: continue
                if compareType is COMPARE_TYPE.ALPHA_LO1 and  self.data[inputPixelIndex1 + 3] == 0x00: continue
                if compareType is COMPARE_TYPE.ALPHA_HI2 and other.data[inputPixelIndex2 + 3] != 0xFF: continue
                if compareType is COMPARE_TYPE.ALPHA_LO2 and other.data[inputPixelIndex2 + 3] == 0x00: continue

                absDiffCountPixelRed   = abs(self.data[inputPixelIndex1 + 0] - other.data[inputPixelIndex2 + 0])
                absDiffCountPixelGreen = abs(self.data[inputPixelIndex1 + 1] - other.data[inputPixelIndex2 + 1])
                absDiffCountPixelBlue  = abs(self.data[inputPixelIndex1 + 2] - other.data[inputPixelIndex2 + 2])

                absDiffCountPixel = absDiffCountPixelRed + absDiffCountPixelGreen + absDiffCountPixelBlue

                absDiffCountPixelAlpha = 0
                if flagCompareAlpha:
                    absDiffCountPixelAlpha = abs(self.data[inputPixelIndex1 + 3] - other.data[inputPixelIndex2 + 3])

                    img1Alpha[outputPixelIndex + 0] =  self.data[inputPixelIndex1 + 3]
                    img1Alpha[outputPixelIndex + 1] =  self.data[inputPixelIndex1 + 3]
                    img1Alpha[outputPixelIndex + 2] =  self.data[inputPixelIndex1 + 3]
                    img2Alpha[outputPixelIndex + 0] = other.data[inputPixelIndex2 + 3]
                    img2Alpha[outputPixelIndex + 1] = other.data[inputPixelIndex2 + 3]
                    img2Alpha[outputPixelIndex + 2] = other.data[inputPixelIndex2 + 3]

                maxChannelDelta = max(maxChannelDelta, absDiffCountPixelRed, absDiffCountPixelGreen, absDiffCountPixelBlue, absDiffCountPixelAlpha)
                absDiffCountPixel = absDiffCountPixelRed + absDiffCountPixelGreen + absDiffCountPixelBlue + absDiffCountPixelAlpha
                absDiffCount += absDiffCountPixel

                pixelDiffCountTmp = 0
                if (absDiffCountPixelRed > 0 or
                    absDiffCountPixelGreen > 0 or
                    absDiffCountPixelBlue > 0):

                    pixelDiffCountTmp = 1
                    t = max(absDiffCountPixelRed, absDiffCountPixelGreen, absDiffCountPixelBlue)

                    color = [0xFF, 0xFF, 0xFF]
                    if colorDict:
                        color = colorDict.get(str(t), colorDict.get('default', color))
                    deltaImageRgb[outputPixelIndex: outputPixelIndex + 3] = color

                    if returnFailPixelList:
                        diffPixelEntry = []
                        diffPixelEntry.append(inputPixelIndex1)
                        diffPixelEntry.append(inputPixelIndex2)
                        diffPixelRgbList.append(diffPixelEntry)

                if absDiffCountPixelAlpha > 0:
                    pixelDiffCountTmp = 1

                    t = absDiffCountPixelAlpha
                    color = [0xFF, 0xFF, 0xFF]
                    if colorDict:
                        color = colorDict.get(str(t), colorDict.get('default', color))
                    deltaImageAlpha[outputPixelIndex: outputPixelIndex + 3] = color

                    if returnFailPixelList:
                        diffPixelEntry = []
                        diffPixelEntry.append(inputPixelIndex1)
                        diffPixelEntry.append(inputPixelIndex2)
                        diffPixelAlphaList.append(diffPixelEntry)

                pixelDiffCount += pixelDiffCountTmp
                if stopOnDiff and pixelDiffCount > 0: return {'isDiff': True}

        returnDict = {'isDiff': pixelDiffCount != 0,
                      'deltaImageRgbData': (deltaImageRgb,   geometry1.width, geometry1.height),
                      'maxChannelDelta':   maxChannelDelta,
                      'pixelDiffCount':    pixelDiffCount,
                      'absDiffCount':      absDiffCount,
                      'diffPixelRgbList':  diffPixelRgbList,
                      'geometry1':         geometry1,
                      'geometry2':         geometry2}

        if flagCompareAlpha:
            alphaDict = {'deltaImageAlphaData': (deltaImageAlpha, geometry1.width, geometry1.height),
                         'img1AlphaData':       (img1Alpha,       geometry1.width, geometry1.height),
                         'img2AlphaData':       (img2Alpha,       geometry1.width, geometry1.height),
                         'diffPixelAlphaList': diffPixelAlphaList}

            returnDict.update(alphaDict)

        return returnDict
