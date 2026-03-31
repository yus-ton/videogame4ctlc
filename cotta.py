import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack-a-Mole")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (120, 70, 15)
GRAY = (90, 90, 90)
DARK_RED = (139, 0, 0)
RED = (200, 0, 0)

font = pygame.font.SysFont(None, 30)

TOP_MARGIN = 60

COLS = 5
ROWS = 4
HOLE_RADIUS = 35

CELL_WIDTH = WIDTH // COLS
CELL_HEIGHT = (HEIGHT - TOP_MARGIN) // ROWS

HOLE_POSITIONS = [
    (c * CELL_WIDTH + CELL_WIDTH // 2,
     TOP_MARGIN + r * CELL_HEIGHT + CELL_HEIGHT // 2)
    for r in range(ROWS)
    for c in range(COLS)
]

mole_image = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(mole_image, DARK_RED, (20, 20), 20)

bomb_image = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(bomb_image, RED, (20, 20), 20)
pygame.draw.circle(bomb_image, BLACK, (20, 20), 20, 2)

hammer_image = pygame.Surface((60, 60), pygame.SRCALPHA)
pygame.draw.rect(hammer_image, BROWN, (26, 18, 8, 34))
pygame.draw.rect(hammer_image, GRAY, (10, 6, 40, 14))

hammer_rect = hammer_image.get_rect()
hammer_angle = 0
hammer_hit_time = 0

MAX_LEVEL = 10
level = 1
hits_required = level * 5
hits_in_level = 0

game_time = 30
start_time = time.time()

mole_time_interval = 1.5
last_spawn_time = 0

moles = []
bombs = []

pygame.mouse.set_visible(False)
running = True

def draw_holes():
    for pos in HOLE_POSITIONS:
        pygame.draw.circle(screen, BLACK, pos, HOLE_RADIUS)

def draw_entities():
    for pos in moles:
        screen.blit(mole_image, mole_image.get_rect(center=pos))
    for pos in bombs:
        screen.blit(bomb_image, bomb_image.get_rect(center=pos))

def draw_ui(remaining):
    screen.blit(font.render(f"Level: {level}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Hits: {hits_in_level}/{hits_required}", True, BLACK), (120, 10))
    screen.blit(font.render(f"Time: {remaining}", True, BLACK), (450, 10))

while running:
    elapsed_time = time.time() - start_time
    remaining_time = game_time - int(elapsed_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEMOTION:
            hammer_rect.center = event.pos

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hammer_angle = -45
            hammer_hit_time = time.time()

            # Controllo talpe
            for pos in moles[:]:
                if hammer_rect.collidepoint(pos):
                    hits_in_level += 1
                    moles.remove(pos)

            # Controllo bombe
            for pos in bombs[:]:
                if hammer_rect.collidepoint(pos):
                    hits_in_level = max(0, hits_in_level - 1)
                    bombs.remove(pos)

    if time.time() - hammer_hit_time > 0.15:
        hammer_angle = 0

    # Spawn entità
    if time.time() - last_spawn_time >= mole_time_interval:
        last_spawn_time = time.time()
        moles.clear()
        bombs.clear()

        mole_count = 1
        if level >= 5:
            mole_count = min(3, 1 + (level - 4))

        positions = random.sample(HOLE_POSITIONS, mole_count + (1 if level >= 7 else 0))

        moles = positions[:mole_count]

        if level >= 7:
            bombs.append(positions[-1])

    # Livello completato
    if hits_in_level >= hits_required:
        level += 1
        if level > MAX_LEVEL:
            break

        hits_required = level * 5
        hits_in_level = 0
        start_time = time.time()
        mole_time_interval = max(0.6, mole_time_interval - 0.1)

    # Tempo scaduto
    if remaining_time <= 0:
        break

    # Disegno
    screen.fill(WHITE)
    draw_ui(remaining_time)
    draw_holes()
    draw_entities()

    rotated_hammer = pygame.transform.rotate(hammer_image, hammer_angle)
    rotated_rect = rotated_hammer.get_rect(center=hammer_rect.center)
    screen.blit(rotated_hammer, rotated_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
