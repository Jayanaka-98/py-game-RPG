import from byllm { Model }

obj Position {
    has x: int;
    has y: int;
}

obj Wall {
    has start_pos: Position;
    has end_pos: Position;
}

obj Level {
    has name: str, difficulty: int;
    has width: int, height: int, num_wall: int, num_enemies: int;
    has time_countdown: int, n_retries_allowed: int;
}

obj Map {
    has level: Level, walls: list[Wall], small_obstacles: list[Position];
    has enemies: list[Position];
    has player_pos: Position;

    def serialize() -> list[str] {
        # Create a map with additional border (width+2, height+2)
        bordered_width = self.level.width + 2;
        bordered_height = self.level.height + 2;
        ret = [['.'] * bordered_width for _ in range(bordered_height)];
        
        # Fill the entire border with blocks
        for i in range(bordered_height) {
            ret[i][0] = 'B';  # Left border
            ret[i][bordered_width - 1] = 'B';  # Right border
        }
        for j in range(bordered_width) {
            ret[0][j] = 'B';  # Top border
            ret[bordered_height - 1][j] = 'B';  # Bottom border
        }
        
        # Place walls, enemies, and player with offset (+1 for the border)
        for wall in self.walls {
            # Walls have start_pos and end_pos, let's place blocks for both positions
            if wall.start_pos.x >= 0 and wall.start_pos.x < self.level.width and wall.start_pos.y >= 0 and wall.start_pos.y < self.level.height {
                ret[wall.start_pos.y + 1][wall.start_pos.x + 1] = 'B';
            }
            if wall.end_pos.x >= 0 and wall.end_pos.x < self.level.width and wall.end_pos.y >= 0 and wall.end_pos.y < self.level.height {
                ret[wall.end_pos.y + 1][wall.end_pos.x + 1] = 'B';
            }
        }
        
        # Place small obstacles
        for obstacle in self.small_obstacles {
            if obstacle.x >= 0 and obstacle.x < self.level.width and obstacle.y >= 0 and obstacle.y < self.level.height {
                ret[obstacle.y + 1][obstacle.x + 1] = 'B';
            }
        }
        
        for enemy in self.enemies {
            if enemy.x >= 0 and enemy.x < self.level.width and enemy.y >= 0 and enemy.y < self.level.height {
                ret[enemy.y + 1][enemy.x + 1] = 'E';
            }
        }
        if self.player_pos.x >= 0 and self.player_pos.x < self.level.width and self.player_pos.y >= 0 and self.player_pos.y < self.level.height {
            ret[self.player_pos.y + 1][self.player_pos.x + 1] = 'P';
        }
        
        return [''.join(row) for row in ret];
    }
}

sem MapTiles.enemies = "Enemy positions reachable by player";
sem MapTiles.player_pos = "Starting position of the player sprite, not enclosed by walls";
sem MapTiles.walls = "Wall positions that block player movement";
# sem LevelManager.difficulty = "Difficulty level affecting map generation complexity";
sem LevelManager.used_maps = "List of previously played maps to avoid repetition and to identify player capabilities";
sem LevelManager.generate_next_level_map = "Generates a new map based on current difficulty and previously used maps, where all enemies can be eliminated by traversing the maze";

obj LevelManager {
    has current_level: int = 0;
    has difficulty: int = 1;
    has used_maps: list[Map] = [];
    has llm: Model = Model("gpt-4o-mini", temperature=0.7);

    def design_level() -> Level by self.llm();
    def generate_next_level_map(level_design: Level) -> Map by self.llm();

    def get_starting_tilemap() -> list[str] {
        # Define the starting map - same as tilemap from map_static.py
        return [
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
        ];
    }

    def get_next_tilemap() -> list[str]{
        self.current_level += 1;
        
        # Use the predefined starting map for level 1
        if self.current_level == 1 {
            return self.get_starting_tilemap();
        }
        
        # For subsequent levels, generate new maps
        self.difficulty += 1;
        new_level_design = self.design_level();
        new_map = self.generate_next_level_map(new_level_design);
        self.used_maps.append(new_map);

        return new_map.serialize();
    }

    def get_current_level() -> int {
        return self.current_level;
    }

    def reset() {
        self.current_level = 0;
        self.used_maps = [];
    }
}