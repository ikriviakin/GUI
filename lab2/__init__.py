import os

import PyQt5

_package_root = os.path.dirname(PyQt5.__file__)
_platform_dir = os.path.join(_package_root, "Qt5", "plugins", "platforms")

if not os.path.isdir(_platform_dir):
    _platform_dir = os.path.join(_package_root, "Qt", "plugins", "platforms")

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = _platform_dir
