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


import sys
import enum
import pUtils
import platform


def paramList(arg):
    return arg.split(',')


def handleCli(args, topLevel, ConfigManager=None):
    kwargs = vars(args)

    preprocessFileList(kwargs)

    command = kwargs.pop('command')
    func = getattr(topLevel, command)

    if kwargs['verbose']:
        pprint(kwargs, color=COLOR.TEAL)
        pprint('---------------------------')

    if ConfigManager:
        kwargs['configManager'] = ConfigManager(**kwargs)

    func(**kwargs)


def preprocessFileList(kwargs):
    fList = kwargs.get('fList')

    if not fList: return
    fListVarNameList = kwargs['fListVarNameList']
    for fListVarName in fListVarNameList:
        fListVar = kwargs.get(fListVarName)
        if fListVar is None: continue
        t = []
        for item in fListVar:
            t += pUtils.quickFileRead(item, 'txt')
        kwargs[fListVarName] = t


class COLOR(enum.Enum):
    RED   = 91
    GREEN = 32
    BLUE  = 34
    TEAL  = 96


def colorString(s, color):
    if platform.system() == 'Linux':
        return '\033[%im%s\033[00m' % (color.value, s)
    return s


def pprint(s, color=None, endLine=True):
    s = str(s)

    if endLine:
        s += '\n'

    if PPRINT_LOG_FILE:
        pUtils.quickFileWrite(PPRINT_LOG_FILE, s, 'at')

    if color:
        s = colorString(s, color)

    sys.stdout.write(s)
    sys.stdout.flush()


PPRINT_LOG_FILE = None
