import pygame
import random
import sys

# --- CONFIGURAZIONE ---
WIDTH, HEIGHT = 800, 800
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter: Mission Completion")
clock = pygame.time.Clock()

# --- ASSETS ---
def load_image(name, scale=None):
    try:
        img = pygame.image.load(name).convert_alpha()
        if scale: img = pygame.transform.scale(img, scale)
        return img
    except:
        surf = pygame.Surface(scale if scale else (50, 50))
        surf.fill((255, 0, 0))
        return surf

player_img = load_image("player.png", (50, 50))
asteroid_img = load_image("asteroid.png", (40, 40))
enemy_img = load_image("enemy_ship.png", (50, 50))
bullet_img = load_image("bullet.png", (10, 20))

# Esplosione
explosion_sheet = load_image("explosion.png")
explosion_frames = []
if explosion_sheet:
    fw = explosion_sheet.get_width() // 5
    fh = explosion_sheet.get_height()
    for i in range(5):
        explosion_frames.append(explosion_sheet.subsurface((i * fw, 0, fw, fh)))

# Font
font_big = pygame.font.SysFont("Arial", 70, bold=True)
font_mid = pygame.font.SysFont("Arial", 40, bold=True)
font_small = pygame.font.SysFont("Arial", 25, bold=True)
font_tiny = pygame.font.SysFont("Arial", 20)

def draw_text(text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center: rect.center = (x, y)
    else: rect.topleft = (x, y)
    screen.blit(surf, rect)

# --- CLASSI ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-80))
        self.speed = 6
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed
        if keys[pygame.K_SPACE]: self.shoot()
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            b = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(b); player_bullets.add(b)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), -50))
        self.target = target
        self.speed_y = 2; self.speed_x = 2; self.hp = 3
        self.last_shot = pygame.time.get_ticks()
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.centerx < self.target.rect.centerx: self.rect.x += self.speed_x
        elif self.rect.centerx > self.target.rect.centerx: self.rect.x -= self.speed_x
        now = pygame.time.get_ticks()
        if now - self.last_shot > 2000:
            self.last_shot = now
            eb = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(eb); enemy_bullets.add(eb)
        if self.rect.top > HEIGHT: self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = asteroid_img
        self.rect = self.image.get_rect(midtop=(random.randint(0, WIDTH), -40))
        self.speed = speed; self.hp = 3
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(midbottom=(x, y))
    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0: self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.rotate(bullet_img, 180)
        self.rect = self.image.get_rect(midtop=(x, y))
    def update(self):
        self.rect.y += 7
        if self.rect.top > HEIGHT: self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = explosion_frames; self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)
        self.last_update = pygame.time.get_ticks()
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now; self.index += 1
            if self.index >= len(self.frames): self.kill()
            else: self.image = self.frames[self.index]

# --- LOGICA GRUPPI ---
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

SPAWN_ASTEROID = pygame.USEREVENT + 1
SPAWN_ENEMY = pygame.USEREVENT + 2

def reset_game():
    all_sprites.empty(); asteroids.empty(); player_bullets.empty()
    enemy_bullets.empty(); enemies.empty()
    p = Player(); all_sprites.add(p)
    return p

# STATI DI GIOCO
MENU, GAME, GAMEOVER, WIN = 0, 1, 2, 3
state, score, player = MENU, 0, None

# Difficoltà
ast_speed_min, ast_speed_max = 3, 5
ast_spawn_rate, en_spawn_rate = 1200, 5000
last_ast_upd, last_en_upd = 0, 0

