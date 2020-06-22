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


from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter, QBrush, QColor
from PySide2.QtCore import QRect, QPoint, QSize, Qt
from PixelView.utils.cli import pprint
from PixelView.gui.loadingIndicators.common import SHAPE, DIRECTION


class Prop:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.space  = 0
        self.fillBrush  = None
        self.hollowBrush  = None
        self.numSockets = 0
        self.shape = SHAPE.RECT
        self.drawFuncDict = {
            SHAPE.RECT:    self.drawRect,
            SHAPE.ELLIPSE: self.drawEllipse,
        }

    def draw(self, painter, center, isFill):
        self.drawFuncDict.get(self.shape, self.drawDefault)(painter, center, isFill)

    def drawEllipse(self, painter, center, isFill):
        painter.setBrush(self.fillBrush if isFill else self.hollowBrush)
        painter.drawEllipse(center, self.dx, self.dy)

    def drawRect(self, painter, center, isFill):
        painter.fillRect(center.x() - self.dx, center.y() - self.dy, self.dx * 2, self.dy * 2, self.fillBrush if isFill else self.hollowBrush)

    def drawDefault(self, painter, center, isFill):
        self.drawRect(self, painter, center, isFill)


class AbstractLoadingIndicator(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(AbstractLoadingIndicator, self).__init__(parent)
        self.palette().setColor(self.palette().Background, Qt.transparent)
        self.initVars(parent, **kwargs)

    def initVars(self, parent, configManager, **kwargs):
        self.cm = configManager
        self.parent = parent

        self.counter = 0
        self.refreshRate = self.cm.getLoadingIndicatorRefreshRate()

        self.prop = Prop()
        self.prop.dx = self.cm.getPropDx()
        self.prop.dy = self.cm.getPropDy()
        self.prop.fillBrush    = QBrush(QColor(*self.cm.getPropFillColor()))
        self.prop.hollowBrush  = QBrush(QColor(*self.cm.getPropHollowColor()))
        self.prop.shape = self.cm.getPropShape()

        self.posList = []
        self.spacing = QPoint(0, 0)
        self.direction = self.cm.getLoadingIndicatorDirection()
        self.tmpIncr = 1

        self.postFunc = None

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        center = QPoint(self.width() / 2, self.height() / 2)

        # Dim out the background
        painter.fillRect(self.rect(), QBrush(QColor(255, 255, 255, 160)))

        ### Add a black rectangle where the loading icon would be displayed ###
        startPos = QPoint(min([i.x() for i in self.posList]),
                          min([i.y() for i in self.posList]))
        endPos   = QPoint(max([i.x() for i in self.posList]),
                          max([i.y() for i in self.posList]))
        delta   = QPoint(endPos.x() - startPos.x(),
                         endPos.y() - startPos.y())

        marginX = 20
        marginY = 20
        origin = QPoint(center.x() + startPos.x() * self.spacing.x() - self.prop.dx - marginX,
                        center.y() + startPos.y() * self.spacing.y() - self.prop.dy - marginY)
        size = QSize(delta.x() * self.spacing.x() + 2 * self.prop.dx + 2 * marginX,
                     delta.y() * self.spacing.y() + 2 * self.prop.dy + 2 * marginY)

        painter.fillRect(QRect(origin, size), QColor(0, 0, 0, 255))
        #######################################################################

        for i in range(len(self.posList)):
            pos = self.posList[i]
            self.prop.draw(painter,
                           QPoint(center.x() + pos.x() * self.spacing.x(),
                                  center.y() + pos.y() * self.spacing.y()),
                           True if i == self.counter else False)

        painter.end()
        self.counterNext()

    def counterForward(self):
        self.counter += 1
        self.counter %= len(self.posList)
        return self.counter

    def counterBack(self):
        self.counter -= 1
        if self.counter < 0:
            self.counter = len(self.posList) - 1
        return self.counter

    def counterBackAndForth(self):
        self.counter += self.tmpIncr
        if self.counter < 0:
            self.counter = 1
            self.tmpIncr = 1
        elif  self.counter >= len(self.posList):
            self.counter = len(self.posList) - 2
            self.tmpIncr = -1
        return self.counter

    def counterNext(self):
        if self.direction is DIRECTION.FORWARD: return self.counterForward()
        if self.direction is DIRECTION.BACKWARD: return self.counterBack()
        if self.direction is DIRECTION.BACK_AND_FORTH: return self.counterBackAndForth()

        # This should never be reached, but just for safety
        pprint('WARNING: direction "%s" not known' % str(self.direction))
        return self.counterForward

    def isDoneFunc(self):
        return False

    def timerEvent(self, event):
        if self.isDoneFunc():
            self.hide()
            self.postFunc()
            return
        self.update()

    def start(self, isDoneFunc, postFunc):
        self.isDoneFunc = isDoneFunc
        self.postFunc = postFunc
        self.show()

    def showEvent(self, event):
        self.resize(self.parent.width(), self.parent.height())
        self.timer = self.startTimer(self.refreshRate)

    def hideEvent(self, event):
        self.killTimer(self.timer)
        self.counter = 0
