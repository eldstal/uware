import sys
import random
import threading
import curses
import re

from logging import LOG
from inputs import INPUTS


#
# This class does two things: It's an UI and a keyboard handler.
#

class UICurses:

  def __init__(self):
    global LOG
    self.score_p1 = 0
    self.score_p2 = 0

    self.keyboard_map = {}
    self.quit = False
    self.players_ready = False
    self.input_received = threading.Condition()

    # Replace logging facilities with our own function
    LOG = self
    self.log = ""

    # curses state
    self.win = None

  # Ersatz LOG handler that other modules use to show text
  def write(self, message):
    cr = re.sub("\n", "\n\r", message, re.M)
    self.log += cr
    if (self.win is not None):
      self.win.clear()
      self.win.addstr(self.log)
      self.win.refresh()
    else:
      pass
      #sys.stderr.write(message)

  def round_results(self, results):
    if (results["winner"] == 1): self.score_p1 += 1
    if (results["winner"] == 2): self.score_p2 += 1
    pass

  # Joystick events, etc.
  def on_input(self, controller, event, value):
    LOG.write("Controller {} {} = {}\n".format(controller, event,  value))


    # Console QUIT key
    if (event == "quit"):
      with self.input_received:
        self.quit = True
        self.input_received.notify()

    # Anyone presses any button to start a game
    elif (not self.players_ready and value == 1):
      with self.input_received:
        self.players_ready = True
        self.input_received.notify()


  # Given a list of games known, return one of them
  # Return None to exit.
  # This is a modal function, output
  # belongs to the UI while it is running.
  # Meanwhile, input is handled in a different thread and on_input() will be called.
  def select_game(self, games):

    self.players_ready = False
    self.write("P1: {}     P2: {}\n".format(self.score_p1, self.score_p2))
    self.write("\n")
    self.write("Games\n")
    self.write("------------\n")
    for g in games:
      self.write("{:>10} {}\n".format(g["author"], g["title"]))
    self.write("------------\n")

    self.write("Press ANYTHING to start playing...\n")

    while not self.quit and not self.players_ready:
      # TODO: select() or something, rather than polling a non-blocking stdin
      self.handle_input()

    if (self.quit):
      return None

    return random.choice(games)


  # Set up resources, configure terminal, whatever else
  def start_ui(self):
    self.win = curses.initscr()
    self.win.scrollok(1)
    curses.noecho()
    curses.halfdelay(1)   # 1/10 second timeout

    # Old logged text, put it back in the window
    self.win.addstr(self.log)
    self.win.refresh()

    pass

  # Release any exclusively held resources (reset the terminal, for example)
  def stop_ui(self):
    self.win.clear()
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    self.win = None

  # stop_ui() was called last, time to shutdown permanently
  def shutdown_ui(self):
    LOG = sys.stderr
    LOG.write("\n"*20)
    LOG.write("Old log:-------------------------\n")
    LOG.write(self.log)
    LOG.write("UI shut down\n")


  def handle_input(self):
    try:
      key = self.win.getkey()
    except:
      # Polling timeout, no key was pressed
      return

    if key in self.keyboard_map:
      controller,ev = self.keyboard_map[key]
      self.on_input(controller, ev, 1)
      self.on_input(controller, ev, 0)


  def add_keyboard_mapping(self, controller, mapping):
    for ev,key in mapping.items():
      self.keyboard_map[key] = (controller, ev)

  # Initialize any resources, be prepared to release them in stop_input()
  def start_input(self):
    pass

  # Release any exclusively-held resources (but be prepared for start_input() later)
  def stop_input(self):
    pass

  def shutdown_input(self):
    pass
