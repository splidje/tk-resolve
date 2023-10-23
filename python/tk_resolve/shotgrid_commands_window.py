from PySide2 import QtCore, QtWidgets

import sgtk

_ENGINE = sgtk.platform.current_bundle()


class ShotGridCommandsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(flags=QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle("ShotGrid - DaVinci Resolve")
        self._command_menu = QtWidgets.QMenu("ShotGrid", self)
        self.menuBar().addMenu(self._command_menu)

        self.setMinimumSize(350, 0)
        size = self.minimumSizeHint()
        self.resize(size)
        self.setMaximumSize(size)

        QtCore.QTimer.singleShot(0, self.deferred_init)

    def deferred_init(self):
        self.move(self.x(), 0)
        _ENGINE._initialize_dark_look_and_feel()

    def reset_commands(self, commands):
        self._command_menu.clear()
        for name, command in sorted(commands.items()):
            action = self._command_menu.addAction(name, command["callback"])
