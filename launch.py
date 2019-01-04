import sys
import subprocess
import json

from logging import LOG
from paths import *

# Return game's result (or a draw if the game failed for any reason)
def launch(game):

  fallback = { "winner":0, "exit":0 }

  LOG.write("Launching game: {} by {}\n".format(game["title"], game["author"]))
  try:
    j = subprocess.check_output([game["executable"], GAME_CONF], cwd=game["directory"])
    return json.loads(j.decode("utf-8"))

  except subprocess.CalledProcessError as e:
    LOG.write("Game returned error code {}\n".format(e.returncode))
    LOG.write("Game output:\n{}\n".format(e.output))

  except json.JSONDecodeError as e:
    LOG.write("Game output is not valid JSON: {}\n".format(e.msg))
    LOG.write("Game output:\n{}\n".format(j))

  return fallback

