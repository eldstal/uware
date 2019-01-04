import json
import sys

from paths import *
from logging import LOG

def load_source_conf():
  try:
    j = open(SRC_CONF,"r")
    sources = json.load(j)

    if "repos" not in sources:
      LOG.write("No repos specified in {}\n".format(SRC_CONF))
      return None

    if not isinstance(sources["repos"], dict):
      LOG.write("repos not in dict format in {}\n".format(SRC_CONF))
      return None

    if "blacklist" not in sources:
      sources["blacklist"] = []

    return sources

  except Exception as e:
    LOG.write("Unable to load {}.\n".format(SRC_CONF))
    LOG.write("{}\n".format(e.msg))
    return None

def _dict_has_string(d, s):
  if s not in d:
    return False, "{} not set".format(s)
  if not isinstance(d[s], str):
    return False, "{} not a string",format(s)
  return True,""

def _check_console_conf(conf, key):
  if key not in conf:
    return False, "{} controller configuration missing".format(key)

  if not isinstance(conf[key], dict):
    return False, "{} is not a dictionary of controls".format(key)

  expected_strings = [ "quit" ]

  for s in expected_strings:
    ok,msg = _dict_has_string(conf[key], s)
    if not ok:
      return False,msg

  return True,""


def _check_controller_conf(conf, key):
  if key not in conf:
    return False, "{} controller configuration missing".format(key)

  if not isinstance(conf[key], dict):
    return False, "{} is not a dictionary of controls".format(key)

  expected_strings = [
      "device",

      "button-Y",
      "button-X",
      "button-B",
      "button-A",

      "dpad-up",
      "dpad-down",
      "dpad-left",
      "dpad-right",

      "bumper-L",
      "bumper-R",
      "trigger-L",
      "trigger-R",

      "L3",
      "R3"
    ]

  analog_strings = [
      "axis-X1",
      "axis-Y1",
      "axis-X2",
      "axis-Y2"
  ]

  for s in expected_strings:
    ok,msg = _dict_has_string(conf[key], s)
    if not ok:
      return False,msg

  # Joystick devices have some additional requirements
  if conf[key]["device"] != "keyboard":
    for s in analog_strings:
      ok,msg = _dict_has_string(conf[key], s)
      if not ok:
        return False,msg


  return True,""

def load_game_conf():
  try:
    j = open(GAME_CONF, "r")
    conf = json.load(j)

    for k in [ "player1-color", "player2-color" ]:
      ok,msg = _dict_has_string(conf, k)
      if not ok:
        LOG.write("{} \n".format(msg))
        return None

    for k in [ "controller1", "controller2" ]:
      ok,msg = _check_controller_conf(conf, k)
      if not ok:
        LOG.write("{} not configured: {}\n".format(k, msg))
        return None

    ok,msg = _check_console_conf(conf, "console")
    if not ok:
      LOG.write("console not configured: {}\n".format(msg))
      return None

    return conf

  except json.JSONDecodeError as e:
    LOG.write("Unable to load {}\n".format(GAME_CONF))
    LOG.write("{}\n".format(e.msg))
    return None

