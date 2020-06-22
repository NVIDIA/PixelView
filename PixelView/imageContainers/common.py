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


import re
import enum


@enum.unique
class COMPARE_TYPE(enum.Enum):

    # Alpha component is ignored if present
    ALPHALESS = 1

    # The alpha component from the first image is used as a bitmask
    # If the alpha is 255 the corresponding pixel is compared normally
    # Otherwise the corresponding pixel is excluded from the comparison
    ALPHA_HI1 = 2

    # The alpha component from the second image is used as a bitmask
    # If the alpha is 255 the corresponding pixel is compared normally
    # Otherwise the corresponding pixel is excluded from the comparison
    ALPHA_HI2 = 3

    # The alpha component from the first image is used as a bitmask
    # If the alpha is 0 the corresponding pixel is excluded from the comparison
    # Otherwise the corresponding pixel is compared normally
    ALPHA_LO1 = 4

    # The alpha component from the second image is used as a bitmask
    # If the alpha is 0 the corresponding pixel is excluded from the comparison
    # Otherwise the corresponding pixel is compared normally
    ALPHA_LO2 = 5

    # Compares color channels as well as the alpha channel
    # A difference of value for a pixel in the alpha channel is enough to deem
    # the result of the comparison as 2 different images
    # images without alpha can be compared like this as well
    # (For such case being equivalent of "ALPHALESS"
    # Alpha in one image and no alpha on the other is considered a difference
    FULL = 6


class Geometry:
    def __init__(self, data=0, y=0, width=0, height=0):
        if isinstance(data, Geometry):
            self.x = data.x
            self.y = data.y
            self.width = data.width
            self.height = data.height
            return

        if isinstance(data, int):
            self.x = data
            self.y = y
            self.width = width
            self.height = height
            return

        if isinstance(data, str):
            # Sample string to match: 320x240+0+0
            t = re.match(r'([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+)', data)
            if t:
                self.x = int(t.group(3))
                self.y = int(t.group(4))
                self.width  = int(t.group(1))
                self.height = int(t.group(2))
                return

    def __str__(self):
        return ','.join([str(item) for item in [self.x, self.y, self.width, self.height]])

    def __eq__(self, other):
        if other is None: return False
        return (self.__dict__ == other.__dict__)

    def isAreaEqual(self, other):
        return (self.width  == other.width and
                self.height == other.height)
