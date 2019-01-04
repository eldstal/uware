import os
import sys
import re
import json
import subprocess

from paths import *

def _repo_path(repo_name):
  return os.path.join(REPOS, repo_name)

def _game_path(repo_name, game_dir_name):
  return os.path.join(_repo_path(repo_name), game_dir_name)


# Check if a directory is a valid game,
# and return its game dict if so.
# Otherwise, returns None
def _game_directory_info(repo_name, game_dir_name):
  game_dir = _game_path(repo_name, game_dir_name)
  game = {}

  # Default information
  game["author"] = repo_name
  game["title"] = game_dir_name
  game["icon"] = None

  game["tag"] = "/".join([repo_name, game_dir_name])
  game["directory"] = game_dir
  game["executable"] = os.path.join(game_dir, "run")
  game["icon"] = os.path.join(game_dir, "icon.png")

  # Must have an executable to be a game
  if (not os.access(game["directory"], os.R_OK)): return None
  if (not os.access(game["directory"], os.X_OK)): return None
  if (not os.access(game["executable"], os.X_OK)): return None
  if (not os.access(game["icon"], os.R_OK)): game["icon"] = None

  # Load additional metadata if present
  try:
    meta_file = os.path.join(game_dir, "metadata.json")
    if (os.access(meta_file, os.R_OK)):
      with open(meta_file) as m:
        j = json.load(m)
        for field in [ "author", "title" ]:
          if field in j:
            game[field] = j[field]
  except json.JSONDecodeError as e:
    LOG.write("Unable to load game metadata for {}: {}\n".format(game["tag"], e.msg))

  return game

# Returns a string revision hash or None on error
def _repo_revision(repo_name):
  repo_dir = _repo_path(repo_name)
  try:
    out = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                  cwd=repo_dir)
    return out.decode("ascii").split("\n")[0]

  except CalledProcessError as e:
    LOG.write("Not a git repo: {}".format(repo_dir))
    return None

def _repo_remote(repo_name):
  repo_dir = _repo_path(repo_name)
  try:
    out = subprocess.check_output(["git", "config", "--get", "remote.origin.url"],
                                  cwd=repo_dir)
    return out.decode("ascii").split("\n")[0]

  except CalledProcessError as e:
    LOG.write("Not a git repo: {}".format(repo_dir))
    return None

# If a repo exists and the remote URL matches, return True
# If the repo doesn't exist, return False
# If something is terriby wrong, return None
def _repo_present(repo_name, url):
  repo_dir = _repo_path(repo_name)

  if (not os.path.isdir(repo_dir)): return False


  # TODO: Remove non-git directories? I don't dare to rm -r from inside a script...
  if (_repo_revision(repo_name) is None): return None

  # TODO: Guard against renamed repos (i.e. it's a repo but with the wrong remote)
  if (_repo_remote(repo_name) != url): return None

  return True

# Fetch, build, check for games.
# Returns a list of game dicts.
def repo_refresh(repo_name, url):
  games_list = []
  repo_dir = _repo_path(repo_name)

  needs_build = False
  if _repo_present(repo_name, url):
    old_rev = _repo_revision(repo_name)
    subprocess.call(["git", "pull"], cwd=repo_dir)
    new_rev = _repo_revision(repo_name)
    if (new_rev != new_rev):
      needs_build = True
  else:
    subprocess.call(["git", "clone", url, repo_name] , cwd=REPOS)
    LOG.write("Initial checkout of repo {}.\n".format(repo_name))
    needs_build = True

  if (needs_build):
    script = os.path.join(repo_dir, "build")
    if (os.access(script, os.X_OK)):
      if (subprocess.call(script, cwd=repo_dir) != 0):
        LOG.write("Build failed for repo {}. Continuing anyway.\n".format(repo_name))
    else:
      LOG.write("No build script in repo {}. No problem, probably.\n".format(repo_name))


  repo_root = os.path.join(REPOS, repo_name)
  subdirs = [ f.name for f in os.scandir(repo_root) if f.is_dir() ]
  for game_dir_name in subdirs:
    game = _game_directory_info(repo_name, game_dir_name)
    if (game is not None):
      games_list += [ game ]

  return games_list

def _cleanup_name(name):
  return re.sub('[^A-Za-z0-9_-]', '', name)

def _is_blacklisted(game, blacklist):
  for blk in blacklist:
    if blk in game["tag"]: return True
  return False

# Outputs a list of games
# Blacklist is a list of strings matched against the paths of games.
# If a game's repo path relative to the launcher root contains a blacklisted string,
# the game isn't included in the returned games list.
# Examples of blacklist strings are "eldstal/example_game" or "test"
# Each returned game is a dict of
#  title
#  author
#  tag    (something like "repo/cool_game")
#  directory
#  executable
#  icon (path or None)
def reload(sources):
  games_list = []
  if (not os.path.isdir(REPOS)):
    os.mkdir(REPOS)

  for _,repo_name in enumerate(sources["repos"]):
    url = sources["repos"][repo_name]

    repo_name = _cleanup_name(repo_name)

    if not isinstance(url, str):
      LOG.write("Configured repo {} does not have a URL. Skipping.\n".format(repo_name))
      continue

    games_list += repo_refresh(repo_name, url)

  games_list = [ g for g in games_list if not _is_blacklisted(g, sources["blacklist"]) ]

  return games_list
