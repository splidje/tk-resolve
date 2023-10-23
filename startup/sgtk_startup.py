import os
import sys
from pathlib import Path

from PySide2 import QtCore, QtWidgets


def _sgtk_startup():
    sys.path.append(
        str(Path(os.getenv("TANK_CURRENT_PC")) / "install" / "core" / "python")
    )
    import sgtk

    # start up shotgun engine
    engine = sgtk.platform.current_engine()
    if engine:
        return

    from tank_vendor.shotgun_authentication import ShotgunAuthenticator

    user = ShotgunAuthenticator(sgtk.util.CoreDefaultsManager()).get_user()
    sgtk.set_authenticated_user(user)
    context = sgtk.context.deserialize(os.environ.get("TANK_CONTEXT"))
    engine = sgtk.platform.start_engine("tk-resolve", context.sgtk, context)


app = QtWidgets.QApplication([])

QtCore.QTimer.singleShot(0, _sgtk_startup)

sys.exit(app.exec_())
