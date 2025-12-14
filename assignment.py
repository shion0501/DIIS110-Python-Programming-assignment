


import pygame
import random
import sys


WIDTH, HEIGHT = 640, 480
FPS = 60


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 20, 60)
GREEN = (50, 205, 50)
ORANGE = (255, 140, 0)
YELLOW = (255, 215, 0)
GRAY = (200, 200, 200)


PLAYER_WIDTH, PLAYER_HEIGHT = 80, 20
PLAYER_SPEED = 6


FALL_WIDTH, FALL_HEIGHT = 28, 28
INITIAL_FALL_SPEED = 3
FALL_SPAWN_INTERVAL = 800  


STARTING_LIVES = 3


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Catcher")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 40)

FALL_TYPES = ['apple', 'orange', 'banana', 'bomb']
FRUIT_COLORS = {
    'apple': RED,
    'orange': ORANGE,
    'banana': YELLOW,
}


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 10)
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

class Falling(pygame.sprite.Sprite):
    def __init__(self, kind, speed):
        super().__init__()
        self.kind = kind  # 'apple', 'orange', 'banana', 'bomb'
        self.image = pygame.Surface((FALL_WIDTH, FALL_HEIGHT), pygame.SRCALPHA)
        if kind == 'bomb':

            pygame.draw.circle(self.image, BLACK, (FALL_WIDTH//2, FALL_HEIGHT//2), FALL_WIDTH//2)

            pygame.draw.circle(self.image, (255, 120, 0), (FALL_WIDTH//2, 6), 4)
        else:
            color = FRUIT_COLORS.get(kind, GREEN)
            pygame.draw.ellipse(self.image, color, (0, 0, FALL_WIDTH, FALL_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - FALL_WIDTH)
        self.rect.y = -FALL_HEIGHT
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

        if self.rect.top > HEIGHT:
            self.kill()


def main():
    running = True
    paused = False


    player = Player()
    player_group = pygame.sprite.Group(player)
    fall_group = pygame.sprite.Group()

    score = 0
    lives = STARTING_LIVES
    fall_speed = INITIAL_FALL_SPEED
    last_spawn = pygame.time.get_ticks()


    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused

        if paused:
            draw_pause(screen, score, lives)
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        player_group.update(keys)


        now = pygame.time.get_ticks()
        spawn_interval = max(200, FALL_SPAWN_INTERVAL - (score * 5)) 
        if now - last_spawn > spawn_interval:
            kind = random.choices(FALL_TYPES, weights=[35, 30, 20, 15])[0] 
            falling = Falling(kind, fall_speed)
            fall_group.add(falling)
            last_spawn = now


        fall_group.update()


        collisions = pygame.sprite.spritecollide(player, fall_group, dokill=True)
        for item in collisions:
            if item.kind == 'bomb':
                lives -= 1

                flash_screen(screen)
            else:
                score += 10
        
                if score % 50 == 0:
                    fall_speed += 0.6

        if lives <= 0:
            game_over_screen(screen, score)

            running = False
            continue


        screen.fill((135, 206, 235))  
     
        pygame.draw.rect(screen, (34,139,34), (0, HEIGHT - 40, WIDTH, 40))
        player_group.draw(screen)
        fall_group.draw(screen)

   
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        draw_hud(screen, score, lives, elapsed)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def draw_hud(surface, score, lives, elapsed_seconds):
    score_surf = font.render(f"Score: {score}", True, BLACK)
    lives_surf = font.render(f"Lives: {lives}", True, BLACK)
    time_surf  = font.render(f"Time: {elapsed_seconds}s", True, BLACK)
    surface.blit(score_surf, (10, 10))
    surface.blit(lives_surf, (10, 34))
    surface.blit(time_surf, (WIDTH - 120, 10))
    hint = font.render("P: Pause   Esc: Quit", True, BLACK)
    surface.blit(hint, (WIDTH - 200, HEIGHT - 30))

def draw_pause(surface, score, lives):

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,120))
    surface.blit(overlay, (0,0))
    text = big_font.render("Paused", True, WHITE)
    sub = font.render(f"Score: {score}    Lives: {lives}", True, WHITE)
    surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
    surface.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

def flash_screen(surface):

    flash = pygame.Surface((WIDTH, HEIGHT))
    flash.fill((255, 100, 100))
    surface.blit(flash, (0,0))
    pygame.display.flip()
    pygame.time.delay(120)

def game_over_screen(surface, score):
    surface.fill((20, 20, 20))
    text = big_font.render("Game Over", True, RED)
    sub = font.render(f"Final Score: {score}", True, WHITE)
    tip = font.render("Press any key to exit...", True, WHITE)
    surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
    surface.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
    surface.blit(tip, tip.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
    pygame.display.flip()

    waiting = True
    while waiting:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                waiting = False
            elif evt.type == pygame.KEYDOWN or evt.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        pygame.time.wait(100)


if __name__ == "__main__":
    main()