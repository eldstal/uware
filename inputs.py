import sys

from logging import LOG


# Controller number to Input mapper
INPUTS={}


# Start input handlers, but be prepared for stop() at any time
def start():
  for c,m in INPUTS.items():
    m.start_input()

# Release any exclusive resources from all inputs
def stop():
  for c,m in INPUTS.items():
    m.stop_input()

def shutdown():
  for c,m in INPUTS.items():
    m.shutdown_input()

# Set up one or more inputs, connect them to an UI
def setup(keyboard, input_handler, game_conf):

  # Console keyboard handler is always present
  INPUTS[0] = keyboard
  INPUTS[0].add_keyboard_mapping(0, game_conf["console"])

  for controller in [ 1, 2 ]:
    mapping = game_conf["controller{}".format(controller)]

    if mapping["device"] == "keyboard":
      # Attach to the console keyboard handler
      INPUTS[0].add_keyboard_mapping(controller, mapping)
    else:
      LOG.write("Ignoring controller {}. Unsupported device.\n".format(controller))


