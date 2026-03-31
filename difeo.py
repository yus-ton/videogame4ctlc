import pygame
import sys
import random

# --- CONFIGURAZIONE --- 
pygame.init()  # Inizializza tutti i moduli di pygame
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 450
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Crea la finestra di gioco
pygame.display.set_caption("Geometry Dash: Evolution")  # Titolo della finestra

# --- COLORI E COSTANTI ---
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
FLOOR_Y = SCREEN_HEIGHT - 100  # Coordinata y del pavimento
FPS = 60  # Frame per secondo

# Palette di colori per diversi livelli: (sfondo, colore ostacoli)
LEVEL_PALETTES = [
    ((15, 15, 30), (0, 255, 255)),   # Livello 1: Cyan
    ((30, 10, 10), (255, 50, 50)),   # Livello 2: Red
    ((10, 30, 10), (50, 255, 50)),   # Livello 3: Green
    ((25, 0, 25), (255, 0, 255)),    # Livello 4: Purple
    ((30, 20, 0), (255, 150, 0)),    # Livello 5: Orange
]

# --- CLASSE PLAYER ---
class Player:
    def __init__(self):
        self.size = 40
        self.original_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)  # Surface trasparente per il player
        self.reset_physics()  # Imposta le variabili fisiche iniziali

    def reset_physics(self):
        # Posizione iniziale e parametri fisici
        self.x, self.y = 150, FLOOR_Y - self.size
        self.velocity_y = 0
        self.angle = 0  # Angolo di rotazione
        self.is_jumping = False
        self.gravity = 0.9  # Gravità del gioco
        self.jump_power = -16  # Forza del salto
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)  # Hitbox del player

    def update_visuals(self, color):
        # Disegna il player con occhi e bocca
        self.original_image.fill((0, 0, 0, 0))  # Reset immagine
        pygame.draw.rect(self.original_image, (*color, 150), (0, 0, self.size, self.size))  # Riempimento trasparente
        pygame.draw.rect(self.original_image, color, (0, 0, self.size, self.size), 3)  # Bordo
        pygame.draw.rect(self.original_image, BLACK, (8, 10, 8, 8))  # Occhio sinistro
        pygame.draw.rect(self.original_image, BLACK, (24, 10, 8, 8))  # Occhio destro
        pygame.draw.rect(self.original_image, BLACK, (10, 28, 20, 3))  # Bocca

    def jump(self):
        if not self.is_jumping:  # Salto solo se non già in aria
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def update(self):
        # Aggiorna la fisica del player
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        if self.y >= FLOOR_Y - self.size:  # Collisione con il pavimento
            self.y = FLOOR_Y - self.size
            self.velocity_y = 0
            self.is_jumping = False
            self.angle = round(self.angle / 90) * 90  # Reset angolo rotazione
        if self.is_jumping: self.angle -= 5  # Rotazione durante il salto
        self.rect.y = int(self.y)  # Aggiorna la hitbox

    def draw(self, surface):
        # Disegna il player ruotato
        rotated_img = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = rotated_img.get_rect(center=(self.x + self.size/2, self.y + self.size/2))
        surface.blit(rotated_img, new_rect.topleft)

# --- CLASSE OSTACOLO ---
class Obstacle:
    def __init__(self, x, type, color, y_offset=0):
        self.x = x
        self.type = type
        self.color = color
        self.y = FLOOR_Y - y_offset
        # Dimensioni a seconda del tipo
        if "spike" in type:
            self.w, self.h = (32, 38) if type == "spike" else (22, 26)
        else: self.w, self.h = 40, 40
        self.rect = pygame.Rect(self.x, self.y - self.h, self.w, self.h)  # Hitbox

    def update(self, speed):
        self.x -= speed  # Movimento verso sinistra
        self.rect.x = self.x  # Aggiorna hitbox

    def draw(self, surface):
        # Disegna ostacolo: spike o blocco
        if "spike" in self.type:
            p = [(self.x, self.y), (self.x + self.w, self.y), (self.x + self.w/2, self.y - self.h)]
            pygame.draw.polygon(surface, BLACK, p)
            pygame.draw.polygon(surface, self.color, p, 2)
        else:
            pygame.draw.rect(surface, BLACK, self.rect)
            pygame.draw.rect(surface, self.color, self.rect, 2)

