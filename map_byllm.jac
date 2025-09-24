import from byllm { Model }

obj Position {
    has x: int;
    has y: int;
}

obj MapTiles {
    has width: int;
    has height: int;
    has walls: list[Position];
    has enemies: list[Position];
    has player_pos: Position;

    def serialize() -> list[str] {
        # Create a map with additional border (width+2, height+2)
        bordered_width = self.width + 2;
        bordered_height = self.height + 2;
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
            if wall.x >= 0 and wall.x < self.width and wall.y >= 0 and wall.y < self.height {
                ret[wall.y + 1][wall.x + 1] = 'B';
            }
        }
        for enemy in self.enemies {
            if enemy.x >= 0 and enemy.x < self.width and enemy.y >= 0 and enemy.y < self.height {
                ret[enemy.y + 1][enemy.x + 1] = 'E';
            }
        }
        if self.player_pos.x >= 0 and self.player_pos.x < self.width and self.player_pos.y >= 0 and self.player_pos.y < self.height {
            ret[self.player_pos.y + 1][self.player_pos.x + 1] = 'P';
        }
        
        return [''.join(row) for row in ret];
    }
}

# sem MapTiles.enemies = "Enemy positions reachable by player";
# sem MapTiles.player_pos = "Starting position of the player";
# sem LevelManager.difficulty = "Difficulty level affecting map generation complexity";
sem LevelManager.used_maps = "List of previously played maps to avoid repetition and to identify player capabilities";


obj LevelManager {
    has current_level: int = 0;
    has difficulty: int = 1;
    has used_maps: list[MapTiles] = [];
    has llm: Model = Model("gpt-4o-mini", temperature=0.7);

    def generate_next_level_map() -> MapTiles by self.llm();

    def get_next_tilemap() -> list[str]{
        self.current_level += 1;
        self.difficulty += 3;
        new_map = self.generate_next_level_map();
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