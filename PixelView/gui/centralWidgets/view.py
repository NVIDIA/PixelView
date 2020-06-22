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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PixelView.utils.other import truncateString
from PixelView.utils.threading import OneShotThread
from PixelView.utils.image import loadImage, widgetDisplayImage


class View(QWidget):
    def __init__(self, configManager, parent=None, **kwargs):
        super(View, self).__init__(parent)
        self.cm = configManager
        self.initLayout()
        self.initLoadingIndicator()

    def initInfoLayout(self):
        layout = QVBoxLayout()
        self.counterLabel = QLabel()
        layout.addWidget(self.counterLabel, alignment=Qt.AlignHCenter | Qt.AlignTop)
        return layout

    def initLayout(self):
        layout = QVBoxLayout()
        layout.addLayout(self.initInfoLayout())

        self.imageLabel = QLabel()
        self.imageLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.imagePathLabel = QLabel()
        imageLayout = QVBoxLayout()
        imageLayout.addWidget(self.imageLabel)
        imageLayout.addWidget(self.imagePathLabel, alignment=Qt.AlignRight | Qt.AlignTop)

        layout.addLayout(imageLayout)
        self.setLayout(layout)

    def initLoadingIndicator(self):
        self.loadingIndicator = self.cm.getLoadingIndicatorClass()(parent=self, configManager=self.cm)

    def updateInfo(self):
        self.counterLabel.setText('%i of %i' % (self.index + 1, self.totalImageSets))
        self.imagePathLabel.setText(truncateString(self.imagePath, self.img.width))

    def loading(self):
        img = loadImage(self.imagePath, self.cm.getNullColor())
        returnData = dict(img=img)
        return returnData

    def draw(self, imagePath1, index, totalImageSets, **kwargs):
        self.imagePath = imagePath1
        self.index = index
        self.totalImageSets = totalImageSets

        self.loadingThread = OneShotThread(oneShotFunc=self.loading)
        self.loadingThread.start()

        self.loadingIndicator.start(isDoneFunc=lambda: not self.loadingThread.isAlive(),
                                    postFunc=self.drawPart2)

    def drawPart2(self):
        data = self.loadingThread.returnData
        self.img = data.get('img')

        self.updateInfo()
        widgetDisplayImage(self.imageLabel, data.get('img'))
