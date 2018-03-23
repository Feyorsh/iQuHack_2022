import logging
import traceback

import display
import ai
import room
import gui
import map
import fonts as f


loaded_map = None
units_manager = None
winner = None


def load_map(map_path):
    global loaded_map, units_manager

    try:
        loaded_map = map.Map(map_path)
        units_manager = loaded_map.units_manager
        for team in units_manager.teams:
            if team.ai:
                team.ai = ai.AI(loaded_map, units_manager, team)
    except:
        msg = _("Can't load map %s! Probably the format is not ok.\n%s") % (map_path, traceback.format_exc())
        logging.error(msg)
        room.run_room(gui.Dialog(msg, f.SMALL_FONT, center=display.get_rect().center))

def kill(unit):
    loaded_map.kill_unit(unit=unit)
    units_manager.kill_unit(unit)

