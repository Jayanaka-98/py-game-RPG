tilemap = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B..E...............B',
    'B..................B',
    'B....BBBB......E...B',
    'B..................B',
    'B..................B',
    'B.........P........B',
    'B..................B',
    'B....E.............B',
    'B..................B',
    'B.......BBB........B',
    'B.........B........B',
    'B.........B....E...B',
    'B.........B........B',
    'BBBBBBBBBBBBBBBBBBBB'

]

tilemap_3 = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B..........E.......B',
    'B..................B',
    'B.......BBBB.......B',
    'B......E...........B',
    'B..................B',
    'B...E..............B',
    'B..................B',
    'B..BBBBB...........B',
    'B.........E........B',
    'B..................B',
    'B............P.....B',
    'B..................B',
    'B.......E..........B',
    'BBBBBBBBBBBBBBBBBBBB'
]

tilemap_4 = [
    'BBBBBBBBBBBBBBBBBBB',
    'B........E........B',
    'B.BBBBBBB.BBBBBBB.B',
    'B.B..P..B.B.....B.B',
    'B.B.BBB.B.B.BBB.B.B',
    'B.B.B...B...B.B.B.B',
    'B.B.B.BBBBB.B.B.B.B',
    'B.B.B.......B.B.B.B',
    'B.B.B.BBB.BBB.B.B.B',
    'B.B...B...B...B.B.B',
    'B.BBB.BBB.BBB.BBB.B',
    'B...B...EEE......B.',
    'BBB.BBB.B.BBB.BBB.B',
    'B.....B...B.....B.B',
    'BBBBBBBBBBBBBBBBBBB'
]

tilemap_5 = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B........E.........B',
    'B..BBBB............B',
    'B..B...............B',
    'B..B........E......B',
    'B..B...............B',
    'B..B.....BBBB......B',
    'B..B..........E....B',
    'B..B...............B',
    'B..B...............B',
    'B..B........P......B',
    'B..B...............B',
    'B..BBBB............B',
    'B.....E............B',
    'BBBBBBBBBBBBBBBBBBBB'
]

tilemap_6 = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B.......E..........B',
    'BB.BB.BB.BB.BB.BB.BB',
    'B..B............B..B',
    'BB.B..BB.BB.BB.B..BB',
    'B.............E....B',
    'BBBB..BB.BB.BB.BB.BB',
    'B..B............B..B',
    'B.BBBBB.BB.BB.BB.BBB',
    'B.....E...........PB',
    'BB.BB.BB.BB.BB.BB.BB',
    'B..B............B..B',
    'BB.BB.BB.BB.BB.BB.BB',
    'B.............E....B',
    'BBBBBBBBBBBBBBBBBBBB'
]

import random

class LevelManager:
    def __init__(self):
        # Store all available tilemaps
        self.tilemaps = [
            tilemap,
            tilemap_3,
            tilemap_4,
            tilemap_5,
            tilemap_6
        ]
        self.current_level = 0
        self.used_maps = []
    
    def get_next_tilemap(self):
        """
        Returns a randomly selected tilemap from the available maps.
        If all maps have been used, it resets and allows reuse of maps.
        """
        # If all maps have been used, reset the used_maps list
        if len(self.used_maps) >= len(self.tilemaps):
            self.used_maps = []
        
        # Get available maps (those not yet used)
        available_maps = [i for i in range(len(self.tilemaps)) if i not in self.used_maps]
        
        # Randomly select a map index from available maps
        selected_index = random.choice(available_maps)
        
        # Mark this map as used
        self.used_maps.append(selected_index)
        
        # Increment level counter
        self.current_level += 1
        
        return self.tilemaps[selected_index]
    
    def get_current_level(self):
        """Returns the current level number"""
        return self.current_level
    
    def reset(self):
        """Resets the level manager to initial state"""
        self.current_level = 0
        self.used_maps = []
