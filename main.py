import jaclang
import pygame
from sprites import *
from config import *
from map import LevelManager
import sys
import os
import json

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = 0
        self.map_height = 0

    def apply(self, entity):
        return entity.rect.move(self.rect.x, self.rect.y)

    def set_map_size(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height

    def update(self, target):
        # Center the camera on the target (player)
        x = -target.rect.centerx + int(WIN_WIDTH / 2)
        y = -target.rect.centery + int(WIN_HEIGHT / 2)
        
        # Add bounds checking only if map size is set and map is larger than screen
        if self.map_width > 0 and self.map_height > 0:
            if self.map_width > WIN_WIDTH:
                x = min(0, x)  # Don't scroll past left edge
                x = max(-(self.map_width - WIN_WIDTH), x)  # Don't scroll past right edge
            else:
                x = 0  # Center small maps
                
            if self.map_height > WIN_HEIGHT:
                y = min(0, y)  # Don't scroll past top edge
                y = max(-(self.map_height - WIN_HEIGHT), y)  # Don't scroll past bottom edge
            else:
                y = 0  # Center small maps
        
        self.rect = pygame.Rect(x, y, self.width, self.height)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('8bitoperator_jve.ttf', 32)
        self.small_font = pygame.font.Font('8bitoperator_jve.ttf', 20)
        self.running = True
        self.won = False

        self.character_spritesheet = Spritesheet('img/character.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.enemy_spritesheet = Spritesheet('img/enemy.png')
        self.attack_spritesheet = Spritesheet('img/attack.png')
        self.intro_background = pygame.image.load('./img/introbackground.png')
        self.go_background = pygame.image.load('./img/gameover.png')
        
        # Initialize the level manager
        self.level_manager = LevelManager()
        self.current_tilemap = None
        
        # Initialize camera
        self.camera = Camera(WIN_WIDTH, WIN_HEIGHT)
        
        # Initialize high score system
        self.high_score_file = 'high_score.json'
        self.high_score = self.load_high_score()

    def load_high_score(self):
        """Load high score from file, return 0 if file doesn't exist"""
        try:
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            with open(self.high_score_file, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def update_high_score(self):
        """Update high score if current level is higher"""
        current_level = self.level_manager.get_current_level()
        if current_level > self.high_score:
            self.high_score = current_level
            self.save_high_score()
    
    def draw_high_score(self):
        """Draw high score in top right corner"""
        high_score_text = self.small_font.render(f'High Score: {self.high_score}', True, WHITE)
        high_score_rect = high_score_text.get_rect()
        high_score_rect.topright = (WIN_WIDTH - 10, 10)
        self.screen.blit(high_score_text, high_score_rect)
    
    def draw_current_score(self):
        """Draw current level score below high score"""
        current_level = self.level_manager.get_current_level()
        current_score_text = self.small_font.render(f'Level: {current_level}', True, YELLOW)
        current_score_rect = current_score_text.get_rect()
        current_score_rect.topright = (WIN_WIDTH - 10, 35)  # 25 pixels below high score
        self.screen.blit(current_score_text, current_score_rect)

    def createTilemap(self):
        # Get the current tilemap from level manager
        if self.current_tilemap is None:
            self.current_tilemap = self.level_manager.get_next_tilemap()
        
        for i, row in enumerate(self.current_tilemap):
            for j, column in enumerate(row):
                Ground(self,j,i)
                if column == "B":
                    Block(self, j, i)
                if column == "E":
                    Enemy(self, j, i)
                if column == "P":
                    self.player = Player(self, j, i)

    def new(self):
        self.playing = True
        self.won = False

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        # Get a new tilemap for this level
        self.current_tilemap = self.level_manager.get_next_tilemap()
        self.createTilemap()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            
            keys =pygame.key.get_pressed()

            
            if keys[pygame.K_SPACE]:
                if self.player.facing == 'up':
                    Attack(self, self.player.rect.x, self.player.rect.y - TILESIZE)
                if self.player.facing == 'down':
                    Attack(self, self.player.rect.x, self.player.rect.y + TILESIZE)
                if self.player.facing == 'right':
                    Attack(self, self.player.rect.x + TILESIZE, self.player.rect.y)
                if self.player.facing == 'left':
                    Attack(self, self.player.rect.x - TILESIZE, self.player.rect.y)
    
    def update(self):
        self.all_sprites.update()
        # Update camera to follow player
        self.camera.update(self.player)
    
    def draw(self):
        self.screen.fill(BLACK)
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        # Draw high score and current score in top right corner
        self.draw_high_score()
        self.draw_current_score()
        
        self.clock.tick(FPS)
        pygame.display.update()


    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
            if len(self.enemies.sprites()) == 0:
                self.won = True
                self.playing = False
        if self.won == False:
            self.playing = False
                

    def game_over(self):
        text = self.font.render('GaMe OvEr', True, RED)
        text_rect = text.get_rect(center = (WIN_WIDTH/2, WIN_HEIGHT/2))

        restart_button = Button(10,WIN_HEIGHT-135, 120, 125, WHITE, BLACK, 'Restart', 32)
        
        for sprite in self.all_sprites:
            sprite.kill()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed)   :
                self.won = False
                self.level_manager.reset()  # Reset level manager when restarting
                self.new()
                # self.main()
                break

            self.screen.blit(self.go_background, (0,0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            
            # Draw high score and current score on game over screen
            self.draw_high_score()
            self.draw_current_score()
            
            self.clock.tick(FPS)
            pygame.display.update()     

    def intro_screen(self):
        intro = True

        title = self.font.render('Spud-nik : SOLO', True, BLUE)
        title_rect = title.get_rect(x=WIN_WIDTH/2-100,y=100)

        play_button = Button(WIN_WIDTH/2-50, 200, 100, 100, WHITE, BLACK, 'Play', 32)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
            
            self.screen.blit(self.intro_background, (0,0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            
            # Draw high score and current score on intro screen
            self.draw_high_score()
            self.draw_current_score()
            
            self.clock.tick(FPS)
            pygame.display.update()

    def game_won(self):
            # Update high score when level is completed
            self.update_high_score()
            
            text = self.font.render('LEVEL COMPLETE!', True, BLUE)
            text_rect = text.get_rect(center = (WIN_WIDTH/2, WIN_HEIGHT/2 - 50))
            
            level_text = self.font.render(f'Level {self.level_manager.get_current_level()}', True, WHITE)
            level_rect = level_text.get_rect(center = (WIN_WIDTH/2, WIN_HEIGHT/2 - 10))

            next_button = Button(WIN_WIDTH/2-75, WIN_HEIGHT/2+50, 150, 50, WHITE, BLACK, 'Next Level', 24)
            restart_button = Button(10,WIN_HEIGHT-135, 120, 125, WHITE, BLACK, 'Restart', 32)
            
            for sprite in self.all_sprites:
                sprite.kill()
            
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()

                if next_button.is_pressed(mouse_pos, mouse_pressed):
                    self.new()  # This will automatically get the next tilemap
                    break
                    
                if restart_button.is_pressed(mouse_pos, mouse_pressed):
                    self.level_manager.reset()  # Reset level manager when restarting
                    self.new()
                    break
                    

                self.screen.blit(self.intro_background, (0,0))
                self.screen.blit(text, text_rect)
                self.screen.blit(level_text, level_rect)
                self.screen.blit(next_button.image, next_button.rect)
                self.screen.blit(restart_button.image, restart_button.rect)
                
                # Draw high score and current score on level complete screen
                self.draw_high_score()
                self.draw_current_score()
                
                self.clock.tick(FPS)
                pygame.display.update()  

        


g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    if g.won == True:
        print(g.won)
        g.game_won()
    else:
        print(g.won)
        g.game_over()

pygame.quit()
sys.exit()
