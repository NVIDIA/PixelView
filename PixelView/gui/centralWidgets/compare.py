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


from copy import deepcopy
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QMessageBox
from PixelView.utils.other import truncateString
from PixelView.utils.threading import OneShotThread
from PixelView.utils.image import loadImage, widgetDisplayImage, getAlphaImage
from PixelView.imageContainers.common import COMPARE_TYPE
from PixelView.imageContainers.rgb888Image import Rgb888Image


class Compare(QWidget):
    def __init__(self, configManager, geometry1=None, geometry2=None, parent=None, **kwargs):
        super(Compare, self).__init__(parent)

        self.cm = configManager
        self.geometry1 = geometry1
        self.geometry2 = geometry2

        self.initVars()
        self.initLayout()
        self.initLoadingIndicator()

    def initVars(self):
        self.pixelIndex1 = 0
        self.pixelIndex2 = 0
        self.pixelDiffIndex = -1

    def initPixelInfoLayout(self):
        layout = QGridLayout()
        layout.setColumnStretch(3, 9)
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(20)

        self.pixelXY1Label = QLabel()
        self.pixelXY2Label = QLabel()
        self.pixelIndex1Label = QLabel()
        self.pixelIndex2Label = QLabel()
        self.pixelColor1Label = QLabel()
        self.pixelColor2Label = QLabel()

        layout.addWidget(self.pixelXY1Label,    0, 0, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.pixelXY2Label,    1, 0, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.pixelIndex1Label, 0, 1, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.pixelIndex2Label, 1, 1, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.pixelColor1Label, 0, 2, alignment=Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.pixelColor2Label, 1, 2, alignment=Qt.AlignLeft | Qt.AlignTop)

        return layout

    def initDifferencesInfoLayout(self):
        layout = QGridLayout()
        self.differentPixelsTotalLabel = QLabel()
        layout.addWidget(self.differentPixelsTotalLabel, 0, 0, alignment=Qt.AlignRight | Qt.AlignBottom)
        return layout

    def initInfoLayout(self):
        layout = QVBoxLayout()

        headerLayout = QHBoxLayout()
        self.counterLabel = QLabel()
        headerLayout.addWidget(self.counterLabel, alignment=Qt.AlignHCenter | Qt.AlignTop)

        bodyLayout = QHBoxLayout()
        bodyLayout.addLayout(self.initPixelInfoLayout())
        bodyLayout.addLayout(self.initDifferencesInfoLayout())

        layout.addLayout(headerLayout)
        layout.addLayout(bodyLayout)
        return layout

    def initImagesLayout(self):
        def initSubLayout(imageLabel, imagePathLabel):
            subLayout = QGridLayout()
            subLayout.setColumnStretch(1, 9)
            subLayout.addWidget(imageLabel, 0, 0)
            subLayout.addWidget(imagePathLabel, 1, 0, 1, 2, alignment=Qt.AlignRight | Qt.AlignTop)
            return subLayout

        layout = QGridLayout()
        self.imageLabelList = []
        for i in range(6):
            tLabel = QLabel()
            tLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.imageLabelList.append(tLabel)

        self.imagePath1Label = QLabel()
        self.imagePath2Label = QLabel()
        self.differentPixelsRgbLabel = QLabel()
        self.differentPixelsAlphaLabel = QLabel()

        subLayout = initSubLayout(self.imageLabelList[0], self.imagePath1Label)
        layout.addLayout(subLayout, 0, 0, alignment=Qt.AlignHCenter | Qt.AlignTop)

        subLayout = initSubLayout(self.imageLabelList[1], self.imagePath2Label)
        layout.addLayout(subLayout, 0, 1, alignment=Qt.AlignHCenter | Qt.AlignTop)

        subLayout = initSubLayout(self.imageLabelList[2], self.differentPixelsRgbLabel)
        layout.addLayout(subLayout, 0, 2, alignment=Qt.AlignHCenter | Qt.AlignTop)

        layout.addWidget(self.imageLabelList[3], 1, 0, alignment=Qt.AlignHCenter | Qt.AlignTop)

        layout.addWidget(self.imageLabelList[4], 1, 1, alignment=Qt.AlignHCenter | Qt.AlignTop)

        subLayout = initSubLayout(self.imageLabelList[5], self.differentPixelsAlphaLabel)
        layout.addLayout(subLayout, 1, 2, alignment=Qt.AlignHCenter | Qt.AlignTop)

        return layout

    def initLayout(self):
        layout = QVBoxLayout()
        layout.addLayout(self.initInfoLayout())
        layout.addLayout(self.initImagesLayout())
        self.setLayout(layout)

    def initLoadingIndicator(self):
        self.loadingIndicator = self.cm.getLoadingIndicatorClass()(parent=self, configManager=self.cm)

    def pixelIndexToXY(self, pixelIndex, bytesPerPixel, width):
        t = pixelIndex / bytesPerPixel
        y = int(t / width)
        x = int(t % width)
        return (x, y)

    def updateMarker(self):
        t = deepcopy(self.diffData['deltaImageRgbData'])
        img3 = Rgb888Image(*t)

        ### Calculate the pixel index for the subImage ###
        x, y = self.pixelIndexToXY(self.pixelIndex1, self.img1.bytesPerPixel, self.img1.width)
        x0 = x - self.geometry1.x
        y0 = y - self.geometry1.y
        indexTmp = (self.geometry1.width * y0 + x0) * 3
        ##################################################

        img3.data[indexTmp: indexTmp + 3] = self.cm.getMarkerColor()
        widgetDisplayImage(self.imageLabelList[2], img3)

    def updateInfo(self):
        def genHexFormatString(bytesPerPixel):
            return '[%02X' + (':%02X' * (bytesPerPixel - 1)) + ']'

        self.counterLabel.setText('%i of %i' % (self.index + 1, self.totalImageSets))

        ### Pixel Info ###
        if self.pixelDiffIndex == -1:
            pixelXY1String    = 'PixelXY1: '    + '    '
            pixelXY2String    = 'PixelXY2: '    + '    '
            pixelIndex1String = 'PixelIndex1: ' + '    '
            pixelIndex2String = 'PixelIndex2: ' + '    '
            pixelColor1String = 'PixelColor1: ' + '    '
            pixelColor2String = 'PixelColor1: ' + '    '
        else:
            pixel1Data = self.img1.data[self.pixelIndex1:self.pixelIndex1 + self.img1.bytesPerPixel]
            pixel2Data = self.img2.data[self.pixelIndex2:self.pixelIndex2 + self.img2.bytesPerPixel]

            pixelXY1String    = 'PixelXY1: '    + '%i,%i' % self.pixelIndexToXY(self.pixelIndex1, self.img1.bytesPerPixel, self.img1.width)
            pixelXY2String    = 'PixelXY2: '    + '%i,%i' % self.pixelIndexToXY(self.pixelIndex2, self.img2.bytesPerPixel, self.img2.width)
            pixelIndex1String = 'PixelIndex1: ' + str(self.pixelIndex1) + ' (in bytes)'
            pixelIndex2String = 'PixelIndex2: ' + str(self.pixelIndex2) + ' (in bytes)'
            pixelColor1String = 'PixelColor1: ' + genHexFormatString(self.img1.bytesPerPixel) % tuple(pixel1Data)
            pixelColor2String = 'PixelColor2: ' + genHexFormatString(self.img2.bytesPerPixel) % tuple(pixel2Data)

        self.pixelXY1Label.setText(pixelXY1String)
        self.pixelXY2Label.setText(pixelXY2String)
        self.pixelIndex1Label.setText(pixelIndex1String)
        self.pixelIndex2Label.setText(pixelIndex2String)
        self.pixelColor1Label.setText(pixelColor1String)
        self.pixelColor2Label.setText(pixelColor2String)
        ##################

        ### Different Pixels Counts ###
        differentPixelsTotal = self.diffData.get('pixelDiffCount')
        differentPixelsRgb   = self.diffData.get('diffPixelRgbList')
        differentPixelsAlpha = self.diffData.get('diffPixelAlphaList')
        differentPixelsTotalString = str(differentPixelsTotal) if differentPixelsTotal is not None else 'UNAVAILABLE'
        differentPixelsRgbString   = str(len(differentPixelsRgb)) if differentPixelsRgb is not None else 'UNAVAILABLE'
        differentPixelsAlphaString = str(len(differentPixelsAlpha)) if differentPixelsAlpha is not None else 'UNAVAILABLE'
        self.differentPixelsTotalLabel.setText('Different Pixels Total: '   + differentPixelsTotalString)
        self.differentPixelsRgbLabel.setText(  'Different Pixels (RGB): '   + differentPixelsRgbString)
        self.differentPixelsAlphaLabel.setText('Different Pixels (Alpha): ' + differentPixelsAlphaString)
        ###############################

        ### Image Paths ###
        self.imagePath1Label.setText(truncateString(self.imagePath1, self.img1.width))
        self.imagePath2Label.setText(truncateString(self.imagePath2, self.img2.width))
        ###################

    def nextDiffPixel(self):
        t = self.diffData.get('diffPixelRgbList')
        if t is None or len(t) == 0: return

        self.pixelDiffIndex += 1
        self.pixelDiffIndex = min(self.pixelDiffIndex, len(self.diffData['diffPixelRgbList']) - 1)

        self.pixelIndex1 = self.diffData['diffPixelRgbList'][self.pixelDiffIndex][0]
        self.pixelIndex2 = self.diffData['diffPixelRgbList'][self.pixelDiffIndex][1]

        self.updateInfo()
        self.updateMarker()

    def prevDiffPixel(self):
        t = self.diffData.get('diffPixelRgbList')
        if t is None or len(t) == 0: return

        self.pixelDiffIndex -= 1
        self.pixelDiffIndex = max(self.pixelDiffIndex, 0)

        self.pixelIndex1 = self.diffData['diffPixelRgbList'][self.pixelDiffIndex][0]
        self.pixelIndex2 = self.diffData['diffPixelRgbList'][self.pixelDiffIndex][1]

        self.updateInfo()
        self.updateMarker()

    def loading(self):
        nullImageData = None

        def genNullImageData(refImg):
            if nullImageData: return nullImageData
            return [bytearray(self.cm.getNullColor() * refImg.width * refImg.height), refImg.width, refImg.height]

        img1 = loadImage(self.imagePath1, self.cm.getNullColor())
        img2 = loadImage(self.imagePath2, self.cm.getNullColor())

        nullImageData1 = genNullImageData(img1)
        nullImageData2 = genNullImageData(img2)
        img4 = getAlphaImage(img1)
        img5 = getAlphaImage(img2)
        if img4 is None: img4 = nullImageData1
        if img5 is None: img5 = nullImageData2

        if img1.srcFileFormat == 'nullImage' or img2.srcFileFormat == 'nullImage':
            data = {}
            img3 = None
            img6 = None
        else:
            data = img1.getDiff(img2, compareType=COMPARE_TYPE.FULL,
                                returnFailPixelList=True, colorDict=self.cm.getDeltaImageColorDict(),
                                geometry1=self.geometry1, geometry2=self.geometry2)

            self.geometry1 = data.get('geometry1', self.geometry1)
            self.geometry2 = data.get('geometry2', self.geometry2)

            img3 = Rgb888Image(*data.get('deltaImageRgbData', nullImageData1))
            img6 = Rgb888Image(*data.get('deltaImageAlphaData', nullImageData1))

        returnData = dict(img1=img1,
                          img2=img2,
                          img3=img3,
                          img4=img4,
                          img5=img5,
                          img6=img6,
                          diffData=data)
        return returnData

    def draw(self, imagePath1, imagePath2, index, totalImageSets, **kwargs):
        self.imagePath1 = imagePath1
        self.imagePath2 = imagePath2
        self.index = index
        self.totalImageSets = totalImageSets

        self.loadingThread = OneShotThread(oneShotFunc=self.loading)
        self.loadingThread.start()

        self.loadingIndicator.start(isDoneFunc=lambda: not self.loadingThread.isAlive(),
                                    postFunc=self.drawPart2)

    def drawPart2(self):
        data = self.loadingThread.returnData

        self.initVars()
        self.img1 = data.get('img1')
        self.img2 = data.get('img2')
        self.diffData = data.get('diffData')

        img3 = data.get('img3')
        img4 = data.get('img4')
        img5 = data.get('img5')
        img6 = data.get('img6')

        self.updateInfo()
        widgetDisplayImage(self.imageLabelList[0], self.img1)
        widgetDisplayImage(self.imageLabelList[1], self.img2)
        widgetDisplayImage(self.imageLabelList[3],      img4)
        widgetDisplayImage(self.imageLabelList[4],      img5)

        widgetList = [
            self.imageLabelList[2],
            self.imageLabelList[5],
            self.differentPixelsTotalLabel,
            self.differentPixelsRgbLabel,
            self.differentPixelsAlphaLabel,
        ]

        if img3 is None or img6 is None:
            for widget in widgetList:
                func = getattr(widget, 'hide')
                func()
        else:
            widgetDisplayImage(self.imageLabelList[2], img3)
            widgetDisplayImage(self.imageLabelList[5], img6)

            for widget in widgetList:
                func = getattr(widget, 'show')
                func()

        if self.img1.srcFileFormat == 'nullImage' or self.img2.srcFileFormat == 'nullImage':
            msgBox = QMessageBox(self)
            msgBox.setText('Unable to load the current image pair')
            msgBox.setInformativeText('Go to the next image pair to continue reviewing the images')
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
