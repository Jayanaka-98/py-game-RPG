import random
import json
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Wall:
    start_pos: Position
    end_pos: Position

@dataclass
class Map:
    walls: List[Wall]
    small_obstacles: List[Position]
    enemies: List[Position]
    player_pos: Position
    width: int
    height: int

    def serialize(self) -> List[str]:
        # Create a map with the specified dimensions
        ret = [['.' for _ in range(self.width)] for _ in range(self.height)]
        
        # Fill the borders with blocks
        for i in range(self.height):
            ret[i][0] = 'B'  # Left border
            ret[i][self.width - 1] = 'B'  # Right border
        for j in range(self.width):
            ret[0][j] = 'B'  # Top border
            ret[self.height - 1][j] = 'B'  # Bottom border
        
        # Place walls
        for wall in self.walls:
            if 0 <= wall.start_pos.x < self.width and 0 <= wall.start_pos.y < self.height:
                ret[wall.start_pos.y][wall.start_pos.x] = 'B'
            if 0 <= wall.end_pos.x < self.width and 0 <= wall.end_pos.y < self.height:
                ret[wall.end_pos.y][wall.end_pos.x] = 'B'
        
        # Place small obstacles
        for obstacle in self.small_obstacles:
            if 0 <= obstacle.x < self.width and 0 <= obstacle.y < self.height:
                ret[obstacle.y][obstacle.x] = 'B'
        
        # Place enemies
        for enemy in self.enemies:
            if 0 <= enemy.x < self.width and 0 <= enemy.y < self.height:
                ret[enemy.y][enemy.x] = 'E'
        
        # Place player
        if 0 <= self.player_pos.x < self.width and 0 <= self.player_pos.y < self.height:
            ret[self.player_pos.y][self.player_pos.x] = 'P'
        
        return [''.join(row) for row in ret]

def load_maps_from_json(json_file_path: str) -> List[Map]:
    """Load maps from a JSON file and convert them to Map objects"""
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    maps = []
    for map_data in data['maps']:
        # Convert position dictionaries to Position objects
        player_pos = Position(map_data['player_pos']['x'], map_data['player_pos']['y'])
        
        enemies = [Position(enemy['x'], enemy['y']) for enemy in map_data['enemies']]
        
        small_obstacles = [Position(obs['x'], obs['y']) for obs in map_data['small_obstacles']]
        
        walls = []
        for wall_data in map_data['walls']:
            start_pos = Position(wall_data['start_pos']['x'], wall_data['start_pos']['y'])
            end_pos = Position(wall_data['end_pos']['x'], wall_data['end_pos']['y'])
            walls.append(Wall(start_pos, end_pos))
        
        # Create Map object
        map_obj = Map(
            walls=walls,
            small_obstacles=small_obstacles,
            enemies=enemies,
            player_pos=player_pos,
            width=map_data['width'],
            height=map_data['height']
        )
        maps.append(map_obj)
    
    return maps

class LevelManager:
    def __init__(self, maps_json_path: str = "maps.json"):
        # Load maps from JSON file
        try:
            # Try to load from the same directory as this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, maps_json_path)
            self.maps = load_maps_from_json(json_path)
        except FileNotFoundError:
            # Fallback to current working directory
            self.maps = load_maps_from_json(maps_json_path)
        
        self.current_level = 0
        self.used_maps = []
    
    def get_next_tilemap(self):
        """
        Returns a serialized tilemap from the available Map objects.
        If all maps have been used, it resets and allows reuse of maps.
        """
        # If all maps have been used, reset the used_maps list
        if len(self.used_maps) >= len(self.maps):
            self.used_maps = []
        
        # Get available maps (those not yet used)
        available_maps = [i for i in range(len(self.maps)) if i not in self.used_maps]
        
        # Randomly select a map index from available maps
        selected_index = random.choice(available_maps)
        
        # Mark this map as used
        self.used_maps.append(selected_index)
        
        # Increment level counter
        self.current_level += 1
        
        # Return the serialized map
        return self.maps[selected_index].serialize()
    
    def get_current_level(self):
        """Returns the current level number"""
        return self.current_level
    
    def reset(self):
        """Resets the level manager to initial state"""
        self.current_level = 0
        self.used_maps = []
