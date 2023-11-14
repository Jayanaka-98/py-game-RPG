# Python based RPG game development using pygame

[Demo Video.webm](https://github.com/Jayanaka-98/py-game-RPG/assets/110921856/1ac069eb-7a07-462f-82fe-a8c1e3481935)


This source code represents a python coded video game which has been coded using "pygame". This game is an RPG type game with attack elements and map gnerations. The code was developed by following a step by step tutorial done by "ShawCode". 

[Link to Tutorial](https://www.youtube.com/watch?v=crUF36OkGDw&list=PLkkm3wcQHjT7gn81Wn-e78cAyhwBW3FIc&pp=iAQB) 

## Setting Up

Create your own virtual environment which will be compatible with the source code. Clone this repo and open a terminal and bas the following (Assuming you have conda already installed).

'''
conda create --name py-games --file requirements.txt
'''

This will install the necessary packages required for the sorce code.

## Trying the game

To try the game, open the "main.py" file and run the code.

## Code Breakdown

### main.py

This file contains the main game code which describes the functionality of the game. 

### sprites.py

All in game sprite models are created within this code. 

### config.py

Configuration parameters such as windowsize. layer order is stored inthis file.

### map.py

Contains the map of the game which can be changed as required.

- B : Blocks (Walls)
- E : Enemy Spawn Point
- P : Player Spawn Point
