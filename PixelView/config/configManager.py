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
import pUtils
from importlib import import_module
from PixelView.utils.cli import pprint, COLOR
from PixelView.gui.loadingIndicators.common import SHAPE, DIRECTION


class ConfigManager:
    """
    The ConfigManager takes care of all settings/configurations throughout the
    life of the application.
    When the app requires to know the current value of a given setting/config,
    it just asks the ConfigManager through the 'get' functions on the bottom
    part of this file.
    Any and all logic to figure out or pre-process any settings/config values
    is centralized and encapsulated here.
    """

    def __init__(self, configFilePath, configName, isUseInternalDefaults, verbose, **kwargs):
        self.configStartPath = os.path.join(os.path.dirname(os.path.abspath(os.path.realpath(__file__))), 'nvidiaPixelViewConfigStart.cfg')
        self.isUseInternaldefaults = isUseInternalDefaults
        self.verbose = verbose
        self.configData = {}
        self.configFilePath = None
        if self.isUseInternaldefaults is True: return

        self.determineConfigFilePath(configFilePath, configName)
        self.load()

    def determineConfigFilePath(self, configFilePath, configName):
        """
        ConfigManager determines what config file to use in the
        following way:

        1) If configFilePath is not None uses that and returns.

        2) If configStart.txt exists:
        2.1) If configName is not None then:
             - ConfigManager loads 'configStart.txt' from the same directory as this file.
               'configStart.txt' points to a config menu file
             - ConfigManager loads the config menu file
               The config menu file is a dictionary of 'configName: path' pairs
             - ConfigManager uses configName with the dictionary and gets the path

        2.2) if configName is None, is then the same as in #2.1 except that
             defaultConfigName (from the config menu file) is used as configName.

        3) Otherwise no configFile would be load
        """

        if configFilePath is not None:
            self.configFilePath = configFilePath
            if not os.path.isabs(self.configFilePath):
                self.configFilePath = os.path.join(os.path.dirname(self.configStartPath), self.configFilePath)
            return

        try:
            self.configMenuPath = pUtils.quickFileRead(self.configStartPath, 'txt')[0]
        except Exception:
            if self.verbose:
                pprint('---------------------------------')
                pprint('Info: ', color=COLOR.TEAL, endLine=False); pprint('Unable to load:')
                pprint('    %s' % self.configStartPath, color=COLOR.TEAL)
                pprint('Internal defaults will be used')
                pprint('---------------------------------')
            return

        if not os.path.isabs(self.configMenuPath):
            self.configMenuPath = os.path.join(os.path.dirname(self.configStartPath), self.configMenuPath)

        try:
            configMenuData = pUtils.quickFileRead(self.configMenuPath, 'json')
        except Exception:
            pprint('Error: ', color=COLOR.RED, endLine=False); pprint('Unable to load json file:')
            pprint('    ' + self.configMenuPath, color=COLOR.TEAL)
            exit(1)

        if configName is None:
            try:
                defaultConfigName = configMenuData['defaultConfigName']
            except Exception:
                pprint('Error: ', color=COLOR.RED, endLine=False); pprint('On file:')
                pprint('    ' + self.configMenuPath, color=COLOR.TEAL)
                pprint('Key: "', endLine=False); pprint('defaultConfigName', endLine=False, color=COLOR.TEAL); pprint('" not found')
                exit(1)
            configName = defaultConfigName

        try:
            self.configFilePathFromMenu = configMenuData['configFilePathDict'][configName]
        except Exception:
            pprint('Error: ', color=COLOR.RED, endLine=False); pprint('On file:')
            pprint('    ' + self.configMenuPath, color=COLOR.TEAL)
            pprint('Key sequence: "', endLine=False); pprint('configFilePathDict ' + configName, endLine=False, color=COLOR.TEAL); pprint('" not found')
            exit(1)

        self.configFilePath = self.configFilePathFromMenu
        if not os.path.isabs(self.configFilePath):
            self.configFilePath = os.path.join(os.path.dirname(self.configMenuPath), self.configFilePath)

    def load(self):
        if self.configFilePath is None: return 1
        try:
            self.configData = pUtils.quickFileRead(self.configFilePath, 'json')
        except Exception:
            pprint('Error: ', color=COLOR.RED, endLine=False); pprint('Unable to load json file:')
            pprint('    ' + self.configFilePath, color=COLOR.TEAL)
            exit(1)
        return 0

    def dump(self, filePath):
        data = {'configData': self.configData,
                'metadata': {'configStartPath': self.configStartPath,
                             'configMenuPath': self.configMenuPath,
                             'configFilePathFromMenu': self.configFilePathFromMenu,
                             'configFilePath': self.configFilePath}}
        pUtils.quickFileWrite(filePath, data, 'json')

    def saveFullConfig(self, filePath):
        if os.path.exists(filePath): return 1

        defaultSettingFuncList = [
            'getPropDx',
            'getPropHollowColor',
            'getLoadingIndicatorDirection',
            'getDumpFileName',
            'getPropFillColor',
            'getLoadingIndicatorClass',
            'getPropShape',
            'getNullColor',
            'getDeltaImageColorDict',
            'getPropDy',
            'getMarkerColor',
            'getLoadingIndicatorRefreshRate',
        ]

        for funcName in defaultSettingFuncList:
            func = getattr(self, funcName)
            func()
        pUtils.quickFileWrite(filePath, self.configData, 'json')
        return 0

    def genMenuConfigFile(self, filePath, configName, configPath):
        if os.path.exists(filePath): return 1

        configMenuData = {'defaultConfigName': configName,
                          'configFilePathDict': {configName: configPath}}
        pUtils.quickFileWrite(filePath, configMenuData, 'json')
        return 0

    def setConfigStart(self, filePath):
        if not os.path.exists(filePath):
            pprint('Error: ', color=COLOR.RED, endLine=False); pprint('File:')
            pprint('    ' + filePath, color=COLOR.TEAL)
            pprint('Does not exists.')
            return 1

        if os.path.exists(self.configStartPath):
            pprint('Warning: ', color=COLOR.RED, endLine=False); pprint('File:')
            pprint('    ' + self.configStartPath, color=COLOR.TEAL)
            pprint('Will be overwritten.')
            promptString = 'Proceed (y/n)? '
            if input(promptString) != 'y':
                pprint('Aborted action')
                return 2

        pUtils.quickFileWrite(self.configStartPath, os.path.abspath(os.path.realpath(filePath)))
        pprint('DONE', color=COLOR.TEAL)
        return 0

    def clearConfigStart(self):
        if not os.path.exists(self.configStartPath):
            pprint('Info: ', color=COLOR.TEAL, endLine=False); pprint('Already clear')
            return 1

        pprint('Warning: ', color=COLOR.RED, endLine=False); pprint('File:')
        pprint('    ' + self.configStartPath, color=COLOR.TEAL)
        pprint('Will be deleted.')
        promptString = 'Proceed (y/n)? '
        if input(promptString) != 'y':
            pprint('Aborted action')
            return 2

        try:
            os.remove(self.configStartPath)
        except Exception:
            pprint('Error: ', color=COLOR.RED, endLine=False); pprint('Unable to clear configStart')
            return 3

        pprint('DONE', color=COLOR.TEAL)
        return 0

    def getter(self, key, default):
        self.configData[key] = self.configData.get(key, default)
        return self.configData[key]

    # Get functions
    def getDeltaImageColorDict(self):
        return self.getter('deltaImageColor',
                           {'0': [0x00, 0x00, 0x00],
                            '1': [0x00, 0xFF, 0x00],
                            '2': [0x00, 0x00, 0xFF],
                            'default': [0xFF, 0xFF, 0xFF]})

    def getDeltaImageColor(self, deltaValue):
        t = self.getDeltaImageColorDict()
        return t.get(str(deltaValue), t['default'])

    def getDumpFileName(self):
        return self.getter('dumpFileName', 'dump.json')

    def getMarkerColor(self):
        return self.getter('markerColor', [0xFF, 0x00, 0x00])

    def getNullColor(self):
        return self.getter('nullColor', [0xFF, 0x00, 0xFF])

    def getLoadingIndicatorClass(self):
        moduleName, objName = self.getter('loadingIndicator', ['PixelView.gui.loadingIndicators.line', 'Line'])
        module = import_module(moduleName, 'PixelView.gui.loadingIndicators')
        obj = getattr(module, objName)
        return obj

    def getLoadingIndicatorRefreshRate(self):
        return self.getter('refreshRate', 100)

    def getLoadingIndicatorDirection(self):
        default = 3
        try:
            t = DIRECTION(self.getter('loadingIndicatorDirection', default))
        except Exception:
            t = DIRECTION(default)
        return t

    def getPropDx(self):
        return self.getter('propDx', 15)

    def getPropDy(self):
        return self.getter('propDy', 15)

    def getPropFillColor(self):
        return self.getter('propFillColor', [0, 0, 255, 255])

    def getPropHollowColor(self):
        return self.getter('propHollowColor', [150, 150, 150, 150])

    def getPropShape(self):
        default = 1
        try:
            t = SHAPE(self.getter('propShape', default))
        except Exception:
            t = SHAPE(default)
        return t
