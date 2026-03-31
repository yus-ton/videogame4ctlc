import pygame
import random

# Inizializzazione
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aereo vs MUSCI - Laser Edition")
clock = pygame.time.Clock()

# Colori
CIELO = (15, 15, 35)
NERO = (0, 0, 0)
ROSSO = (255, 0, 0)
VERDE = (0, 255, 0)
BIANCO = (255, 255, 255)
VIOLA_SCURO = (100, 0, 150)
GRIGIO_METALLO = (70, 70, 90)
ORO = (255, 215, 0)
VIOLA_LASER = (255, 0, 255)

def draw_player(surface, x, y):
    pygame.draw.ellipse(surface, (200, 200, 200), (x, y, 60, 20))
    pygame.draw.rect(surface, (150, 150, 150), (x + 20, y - 10, 15, 40))
    pygame.draw.rect(surface, (255, 0, 0), (x, y + 5, 10, 10))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, HEIGHT // 2, 60, 20)
        self.vel_y = 0
        self.gravity = 0.35
        self.lift = -8

    def update(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        return 0 <= self.rect.y <= HEIGHT - 20

    def jump(self):
        self.vel_y = self.lift

class BossMusci:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 180, HEIGHT // 2, 120, 150)
        self.hp = 15
        self.max_hp = 15
        self.speed = 4
        self.direction = 1
        self.shoot_timer = 0

    def update(self, boss_bullets):
        self.rect.y += self.speed * self.direction
        if self.rect.top <= 60 or self.rect.bottom >= HEIGHT - 60:
            self.direction *= -1
        
        # Musci spara ogni 45 frame
        self.shoot_timer += 1
        if self.shoot_timer >= 45:
            boss_bullets.append(pygame.Rect(self.rect.left, self.rect.centery, 30, 8))
            self.shoot_timer = 0

    def draw(self, surface):
        pygame.draw.rect(surface, VIOLA_SCURO, self.rect, border_radius=20)
        pygame.draw.rect(surface, GRIGIO_METALLO, self.rect, 5, border_radius=20)
        pygame.draw.ellipse(surface, ROSSO, (self.rect.x + 20, self.rect.y + 30, 35, 25))
        pygame.draw.circle(surface, NERO, (self.rect.x + 37, self.rect.y + 42), 6)
        pygame.draw.ellipse(surface, ROSSO, (self.rect.x + 65, self.rect.y + 30, 35, 25))
        pygame.draw.circle(surface, NERO, (self.rect.x + 82, self.rect.y + 42), 6)
        pygame.draw.rect(surface, NERO, (self.rect.x + 30, self.rect.y + 90, 60, 20), border_radius=5)
        for i in range(5):
            pygame.draw.rect(surface, BIANCO, (self.rect.x + 35 + (i*10), self.rect.y + 90, 5, 8))
        font = pygame.font.SysFont("Arial", 24, bold=True)
        name_tag = font.render("MUSCI", True, ORO)
        surface.blit(name_tag, (self.rect.x + 25, self.rect.y - 45))
        pygame.draw.rect(surface, (50, 0, 0), (self.rect.x, self.rect.y - 15, 120, 12))
        life_width = (self.hp / self.max_hp) * 120
        pygame.draw.rect(surface, VERDE, (self.rect.x, self.rect.y - 15, life_width, 12))

def show_text(text, size, x, y, color=BIANCO):
    font = pygame.font.SysFont("Arial", size, bold=True)
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=(x, y)))

def game_over_screen(score):
    while True:
        screen.fill((30, 0, 0))
        show_text("GAME OVER", 70, WIDTH//2, HEIGHT//2 - 50, ROSSO)
        show_text(f"Punteggio Finale: {score}", 30, WIDTH//2, HEIGHT//2 + 20, BIANCO)
        show_text("Premi R per Riprovare o ESC per Uscire", 25, WIDTH//2, HEIGHT//2 + 80, ORO)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "RESTART"
                if event.key == pygame.K_ESCAPE: return "QUIT"

def choice_screen(score):
    while True:
        screen.fill((5, 5, 20))
        show_text("MUSCI È STATO DISTRUTTO!", 50, WIDTH//2, 150, ORO)
        pygame.draw.rect(screen, VERDE, (150, 350, 220, 60), border_radius=10)
        show_text("CONTINUA IL MASSACRO", 18, 260, 380, NERO)
        pygame.draw.rect(screen, ROSSO, (430, 350, 220, 60), border_radius=10)
        show_text("ESCI DA CAMPIONE", 18, 540, 380, NERO)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 150 <= mx <= 370 and 350 <= my <= 410: return "CONTINUE"
                if 430 <= mx <= 650 and 350 <= my <= 410: return "QUIT"

def main():
    while True:
        player = Player()
        bullets, enemies, boss_bullets = [], [], []
        boss = None
        score = 0
        game_active = False
        boss_defeated = False
        running = True
        current_action = "PLAY"

        while running:
            screen.fill(CIELO)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not game_active: game_active = True
                    player.jump()
                if event.type == pygame.MOUSEBUTTONDOWN and game_active:
                    bullets.append(pygame.Rect(player.rect.right, player.rect.centery, 15, 5))

            if not game_active:
                show_text("PREMI SPAZIO PER GIOCARE", 35, WIDTH//2, HEIGHT//2)
            else:
                if not player.update(): 
                    current_action = game_over_screen(score)
                    running = False

                if score >= 15 and boss is None and not boss_defeated:
                    boss = BossMusci()
                    enemies = []

                if boss:
                    boss.update(boss_bullets)
                    boss.draw(screen)
                    if player.rect.colliderect(boss.rect):
                        current_action = game_over_screen(score)
                        running = False
                else:
                    spawn_rate = 25 if boss_defeated else 40
                    if random.randint(1, spawn_rate) == 1:
                        enemies.append(pygame.Rect(WIDTH, random.randint(50, HEIGHT-80), 30, 30))

                # Gestione proiettili di Musci
                for bb in boss_bullets[:]:
                    bb.x -= 10
                    pygame.draw.rect(screen, VIOLA_LASER, bb, border_radius=2)
                    if player.rect.colliderect(bb):
                        current_action = game_over_screen(score)
                        running = False
                    if bb.right < 0: boss_bullets.remove(bb)

                for b in bullets[:]:
                    b.x += 14
                    pygame.draw.rect(screen, ROSSO, b)
                    if boss and b.colliderect(boss.rect):
                        boss.hp -= 1
                        bullets.remove(b)
                        if boss.hp <= 0:
                            if choice_screen(score) == "CONTINUE":
                                boss = None
                                boss_defeated = True
                                boss_bullets = []
                            else: pygame.quit(); return
                    for e in enemies[:]:
                        if b.colliderect(e):
                            if e in enemies: enemies.remove(e)
                            if b in bullets: bullets.remove(b)
                            score += 1
                            break

                for e in enemies[:]:
                    e.x -= 8
                    pygame.draw.circle(screen, (0, 200, 0), e.center, 15)
                    if player.rect.colliderect(e):
                        current_action = game_over_screen(score)
                        running = False

                draw_player(screen, player.rect.x, player.rect.y)
                show_text(f"SCORE: {score}", 30, 100, 30, ORO)

            pygame.display.flip()
            clock.tick(60)
        
        if current_action == "QUIT": break
    pygame.quit()

if __name__ == "__main__":
    main()
