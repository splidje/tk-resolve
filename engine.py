import os
import logging
from functools import wraps

import fusionscript

from sgtk import Context
from sgtk.platform import Engine


def _log_exception(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except:
            self.logger.exception("Exception:")
            raise

    return wrapper


class ResolveEngine(Engine):
    def init_engine(self):
        self._commands_window = self.import_module(
            "tk_resolve"
        ).ShotGridCommandsWindow()
        self._commands_window.setVisible(True)

    def post_app_init(self):
        self._refresh_shotgun_menu()
        self._open_project_path_if_required()

    def destroy_engine(self):
        self._commands_window.close()

    @property
    def context_change_allowed(self):
        return True

    @property
    def has_ui(self):
        return True

    def _emit_log_message(self, handler, record):
        if record.levelno < logging.INFO:
            formatter = logging.Formatter("Debug: Shotgun %(basename)s: %(message)s")
        else:
            formatter = logging.Formatter("Shotgun %(basename)s: %(message)s")
        msg = formatter.format(record)
        print(msg)

    def _register_save_project_command(self):
        self.register_command(
            "Save Project",
            self._save_project,
            dict(
                short_name="save_project",
            ),
        )

    @_log_exception
    def _save_project(self):
        workfiles_app, scene_operation = self._find_workfiles_app_and_scene_operation()
        if not workfiles_app:
            raise KeyError("Can't save project. No Workfiles app.")
        scene_operation.save_file(
            workfiles_app, scene_operation.SAVE_FILE_AS_ACTION, self.context
        )

    def _refresh_shotgun_menu(self):
        self._register_save_project_command()
        self._commands_window.reset_commands(self.commands)

    def post_context_change(self, old_context, new_context):
        os.environ["TANK_CONTEXT"] = Context.serialize(new_context)
        self._refresh_shotgun_menu()

    @property
    def resolve(self):
        return fusionscript.scriptapp("Resolve")

    def _open_project_path_if_required(self):
        project_path = os.getenv("SGTK_RESOLVE_PROJECT_PATH_TO_OPEN")
        if not project_path:
            return
        del os.environ["SGTK_RESOLVE_PROJECT_PATH_TO_OPEN"]
        workfiles_app, scene_operation = self._find_workfiles_app_and_scene_operation()
        if not workfiles_app:
            self.logger.warning(
                f"No workfiles2 app, so skipping opening: {project_path}"
            )
            return
        scene_operation.open_file(
            workfiles_app,
            scene_operation.OPEN_FILE_ACTION,
            self.context,
            project_path,
            0,
            False,
        )

    def _find_workfiles_app_and_scene_operation(self):
        workfiles_app = self.apps.get("tk-multi-workfiles2")
        if not workfiles_app:
            return None, None
        return (
            workfiles_app,
            workfiles_app.import_module("tk_multi_workfiles").scene_operation,
        )