# --- FUNZIONE PRINCIPALE ---
def main():
    clock = pygame.time.Clock()
    # Font di diverse dimensioni
    font_s = pygame.font.SysFont("Arial", 22, bold=True)
    font_m = pygame.font.SysFont("Arial", 35, bold=True)
    font_l = pygame.font.SysFont("Arial", 70, bold=True)
    
    player = Player()
    
    # Variabili di stato
    state = "MENU"  # MENU, PLAYING, GAMEOVER, LEVEL_UP
    level = 1
    obstacles = []
    
    # Imposta le variabili specifiche del livello
    def setup_level_vars(lvl):
        palette = LEVEL_PALETTES[(lvl-1) % len(LEVEL_PALETTES)]
        speed = 6 + (lvl * 0.8)  # Velocità aumenta col livello
        length = 4000 + (lvl * 1500)  # Lunghezza livello
        player.update_visuals(palette[1])  # Colore del player
        return palette, speed, length, 0, 0  # palette, speed, lunghezza, distanza, timer spawn

    palette, game_speed, level_length, distance_traveled, spawn_timer = setup_level_vars(level)

    while True:
        # --- 1. GESTIONE EVENTI ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_UP]:
                    if state == "MENU":
                        state = "PLAYING"
                    elif state == "PLAYING":
                        player.jump()
                    elif state == "GAMEOVER":
                        # Restart dal livello 1
                        level = 1
                        palette, game_speed, level_length, distance_traveled, spawn_timer = setup_level_vars(level)
                        player.reset_physics()
                        obstacles.clear()
                        state = "PLAYING"

        # --- 2. LOGICA DEL GIOCO ---
        if state == "PLAYING":
            player.update()  # Aggiorna posizione player
            distance_traveled += game_speed  # Incrementa distanza
            progress = min(int((distance_traveled / level_length) * 100), 100)  # Percentuale completamento

            # Spawning dinamico degli ostacoli
            spawn_timer -= 1
            if spawn_timer <= 0:
                type_choice = random.choices(["spike", "double", "block"], weights=[50, 20 + (level*5), 30])[0]
                if type_choice == "spike":
                    obstacles.append(Obstacle(SCREEN_WIDTH + 50, "spike", palette[1]))
                elif type_choice == "double":
                    obstacles.append(Obstacle(SCREEN_WIDTH + 50, "spike", palette[1]))
                    obstacles.append(Obstacle(SCREEN_WIDTH + 85, "spike", palette[1]))
                elif type_choice == "block":
                    obstacles.append(Obstacle(SCREEN_WIDTH + 50, "block", palette[1]))

                # Frequenza di spawn diminuisce col livello
                wait_time = max(25, 65 - (level * 6))
                spawn_timer = random.randint(wait_time, wait_time + 30)

            # Collisioni e rimozione ostacoli
            hitbox = player.rect.inflate(-16, -16)  # Hitbox più piccola per collisioni realistiche
            for obs in obstacles[:]:
                obs.update(game_speed)
                if hitbox.colliderect(obs.rect):  # Collisione
                    state = "GAMEOVER"
                if obs.x < -100:  # Ostacolo fuori schermo
                    obstacles.remove(obs)

            if progress >= 100:
                state = "LEVEL_UP"
                timer_state = FPS * 2  # 2 secondi di pausa

        elif state == "LEVEL_UP":
            timer_state -= 1
            if timer_state <= 0:
                level += 1
                palette, game_speed, level_length, distance_traveled, spawn_timer = setup_level_vars(level)
                player.reset_physics()
                obstacles.clear()
                state = "PLAYING"

        # --- 3. DISEGNO SU SCHERMO ---
        SCREEN.fill(palette[0])  # Sfondo del livello
        
        # Pavimento e griglia
        pygame.draw.rect(SCREEN, BLACK, (0, FLOOR_Y, SCREEN_WIDTH, 100))  # Pavimento
        grid_offset = int(-distance_traveled % 50)
        for i in range(0, SCREEN_WIDTH + 50, 50):
            pygame.draw.line(SCREEN, (30, 30, 30), (i + grid_offset, FLOOR_Y), (i + grid_offset, SCREEN_HEIGHT))
        pygame.draw.line(SCREEN, palette[1], (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 3)

        # Disegna ostacoli e player
        for obs in obstacles: obs.draw(SCREEN)
        player.draw(SCREEN)

        # --- 4. OVERLAY (MENU, UI, GAMEOVER) ---
        if state == "MENU":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Sfondo semitrasparente
            SCREEN.blit(overlay, (0,0))
            
            title = font_l.render("GEOMETRY DASH", True, palette[1])
            start_msg = font_m.render("Premi SPAZIO per iniziare", True, WHITE)
            SCREEN.blit(title, title.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40)))
            SCREEN.blit(start_msg, start_msg.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)))

        elif state == "PLAYING":
            # Barra progresso
            bar_w = 400
            pygame.draw.rect(SCREEN, (50, 50, 50), (200, 20, bar_w, 10))
            pygame.draw.rect(SCREEN, palette[1], (200, 20, (progress/100) * bar_w, 10))
            txt = font_s.render(f"LEVEL {level} - {progress}%", True, WHITE)
            SCREEN.blit(txt, (200, 35))

        elif state == "LEVEL_UP":
            txt = font_l.render(f"LIVELLO {level} COMPLETATO!", True, WHITE)
            SCREEN.blit(txt, txt.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

        elif state == "GAMEOVER":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))  # Overlay semitrasparente
            SCREEN.blit(s, (0,0))
            msg = font_l.render("CRASH!", True, (255, 50, 50))
            retry = font_s.render("Premi SPAZIO per riprovare", True, WHITE)
            SCREEN.blit(msg, msg.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20)))
            SCREEN.blit(retry, retry.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))

        pygame.display.flip()  # Aggiorna lo schermo
        clock.tick(FPS)  # Mantiene FPS costanti

if __name__ == "__main__":
    main()
