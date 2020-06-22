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


from PySide2.QtCore import QPoint
from .abstractLoadingIndicator import AbstractLoadingIndicator


class Line(AbstractLoadingIndicator):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    def initVars(self, parent, **kwargs):
        super().initVars(parent, **kwargs)

        self.posList = [
            QPoint(-2, 0),
            QPoint(-1, 0),
            QPoint( 0, 0),
            QPoint( 1, 0),
            QPoint( 2, 0),
        ]

        self.spacing = QPoint(2 * self.prop.dx + 10, 2 * self.prop.dy + 10)
