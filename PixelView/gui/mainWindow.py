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
import enum
import pUtils
from PySide2.QtWidgets import QApplication, QMainWindow, QMenuBar, QAction, QMessageBox
from PixelView.gui.centralWidgets.view import View
from PixelView.gui.centralWidgets.compare import Compare


@enum.unique
class MAIN_WINDOW_MODE(enum.Enum):
    VIEW = 1
    COMPARE = 2


class MainWindow(QMainWindow):
    def __init__(self, parent=None, **kwargs):
        super(MainWindow, self).__init__(parent)

        self.initVars(**kwargs)

        self.resize(200, 200)
        self.move(0, 0)
        self.setWindowTitle('PixelView')
        self.initMenuBar()
        self.selectCentralWidget()

    def initVars(self, mode, configManager, **kwargs):
        self.cm = configManager
        self.imagePathList1 = []
        self.imagePathList2 = []

        self.droppedList1 = []
        self.droppedList2 = []

        self.index = 0
        self.pixelDiffIndex = None
        self.pixelIndex1 = 0
        self.pixelIndex2 = 0

        self.mode = mode
        self.centralWidgetDict = {
            MAIN_WINDOW_MODE.VIEW:    View(configManager=configManager, **kwargs),
            MAIN_WINDOW_MODE.COMPARE: Compare(configManager=configManager, **kwargs),
        }

    def initMenuBar(self, mode=None):
        if mode:
            self.mode = mode
        self.setMenuBar(self.createMenuBar())

    def selectCentralWidget(self, mode=None):
        if mode:
            self.mode = mode
        self.setCentralWidget(self.centralWidgetDict[self.mode])

    def dropImage(self):
        if len(self.imagePathList1) == 1: return
        self.droppedList1.append(self.imagePathList1.pop(self.index))
        if self.imagePathList2:
            self.droppedList2.append(self.imagePathList2.pop(self.index))
        if self.index >= len(self.imagePathList1):
            self.index = len(self.imagePathList1) - 1
        self.draw()

    def writeLists(self):
        def f(s):
            return os.path.abspath(os.path.realpath(s))

        d = dict(imagePathList1=[f(i) for i in self.imagePathList1],
                 imagePathList2=[f(i) for i in self.imagePathList2],
                 droppedPathList1=[f(i) for i in self.droppedList1],
                 droppedPathList2=[f(i) for i in self.droppedList2],)

        filePath = os.path.abspath(self.cm.getDumpFileName())
        try:
            if not os.path.exists(filePath):
                pUtils.quickFileWrite(filePath, d, 'json')
            else:
                msgBox = QMessageBox(self)
                msgBox.setText('File:\n    %s\nalready exists' % filePath)
                msgBox.setInformativeText('Do you want to overwrite it?')
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Cancel)
                ret = msgBox.exec_()
                if ret == QMessageBox.Yes:
                    pUtils.quickFileWrite(filePath, d, 'json')
        except Exception:
            msgBox = QMessageBox(self)
            msgBox.setText('Unable to write file:\n    %s' % filePath)
            msgBox.setInformativeText('Please make sure you have right access and space left')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()

    def prevImage(self):
        if self.index <= 0: return
        self.index = self.index - 1
        self.draw()

    def nextImage(self):
        if self.index >= len(self.imagePathList1) - 1: return
        self.index = self.index + 1
        self.draw()

    def createMenuBar(self):
        menuBar = QMenuBar(parent=None)

        # File Menu
        fileMenu = menuBar.addMenu('&File')

        dumpListsAction = QAction('Dump Lists', fileMenu)
        dumpListsAction.setShortcut('Ctrl+S')
        dumpListsAction.triggered.connect(self.writeLists)
        fileMenu.addAction(dumpListsAction)

        fileMenu.addSeparator()

        exitAction = QAction('E&xit', fileMenu)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QApplication.closeAllWindows)
        fileMenu.addAction(exitAction)

        # View Menu
        viewMenu = menuBar.addMenu('V&iew')

        t = ' pair' if self.mode == MAIN_WINDOW_MODE.COMPARE else ''

        nextImageAction = QAction('next image' + t, viewMenu)
        nextImageAction.setShortcut('Ctrl+]')
        nextImageAction.triggered.connect(self.nextImage)
        viewMenu.addAction(nextImageAction)

        prevImageAction = QAction('prev image' + t, viewMenu)
        prevImageAction.setShortcut('Ctrl+[')
        prevImageAction.triggered.connect(self.prevImage)
        viewMenu.addAction(prevImageAction)

        viewMenu.addSeparator()

        dropImageAction = QAction('Drop image' + t, viewMenu)
        dropImageAction.setShortcut('Ctrl+D')
        dropImageAction.triggered.connect(self.dropImage)
        viewMenu.addAction(dropImageAction)

        if self.mode == MAIN_WINDOW_MODE.COMPARE:
            viewMenu.addSeparator()

            nextDiffPixelAction = QAction('next diff pixel', viewMenu)
            nextDiffPixelAction.setShortcut('Ctrl+.')
            nextDiffPixelAction.triggered.connect(self.centralWidgetDict[MAIN_WINDOW_MODE.COMPARE].nextDiffPixel)
            viewMenu.addAction(nextDiffPixelAction)

            prevDiffPixelAction = QAction('prev diff pixel', viewMenu)
            prevDiffPixelAction.setShortcut('Ctrl+,')
            prevDiffPixelAction.triggered.connect(self.centralWidgetDict[MAIN_WINDOW_MODE.COMPARE].prevDiffPixel)
            viewMenu.addAction(prevDiffPixelAction)
        return menuBar

    def draw(self):
        imagePath1 =  self.imagePathList1[self.index]
        imagePath2 = ''
        if self.imagePathList2: imagePath2 = self.imagePathList2[self.index]
        self.centralWidget().draw(imagePath1=imagePath1,
                                  imagePath2=imagePath2,
                                  index=self.index,
                                  totalImageSets=len(self.imagePathList1))


def launch(configManager, imagePathList1, imagePathList2=[], mode=MAIN_WINDOW_MODE.VIEW, **kwargs):

    app = QApplication([])

    pv = MainWindow(mode=mode, configManager=configManager, **kwargs)
    pv.imagePathList1 = imagePathList1
    pv.imagePathList2 = imagePathList2
    pv.draw()
    pv.show()

    app.exec_()
