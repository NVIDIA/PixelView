# PixelView
A compact and extensible image viewer
* Facilitates the comparison and review of sets of multiple images
* Is easily extendable to perform custom pixel level analysis
* It can be cleanly wrapped by other programs to create more complex and specific automation (it is both, a python app and a python module)
* Can run in Linux and Windows


## Requirements
* Python3 (https://www.python.org)
* pip     (https://pypi.org/project/pip)
* Pillow  (https://pypi.org/project/Pillow)
* PySide2 (https://pypi.org/project/PySide2)
* pUtils  (https://github.com/GawpAzrag/pUtils)


## Installation
* Install the requirements listed above
* Clone PixelView and install it
```
git clone https://github.com/NVIDIA/PixelView.git
cd PixelView
pip install .
```
> **Note:** In Windows you need to have the 'Scripts' directory within your python installation on your path if you want to invoke it just by 'PixelView'. Alternatively you can invoke it by 'python3 -m PixelView' as well.


## Usage
PixelView supports PNG (24bit rgb and 32bit rgba) as well as its own format, which is simply a flat rgb(a) 8bits per channel with a single line ascii header at the top.
The examples below use rgba format so that the earlier commands generate some single color images and the commands later on, reads them. This is so that it is possible to copy and paste each command in order as they are and see them work (except for the couple that have a syntax place holder, easily identifiable by the "<  >" symbols), to provide a smooth "tour" of the application.

### version
To display PixelView's version
```
 PixelView version
```

### genCanvas
To generate a single color image file in rgb(a) format (the file will contain a one line ascii header at the top)
```
 PixelView genCanvas red320.rgba  255 0 0 --alpha 0
 PixelView genCanvas blue320.rgba 0 0 255 --alpha 0
```

### info
To display basic information of an image
```
 PixelView info red320.rgba
```

### printVal
To print the value of a specific pixel
```
 PixelView printVal red320.rgba 0 0
```

### view
To view an image
```
 PixelView view red320.rgba
```

To view a list of images (displayed one at a time)
```
 PixelView view red320.rgba,blue320.rgba
```
Same as above, but loading the list from a file (one path per line)
```
 PixelView view <imagesPathList> --fList
```

### compare
To compare two images
```
 PixelView compare red320.rgba blue320.rgba
```

To compare two lists of images (displayed one pair at a time)
```
 PixelView compare red320.rgba,blue320.rgba blue320.rgba,red320.rgba
```
Same as above but providing the list files (one path per line)
```
 PixelView compare <imagesPathListA> <imagesPathListB> --fList
```

To compare subsections of the images
```
 PixelView compare red320.rgba,blue320.rgba blue320.rgba,red320.rgba --geometry1=200x100+0+0 --geometry2=200x100+20+10
```

### Customization and configuration
 To generate a set of starting configuration files and tell PixelView to use them
```
 PixelView --useInternalDefaults genConfig myConfigDir
 PixelView setConfigStart myConfigDir/configMenu.json
```
 Edit myConfigDir/config1.json to customize PixelView

### help
 For a full list of commands
```
 PixelView -h
```


## Issues and Contributing
[Checkout the Contributing document!](CONTRIBUTING.md)
* Please let us know by [filing a new issue](http://github.com/NVIDIA/PixelView/issues/new)
* You can contribute by opening a [pull request](https://help.github.com/articles/using-pull-requests)
