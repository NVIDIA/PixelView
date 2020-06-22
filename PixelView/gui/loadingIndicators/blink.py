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


from PySide2.QtCore import QPoint, QRect
from PySide2.QtGui import QPainter, QBrush, QColor
from .abstractLoadingIndicator import AbstractLoadingIndicator


class Blink(AbstractLoadingIndicator):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        center = QPoint(self.width() / 2, self.height() / 2)
        painter.fillRect(self.rect(), QBrush(QColor(255, 255, 255, 160)))

        margin = 20
        painter.fillRect(QRect(center.x() - self.prop.dx - margin,
                               center.y() - self.prop.dy - margin,
                               (self.prop.dx + margin) * 2,
                               (self.prop.dy + margin) * 2),
                         QBrush(QColor(0, 0, 0, 255)))

        self.prop.draw(painter,
                       QPoint(center.x(),
                              center.y()),
                       True if self.counter == 0 else False)

        painter.end()

        self.counter += 1
        self.counter %= 2
