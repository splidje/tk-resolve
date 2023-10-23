import os
from pathlib import Path
from shutil import copyfile

import sgtk
from sgtk.platform import SoftwareLauncher, LaunchInformation

_STARTUP_SCRIPT_FILE_NAME = "sgtk_startup.scriptlib"
_UTILITY_SCRIPT_FILE_NAME = "ShotGrid Toolkit.lua"
_STARTUP_SCRIPT_FU = "\n".join(
    (
        "if os.getenv('SGTK_RESOLVE_STARTUP_SCRIPT') then"
        "   project_manager = resolve:GetProjectManager()",
        "   project_manager:DeleteProject('Untitled')",
        "   project_manager:CreateProject('Untitled')",
        "   project_manager:LoadProject('Untitled')",
        "   fu:Execute('os.execute(\"PYTHONPATH=/opt/resolve/libs/Fusion/:$PYTHONPATH python $SGTK_RESOLVE_STARTUP_SCRIPT\")')",
        "end",
        "",
    )
)


class ResolveLauncher(SoftwareLauncher):
    def prepare_launch(self, exec_path, args, file_to_open=None):
        disk_location = Path(self.disk_location)

        sgtk_startup_script_path = disk_location / "startup" / "sgtk_startup.py"

        fusion_scripts_folder_path = (
            Path.home() / ".local" / "share" / "DaVinciResolve" / "Fusion" / "Scripts"
        )

        startup_script_path = fusion_scripts_folder_path / _STARTUP_SCRIPT_FILE_NAME
        _create_and_write_to_file(startup_script_path, _STARTUP_SCRIPT_FU)

        fusion_utility_scripts_folder_path = fusion_scripts_folder_path / "Utility"
        fusion_utility_scripts_folder_path.mkdir(parents=True, exist_ok=True)
        utility_script_path = (
            fusion_utility_scripts_folder_path / _UTILITY_SCRIPT_FILE_NAME
        )
        # The presence of this empty file will still create an item in the menu
        _create_and_write_to_file(utility_script_path, "")

        local_lut_folder_path = (
            Path(os.path.expandvars(os.getenv("SHOTGUN_HOME"))).expanduser()
            / "tk-resolve"
            / "LUT"
        )
        local_lut_folder_path.mkdir(parents=True, exist_ok=True)
        _simple_sync("/opt/resolve/LUT", local_lut_folder_path)

        required_env = dict(
            TANK_CONTEXT=sgtk.Context.serialize(self.context),
            SGTK_RESOLVE_STARTUP_SCRIPT=str(sgtk_startup_script_path),
            BMD_RESOLVE_LUT_DIR=str(local_lut_folder_path),
        )

        if file_to_open:
            required_env["SGTK_RESOLVE_PROJECT_PATH_TO_OPEN"] = file_to_open

        return LaunchInformation(exec_path, args, required_env)


def _create_and_write_to_file(path, content):
    if path.exists() or path.is_symlink():
        path.unlink()
    with path.open("w") as file_:
        file_.write(content)


def _simple_sync(source_root_folder_path, destination_root_folder_path):
    for source_folder_path, folder_names, file_names in os.walk(
        source_root_folder_path
    ):
        source_folder_path = Path(source_folder_path)
        destination_folder_path = (
            destination_root_folder_path
            / source_folder_path.relative_to(source_root_folder_path)
        )
        destination_folder_path.mkdir(parents=True, exist_ok=True)
        for file_name in file_names:
            source_file_path = source_folder_path / file_name
            destination_file_path = destination_folder_path / file_name
            if (
                destination_file_path.exists()
                and destination_file_path.stat().st_size
                == source_file_path.stat().st_size
            ):
                continue
            copyfile(source_file_path, destination_file_path)
