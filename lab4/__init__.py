import os

import PyQt5

_pyqt_base = os.path.dirname(PyQt5.__file__)

_qml_modules = os.path.join(_pyqt_base, "Qt5", "qml")
if not os.path.isdir(_qml_modules):
    _qml_modules = os.path.join(_pyqt_base, "Qt", "qml")

_plugins = os.path.join(_pyqt_base, "Qt5", "plugins")
if not os.path.isdir(_plugins):
    _plugins = os.path.join(_pyqt_base, "Qt", "plugins")

_platforms = os.path.join(_plugins, "platforms")
if os.path.isdir(_platforms):
    os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", _platforms)

os.environ["QML2_IMPORT_PATH"] = _qml_modules
os.environ["QT_PLUGIN_PATH"] = _plugins