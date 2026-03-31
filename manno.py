import pygame
import sys
import random

# --- 1. CONFIGURAZIONE ---
pygame.init()

# Colori
NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
ROSSO = (255, 0, 0)     # Nemico Normale
BLU = (0, 100, 255)     # Nemico Veloce (Nuovo!)
VERDE = (0, 255, 0)     # Giocatore

# Schermo
LARGHEZZA = 600
ALTEZZA = 400
screen = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Schiva i Blocchi 2.0")

clock = pygame.time.Clock()

# --- 2. VARIABILI DEL GIOCO ---

# Giocatore
player_dim = 40
player_x = LARGHEZZA // 2
player_y = ALTEZZA - 60
player_speed = 5

# --- GESTIONE NEMICI ---
# Lista 1: Nemici Rossi (Lenti)
nemici_rossi = [] 
vel_rossi = 4

# Lista 2: Nemici Blu (Veloci) - NOVITÀ
nemici_blu = []
vel_blu = 8  # Vanno al doppio della velocità!

frequenza_nemici = 20
timer_nemici = 0

# Punteggio
punti = 0
game_over = False
font = pygame.font.SysFont("Arial", 24)

# --- 3. CICLO PRINCIPALE ---
while True:
    # A. GESTIONE EVENTI
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit() # Chiude tutto il sistema

    if not game_over:
        
        # B. MOVIMENTO GIOCATORE
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < LARGHEZZA - player_dim:
            player_x += player_speed

        player_rect = pygame.Rect(player_x, player_y, player_dim, player_dim)

        # C. CREAZIONE NEMICI
        timer_nemici += 1
        if timer_nemici >= frequenza_nemici:
            
            # Tiro un dado da 1 a 10
            sorte = random.randint(1, 10)
            x_casuale = random.randint(0, LARGHEZZA - 30)
            
            # Se esce 1 o 2 (20% di probabilità), creo un nemico BLU
            if sorte <= 2:
                nuovo_nemico = pygame.Rect(x_casuale, 0, 30, 30)
                nemici_blu.append(nuovo_nemico)
            else:
                # Altrimenti creo un nemico ROSSO classico
                nuovo_nemico = pygame.Rect(x_casuale, 0, 30, 30)
                nemici_rossi.append(nuovo_nemico)
                
            timer_nemici = 0 

        # D. MOVIMENTO E COLLISIONI (NEMICI ROSSI)
        for nemico in nemici_rossi[:]:
            nemico.y += vel_rossi
            if player_rect.colliderect(nemico):
                game_over = True
            if nemico.y > ALTEZZA:
                nemici_rossi.remove(nemico)
                punti += 1

        # E. MOVIMENTO E COLLISIONI (NEMICI BLU)
        for nemico in nemici_blu[:]:
            nemico.y += vel_blu  # Questi scendono veloci!
            if player_rect.colliderect(nemico):
                game_over = True
            if nemico.y > ALTEZZA:
                nemici_blu.remove(nemico)
                punti += 2 # I blu valgono doppio!

    # --- 4. DISEGNO ---
    screen.fill(NERO)

    if not game_over:
        # Disegno Giocatore
        pygame.draw.rect(screen, VERDE, (player_x, player_y, player_dim, player_dim))
        
        # Disegno Rossi
        for nemico in nemici_rossi:
            pygame.draw.rect(screen, ROSSO, nemico)
            
        # Disegno Blu
        for nemico in nemici_blu:
            pygame.draw.rect(screen, BLU, nemico)
        
        testo = font.render(f"Punti: {punti}", True, BIANCO)
        screen.blit(testo, (10, 10))
        
    else:
        testo_fine = font.render("HAI PERSO!", True, ROSSO)
        testo_punti = font.render(f"Punti totali: {punti}", True, BIANCO)
        screen.blit(testo_fine, (LARGHEZZA//2 - 60, ALTEZZA//2 - 20))
        screen.blit(testo_punti, (LARGHEZZA//2 - 60, ALTEZZA//2 + 20))

    pygame.display.flip()
    clock.tick(30)
