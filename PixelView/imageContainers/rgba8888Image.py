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
import pUtils
from PIL import Image
from PixelView.imageContainers.abstractImage import AbstractImage


class Rgba8888Image(AbstractImage):

    def __init__(self, data=bytearray(), width=0, height=0):
        super().__init__(data, width, height)
        self.bytesPerPixel = 4
        self.mode = 'RGBA'

    def save(self, filePath):
        header = str.encode('rgba8888 ' + str(self.width) + ' ' + str(self.height) + chr(0x0A))
        pUtils.quickFileWrite(filePath, header + self.data, 'wb')

    def savePNG(self, filePath):
        img = Image.frombytes('RGBA', (self.width, self.height), self.data)
        img.save(filePath, 'PNG')

    def load(self, filePath, data=None):
        if data is None:
            data = pUtils.quickFileRead(filePath, 'rb')

        index = data.find(b'\x0A')
        header = data[:index]
        body = data[index + 1:]

        # Sample string to match: rgba8888 320 240
        t = re.match(b'rgba8888 ([\x30-\x39]+) ([\x30-\x39]+)', header)
        if t is None:
            raise Exception('Invalid header for a rgba8888 file type')
        self.width = int(t.group(1))
        self.height = int(t.group(2))
        self.data = bytearray(body)
        self.srcFilePath = filePath
        self.srcFileFormat = 'RGBA8888'
