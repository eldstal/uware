# uWare
uWare, an automatic launcher for super-short micro party-games.
Games are designed for two players and rounds of about 60 seconds or so.
Typically, the game starts with a single screen of introduction to the rules and controls.
Each game is its own program, which is invoked by the launcher and runs until termination.


# Configuration
Add game repositories to `repos.json`, formatted like this:
```json
{
   "Jen" : "http://github.com/jen/uware-games",
   "Mike" : "http://github.com/mike/tinygames"
}
```

The launcher will automatically keep these repos up-to-date between rounds.
Push a game to your repository and it will be entered into rotation automatically.

It should go without saying that you shouldn't add the repositories of people you
do not trust, since this gives them access to automatically run code on your system.


## Game repository
A game repository is a git repository and contains two things:
* A `build` script
* Any number of directories, each containing a single game.

The `build` script in the root of the repo will be executed whenever the repo
has been updated, so please make sure it runs fast and only recompiles what has changed.

Any directory in the root which fulfills the requirements of `Game directories` below is treated
by the launcher as a game. Any other directories are ignored (you can keep your common code there
or whatever other support stuff you need.)


## Game directory
A game directory is any directory in the root which, after `build` has been run, contains the following:
* An executable file called `run`


## Game metadata
Optionally, a game directory may contain:
* `icon.png`, a square icon that is displayed in the game list
* `metadata.json`, as formatted below

The optional `metadata.json` file may contain information about the game, as displayed in the launcher.
```json
{
   "author" : "Nikola Tesla",
   "title"  : "Dine 'n' Dash"
}
```

## Game configuration
`game_config.json` in the launcher root should have the following format, and will be passed to all games
for a more unified experience:

```json
{
   "player1-color": "#ce3910",
   "player2-color": "#efef32",
   
   "controller1": {
      "device": "/dev/js0",
      
      "axis-X1": "ax1",
      "axis-Y1": "ax2",
      "axis-X2": "ax5",
      "axis-Y2": "ax6",
      
      "button-Y": "b4",
      "button-X": "b1",
      "button-B": "b3",
      "button-A": "b2",
      
      "dpad-up": "pov-up",
      "dpad-down": "pov-down",
      "dpad-left": "pov-left",
      "dpad-right": "pov-right",
      
      "bumper-L": "b5",
      "bumper-R": "b7",
      "trigger-L": "b7",
      "trigger-R": "b8",
      
      "L3": "b11",
      "R3": "b12"
   },
   
   "controller2": {
      "device": "keyboard",

      "button-Y": "i",
      "button-X": "j",
      "button-B": "l",
      "button-A": "k",
      
      "dpad-up": "w",
      "dpad-down": "s",
      "dpad-left": "a",
      "dpad-right": "d",
      
      "bumper-L": "q",
      "bumper-R": "e",
      "trigger-L": "1",
      "trigger-R": "3",
      
      "L3": "z",
      "R3": "x"
   },
}
```

Button names follow the xbox order, i.e.
```
   Y
 X   B
   A
```

Some copy-and-paste input mappers for various languages will be available in `utils/`.

## Game execution
The `run` program in your game directory is invoked in the game directory by the launcher.
The command line contains exactly one argument, the path to the launcher's `game_config.json` with settings
the game should respect (if applicable).

## Game completion
The `run` program should output on stdout a JSON document of the following format:
```json
{
   "winner": 1,
   "exit": false
}
```
`winner` is 0 for draw, 1 for player 1, and 2 for player 2.

`exit` should be set if the player seems to want to stop playing, for example if `Esc` was pressed.
In this case, the launcher will stop spawning random games.
