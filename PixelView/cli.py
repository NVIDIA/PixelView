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


import argparse
from PixelView import topLevel
from PixelView.utils.cli import paramList, handleCli
from PixelView.imageContainers.common import Geometry
from PixelView.config.configManager import ConfigManager


def subCommands(subparsers):
    command = 'version'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)

    command = 'info'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)
    subparser.add_argument('filePath', help='Image File Path')

    command = 'printVal'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)
    subparser.add_argument('filePath', help='Image File Path')
    subparser.add_argument('x', help='X coordinate', type=int)
    subparser.add_argument('y', help='Y coordinate', type=int)

    command = 'genCanvas'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)
    subparser.add_argument('outFilePath', help='Output File Path')
    subparser.add_argument('red',         help='Red   component [0-255]', type=int)
    subparser.add_argument('green',       help='Green component [0-255]', type=int)
    subparser.add_argument('blue',        help='Blue  component [0-255]', type=int)
    subparser.add_argument('--alpha',     help='Alpha component [0-255]', type=int)
    subparser.add_argument('--width',     help='Surface Area Width',      type=int, default='320')
    subparser.add_argument('--height',    help='Surface Area Height',     type=int, default='240')

    command = 'genConfig'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)
    subparser.add_argument('dirPath', help='Path to directory that will contain the config files\n'
                                           'If it does not exists, it is created')
    command = 'setConfigStart'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)
    subparser.add_argument('filePath', help='Path to the configMenu File')

    command = 'clearConfigStart'
    subparser = subparsers.add_parser(command)
    subparser.set_defaults(command=command)

    command = 'view'
    subparser = subparsers.add_parser(command, formatter_class=argparse.RawTextHelpFormatter)
    subparser.set_defaults(command=command)
    subparser.set_defaults(fListVarNameList=['filePathList'])
    subparser.add_argument('filePathList',
                           help='This argument can be either:\n'
                                '- The file path for the image\n'
                                '- A commaseparated list of file paths for the images\n'
                                '- A path of a file that contains file paths for the images (with --fList flag)',
                           type=paramList)
    subparser.add_argument('--fList', action='store_true',
                           help='If present, any path provided is treated as a file that contains file paths to images')

    command = 'compare'
    subparser = subparsers.add_parser(command, formatter_class=argparse.RawTextHelpFormatter)
    subparser.set_defaults(command=command)
    subparser.set_defaults(fListVarNameList=['filePathList1', 'filePathList2'])
    subparser.add_argument('filePathList1',
                           help='This argument can be either:\n'
                                '- The file path for the image\n'
                                '- A commaseparated list of file paths for the images\n'
                                '- A path of a file that contains file paths for the images (with --fList flag)',
                           type=paramList)
    subparser.add_argument('filePathList2',
                           help='Same as filePathList1, but for the second image (or second set of images)',
                           type=paramList)
    subparser.add_argument('--fList', action='store_true',
                           help='If present, any path provided is treated as a file that contains file paths to images')
    subparser.add_argument('--geometry1', help='The area within the image to compare, of the form: <width>x<height>+<x>+<y>', type=Geometry)
    subparser.add_argument('--geometry2', help='The area within the image to compare, of the form: <width>x<height>+<x>+<y>', type=Geometry)


def run():
    parser = argparse.ArgumentParser(prog='PixelView', formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
    parser.add_argument('--cf', help='Config File Path', dest='configFilePath')
    parser.add_argument('--cn', help='Config Name', dest='configName')
    parser.add_argument('--useInternalDefaults', help='Config Name', dest='isUseInternalDefaults', action='store_true')
    subCommands(subparsers)
    args = parser.parse_args()
    handleCli(args, topLevel, ConfigManager)
