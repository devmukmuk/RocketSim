#!/usr/bin/env bash

set -e

echo "Creating PackIt CLI command scaffold..."

BASE="cli/commands"

# Create directories
mkdir -p $BASE/{core,logging,mode,rooms,boxes,qr,reports,maintenance}

########################################
# registry.py
########################################

cat << 'EOF' > $BASE/registry.py
COMMANDS = {}

def register_command(name, help_text=""):

    def decorator(func):
        COMMANDS[name] = {
            "func": func,
            "help": help_text
        }
        return func

    return decorator
EOF

########################################
# loader.py
########################################

cat << 'EOF' > $BASE/loader.py
import importlib
import pkgutil

def load_commands(package_name="cli.commands"):

    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(
        package.__path__,
        package.__name__ + "."
    ):

        if module_name.endswith("__init__"):
            continue

        importlib.import_module(module_name)
EOF

########################################
# Helper function to create command files
########################################

create_cmd () {
    FILE=$1
    CMD=$2
    HELP=$3

cat << EOF > $FILE
from cli.commands.registry import register_command


@register_command("$CMD", "$HELP")
def ${CMD//-/_}_cmd(args, state):

    print("TODO: implement $CMD")
EOF

}

########################################
# CORE
########################################

create_cmd $BASE/core/show_config_cmd.py "show-config" "Display current configuration"
create_cmd $BASE/core/set_config_cmd.py "set-config" "Update config.ini value"
create_cmd $BASE/core/version_cmd.py "version" "Show PackIt version"

########################################
# LOGGING
########################################

create_cmd $BASE/logging/log_level_cmd.py "log-level" "Set logging level"
create_cmd $BASE/logging/log_show_cmd.py "log-show" "Display logs"
create_cmd $BASE/logging/log_clear_cmd.py "log-clear" "Clear logs"

########################################
# MODE
########################################

create_cmd $BASE/mode/mode_cmd.py "mode" "Set output mode"
create_cmd $BASE/mode/sync_cmd.py "sync" "Sync local and Google data"

########################################
# ROOMS
########################################

create_cmd $BASE/rooms/room_add_cmd.py "room-add" "Create a new room"
create_cmd $BASE/rooms/room_remove_cmd.py "room-remove" "Delete a room"
create_cmd $BASE/rooms/room_list_cmd.py "room-list" "List rooms"
create_cmd $BASE/rooms/room_rename_cmd.py "room-rename" "Rename room"

########################################
# BOXES
########################################

create_cmd $BASE/boxes/box_add_cmd.py "box-add" "Add a box"
create_cmd $BASE/boxes/box_remove_cmd.py "box-remove" "Remove a box"
create_cmd $BASE/boxes/box_list_cmd.py "box-list" "List boxes"
create_cmd $BASE/boxes/box_move_cmd.py "box-move" "Move box"
create_cmd $BASE/boxes/box_rename_cmd.py "box-rename" "Rename box"

########################################
# QR
########################################

create_cmd $BASE/qr/qr_generate_cmd.py "qr-generate" "Generate QR code"
create_cmd $BASE/qr/qr_regenerate_cmd.py "qr-regenerate" "Regenerate QR codes"
create_cmd $BASE/qr/qr_room_cmd.py "qr-room" "Generate room QR codes"

########################################
# REPORTS
########################################

create_cmd $BASE/reports/report_room_cmd.py "report-room" "Generate room report"
create_cmd $BASE/reports/report_box_cmd.py "report-box" "Generate box report"
create_cmd $BASE/reports/report_all_cmd.py "report-all" "Generate full report"

########################################
# MAINTENANCE
########################################

create_cmd $BASE/maintenance/validate_cmd.py "validate" "Validate system"
create_cmd $BASE/maintenance/repair_cmd.py "repair" "Repair system"
create_cmd $BASE/maintenance/cleanup_cmd.py "cleanup" "Cleanup temp files"

echo "PackIt CLI scaffold created successfully."