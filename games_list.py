import os
from paths import *


# Check if a directory is a valid game,
# and return its game dict if so.
def _game_directory_info(repo_name, game_dir_name):
  pass

# Returns a string revision hash or None on error
def _repo_revision(repo_name):
  pass

# If a repo exists and the remote URL matches, return True
# If the repo doesn't exist, return False
# If the repo exists but has a different remote, delete it and return False
def _repo_present(repo_name, url):
  pass

# Fetch, build, check for games.
# Returns a list of game dicts.
def repo_refresh(repo_name):
  games_list = []

  needs_build = False
  if repo_already_exists(repo_name):
    old_rev = _repo_revision(repo_name)
    # TODO: git pull
    new_rev = _repo_revision(repo_name)
    if (new_rev != new_rev):
      needs_build = True
  else:
    # TODO: git clone
    needs_build = True

  if (needs_build):
    pass
    # TODO: cd repo && ./build

  repo_root = os.path.join(REPOS, repo_name)
  subdirs = [f.path for f in os.scandir(repo_root) if f.is_dir() ]
  for game_dir_name in subdirs:
    game = _game_directory_info(repo_name, game_dir_name)
    if (game is not None):
      games_list += [ game ]

  return games_list

# Outputs a list of games
# Each game is a dict of
#  title
#  author
#  path
#  icon (if icon.png is present)
def reload(conf):
  games_list = []
  for repo_name,url in enumerate(conf):
    games_list += repo_refresh(repo_name)
  return games_list
