import os

import PyQt5
from PyQt5.QtCore import QCoreApplication

_pyqt_root = os.path.dirname(PyQt5.__file__)
_plugins_root = os.path.join(_pyqt_root, "Qt5", "plugins")

if not os.path.isdir(_plugins_root):
    _plugins_root = os.path.join(_pyqt_root, "Qt", "plugins")

_platforms = os.path.join(_plugins_root, "platforms")
if os.path.isdir(_platforms):
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = _platforms

QCoreApplication.addLibraryPath(_plugins_root)