# --- LOOP PRINCIPALE ---
while True:
    screen.fill((5, 5, 20))
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if state == MENU and event.type == pygame.KEYDOWN:
            player = reset_game(); score = 0
            ast_speed_min, ast_speed_max = 3, 5
            ast_spawn_rate, en_spawn_rate = 1200, 5000
            last_ast_upd, last_en_upd = now, now
            pygame.time.set_timer(SPAWN_ASTEROID, ast_spawn_rate)
            pygame.time.set_timer(SPAWN_ENEMY, en_spawn_rate)
            state = GAME
        
        elif (state == GAMEOVER or state == WIN) and event.type == pygame.KEYDOWN:
            state = MENU

        if state == GAME:
            if event.type == SPAWN_ASTEROID:
                a = Asteroid(random.randint(int(ast_speed_min), int(ast_speed_max)))
                all_sprites.add(a); asteroids.add(a)
            if event.type == SPAWN_ENEMY:
                en = Enemy(player); all_sprites.add(en); enemies.add(en)

    if state == MENU:
        if state == MENU:
            draw_text("SPACE SHOOTER", font_big, (255, 255, 255), WIDTH//2, HEIGHT//2 - 180, True)
            draw_text("Premi un tasto per iniziare", font_small, (255, 255, 0), WIDTH//2, HEIGHT//2 - 100, True)
            pygame.draw.rect(screen, (50, 50, 80), (WIDTH//2 - 200, HEIGHT//2 - 40, 400, 260), border_radius=15)
            draw_text("--- COMANDI ---", font_small, (0, 255, 255), WIDTH//2, HEIGHT//2, True)
            draw_text("Frecce: Muovi | Spazio: Spara", font_tiny, (255, 255, 255), WIDTH//2, HEIGHT//2 + 45, True)
            draw_text("--- PUNTI ---", font_small, (0, 255, 0), WIDTH//2, HEIGHT//2 + 90, True)
            draw_text("Asteroide: 10 | Nemico: 50", font_tiny, (255, 255, 255), WIDTH//2, HEIGHT//2 + 120, True)
            draw_text("Obiettivo: 2000 Punti per Vincere!", font_tiny, (255, 200, 0), WIDTH//2, HEIGHT//2 + 150, True)
            draw_text("Difficoltà aumenta col tempo!", font_tiny, (255, 100, 100), WIDTH//2, HEIGHT//2 + 180, True)        
    elif state == GAME:
        # Controllo Vittoria
        if score >= 2000:
            state = WIN

        # Update Difficoltà
        if now - last_ast_upd > 10000:
            last_ast_upd = now; ast_speed_min += 0.5; ast_speed_max += 0.5
            ast_spawn_rate = max(300, ast_spawn_rate - 150)
            pygame.time.set_timer(SPAWN_ASTEROID, ast_spawn_rate)
        if now - last_en_upd > 15000:
            last_en_upd = now; en_spawn_rate = max(1500, en_spawn_rate - 500)
            pygame.time.set_timer(SPAWN_ENEMY, en_spawn_rate)

        all_sprites.update()
        
        # Collisioni
        hits = pygame.sprite.groupcollide(asteroids, player_bullets, False, True)
        for a in hits:
            a.hp -= 1
            if a.hp <= 0: all_sprites.add(Explosion(a.rect.center)); score += 10; a.kill()
        
        en_hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for en in en_hits:
            en.hp -= 1
            if en.hp <= 0: all_sprites.add(Explosion(en.rect.center)); score += 50; en.kill()
        
        if pygame.sprite.spritecollide(player, asteroids, False) or \
           pygame.sprite.spritecollide(player, enemy_bullets, False) or \
           pygame.sprite.spritecollide(player, enemies, False):
            all_sprites.add(Explosion(player.rect.center))
            state = GAMEOVER

        all_sprites.draw(screen)
        draw_text(f"SCORE: {score} / 2000", font_small, (255, 255, 255), 10, 10)

    elif state == GAMEOVER:
        draw_text("MISSIONE FALLITA!", font_big, (255, 50, 50), WIDTH//2, HEIGHT//2 - 100, True)
        draw_text(f"SCORE FINALE: {score}", font_mid, (255, 255, 255), WIDTH//2, HEIGHT//2, True)
        draw_text("Premi un tasto per riprovare", font_small, (0, 255, 0), WIDTH//2, HEIGHT//2 + 100, True)

    elif state == WIN:
        # --- SCHERMATA DI VITTORIA ---
        screen.fill((10, 40, 10)) # Sfondo verdastro per la vittoria
        draw_text("COMPLIMENTI!", font_big, (0, 255, 100), WIDTH//2, HEIGHT//2 - 120, True)
        draw_text("Hai finito il gioco!", font_mid, (255, 255, 255), WIDTH//2, HEIGHT//2 - 40, True)
        draw_text("Grazie per aver giocato", font_small, (200, 200, 200), WIDTH//2, HEIGHT//2 + 40, True)
        draw_text("Premi un tasto per il Menu", font_small, (255, 255, 0), WIDTH//2, HEIGHT//2 + 120, True)

    pygame.display.flip()
    clock.tick(FPS)
