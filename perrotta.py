import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falling Squares")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 48)

high_score = 0

def menu():
    while True:
        clock.tick(60)
        screen.fill(WHITE)

        title = big_font.render("FALLING SQUARES", True, BLACK)
        play_text = font.render("GIOCA", True, BLACK)
        score_text = font.render(f"Punteggio massimo: {high_score}", True, BLACK)

        play_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 40)

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        pygame.draw.rect(screen, GRAY, play_rect)
        screen.blit(play_text, (play_rect.centerx - play_text.get_width()//2,
                                 play_rect.centery - play_text.get_height()//2))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2,
                                 play_rect.bottom + 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    game()

        pygame.display.update()

def game():
    global high_score

    player_size = 40
    player_x = WIDTH / 2
    player_y = HEIGHT - 60
    player_speed = 6.5

    enemy_size = 40
    base_enemy_speed = 2.5
    enemies = []

    def new_enemy():
        x = random.randint(0, WIDTH - enemy_size)
        y = random.randint(-400, -40)
        return {"rect": pygame.Rect(x, y, enemy_size, enemy_size), "y": float(y)}

    enemies.append(new_enemy())

    score = 0
    running = True

    while running:
        dt = clock.tick(60) / 1000
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed * 60 * dt
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed * 60 * dt

        player_rect = pygame.Rect(int(player_x), int(player_y),
                                  player_size, player_size)

        enemy_speed = base_enemy_speed + score * 0.05

        for enemy in enemies:
            enemy["y"] += enemy_speed * 60 * dt
            enemy["rect"].y = int(enemy["y"])

            if enemy["rect"].y > HEIGHT:
                enemy["y"] = random.randint(-400, -40)
                enemy["rect"].x = random.randint(0, WIDTH - enemy_size)
                score += 1

                if score % 4 == 0:
                    enemies.append(new_enemy())

            if player_rect.colliderect(enemy["rect"]):
                running = False

            pygame.draw.rect(screen, RED, enemy["rect"])

        pygame.draw.rect(screen, BLUE, player_rect)
        score_text = font.render(f"Punteggio: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

    if score > high_score:
        high_score = score

    screen.fill(WHITE)
    game_over = big_font.render("GAME OVER", True, RED)
    final_score = font.render(f"Punteggio: {score}", True, BLACK)
    back_text = font.render("Ritorno al menu...", True, BLACK)

    screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, 130))
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 190))
    screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, 240))

    pygame.display.update()
    pygame.time.wait(2500)

menu()
