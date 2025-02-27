import pygame
import sys

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Bros Clone")

# Set up clock (to control FPS)
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE  = (0, 0, 255)

# Font
font = pygame.font.Font(None, 36)

# Load Sounds (replace with your actual sound files)
try:
    jump_sound = pygame.mixer.Sound("jump.wav")
    stomp_sound = pygame.mixer.Sound("stomp.wav")
    game_over_sound = pygame.mixer.Sound("game_over.wav")
except Exception as e:
    print("Sound files not found, skipping sound effects.")
    jump_sound = stomp_sound = game_over_sound = None

# Mario settings
MARIO_WIDTH, MARIO_HEIGHT = 32, 32
mario_img = pygame.Surface((MARIO_WIDTH, MARIO_HEIGHT))
mario_img.fill(BLUE)

player_speed = 4
gravity = 0.6
jump_strength = -12
GROUND_Y = 500

# --- PLATFORM CLASS ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((139, 69, 19))
        self.rect = self.image.get_rect(topleft=(x, y))

# --- GOOMBA CLASS ---
class Goomba(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        # Align Goomba's bottom with the ground
        self.rect.bottom = GROUND_Y  
        self.speed = 2
        self.direction = 1
        print(f"Goomba spawned at: x={self.rect.x}, bottom={self.rect.bottom}, expected={GROUND_Y}")

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x <= 200 or self.rect.x >= 600:
            self.direction *= -1

# --- GAME OVER SCREEN FUNCTION ---
def game_over_screen(score):
    if game_over_sound:
        game_over_sound.play()
    while True:
        screen.fill(WHITE)
        text = font.render("Game Over!", True, BLACK)
        score_text = font.render("Score: " + str(score), True, BLACK)
        screen.blit(text, (WIDTH // 2 - 50, HEIGHT // 3))
        screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 3 + 40))
        play_button = pygame.Rect(WIDTH // 3, HEIGHT // 2, 150, 50)
        quit_button = pygame.Rect(WIDTH // 3 * 2 - 50, HEIGHT // 2, 150, 50)
        pygame.draw.rect(screen, GREEN, play_button)
        pygame.draw.rect(screen, RED, quit_button)
        play_text = font.render("Play Again", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)
        screen.blit(play_text, (play_button.x + 20, play_button.y + 10))
        screen.blit(quit_text, (quit_button.x + 50, quit_button.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# --- GAME FUNCTION (with Score and In-Game Start Again Button) ---
def run_game():
    mario_rect = mario_img.get_rect()
    mario_rect.x = 50
    mario_rect.bottom = GROUND_Y

    velocity_y = 0
    is_jumping = False
    score = 0

    platforms = pygame.sprite.Group()
    platforms.add(Platform(300, 400, 100, 20))
    platforms.add(Platform(500, 300, 120, 20))

    enemies = pygame.sprite.Group()
    enemies.add(Goomba(400))

    running = True
    while running:
        clock.tick(FPS)
        
        # Create the "Start Again" button at the start of each frame
        start_button = pygame.Rect(10, 10, 120, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return  # Restart game when the button is clicked

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            mario_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            mario_rect.x += player_speed
        if keys[pygame.K_SPACE] and not is_jumping:
            velocity_y = jump_strength
            is_jumping = True
            if jump_sound:
                jump_sound.play()

        velocity_y += gravity
        mario_rect.y += velocity_y

        # Ground collision
        if mario_rect.bottom >= GROUND_Y:
            mario_rect.bottom = GROUND_Y
            is_jumping = False
            velocity_y = 0

        for platform in platforms:
            if mario_rect.colliderect(platform.rect) and velocity_y > 0:
                mario_rect.bottom = platform.rect.top
                is_jumping = False
                velocity_y = 0

        for enemy in enemies:
            if mario_rect.colliderect(enemy.rect):
                if velocity_y > 0 and mario_rect.bottom <= enemy.rect.bottom + 5:
                    enemies.remove(enemy)
                    score += 100
                    velocity_y = jump_strength
                    if stomp_sound:
                        stomp_sound.play()
                else:
                    game_over_screen(score)
                    return

        enemies.update()

        screen.fill((135, 206, 250))
        screen.blit(mario_img, mario_rect)
        platforms.draw(screen)
        enemies.draw(screen)

        pygame.draw.rect(screen, GREEN, start_button)
        start_text = font.render("Start Again", True, BLACK)
        screen.blit(start_text, (start_button.x + 10, start_button.y + 10))

        score_text = font.render("Score: " + str(score), True, BLACK)
        screen.blit(score_text, (WIDTH - 150, 10))

        pygame.display.flip()

while True:
    run_game()
