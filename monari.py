import pygame
import random
import sys

# --- INIZIALIZZAZIONE ---
pygame.init()

# --- DIMENSIONI ---
GRID = 20 
GAME_WIDTH, GAME_HEIGHT = 1000, 700 
UI_HEIGHT = 85 
SIDE_MARGIN = 40 
WIDTH = GAME_WIDTH + (SIDE_MARGIN * 2)
HEIGHT = GAME_HEIGHT + UI_HEIGHT + SIDE_MARGIN

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SnakeNapoli - Edizione Finale Scudetto")

clock = pygame.time.Clock()
GAME_FONT = pygame.font.SysFont("Arial", 22, bold=True) 
BANNER_FONT = pygame.font.SysFont("Impact", 24) 
TITLE_FONT = pygame.font.SysFont("Arial", 50, bold=True)
BTN_FONT = pygame.font.SysFont("Arial", 20, bold=True) 
SMALL_BTN_FONT = pygame.font.SysFont("Arial", 14, bold=True) 

# --- COLORI ---
BLACK = (15, 15, 15)
AZZURRO = (0, 132, 197)   
DARK_BLUE = (0, 20, 60)   
RED = (231, 76, 60)       
WHITE = (255, 255, 255)   
GOLD = (212, 175, 55)     
GREY = (40, 40, 40)       
GREEN = (46, 204, 113)    

# --- DISEGNO ---

def draw_logo_head(x, y):
    center = (x + GRID // 2, y + GRID // 2)
    pygame.draw.circle(screen, AZZURRO, center, GRID // 2)
    pygame.draw.circle(screen, WHITE, center, GRID // 2, 2)
    font_n = pygame.font.SysFont("Arial", 16, bold=True)
    n_surf = font_n.render("N", True, WHITE)
    screen.blit(n_surf, (center[0] - n_surf.get_width() // 2, center[1] - n_surf.get_height() // 2))

def draw_button(rect, text, bg_color, text_color=WHITE):
    """Disegna un pulsante standard."""
    mouse_pos = pygame.mouse.get_pos()
    color = bg_color
    if rect.collidepoint(mouse_pos):
        color = (min(bg_color[0]+20, 255), min(bg_color[1]+20, 255), min(bg_color[2]+20, 255))
        
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    
    txt_surf = BTN_FONT.render(text, True, text_color)
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))
    return rect

def draw_banners_and_ui(score, level):
    testo_banner = "FORZA NAPOLI  -  CIRO VIVE  -  1926"
    
    # Sfondi
    pygame.draw.rect(screen, AZZURRO, (0, 0, WIDTH, 40)) 
    pygame.draw.rect(screen, AZZURRO, (0, HEIGHT - SIDE_MARGIN, WIDTH, SIDE_MARGIN)) 
    pygame.draw.rect(screen, AZZURRO, (0, 0, SIDE_MARGIN, HEIGHT)) 
    pygame.draw.rect(screen, AZZURRO, (WIDTH - SIDE_MARGIN, 0, SIDE_MARGIN, HEIGHT)) 

    # Testi Banner
    s_hor = BANNER_FONT.render(testo_banner, True, WHITE)
    screen.blit(s_hor, (WIDTH // 2 - s_hor.get_width() // 2, 5)) 
    screen.blit(s_hor, (WIDTH // 2 - s_hor.get_width() // 2, HEIGHT - SIDE_MARGIN + 5)) 

    s_ver_raw = BANNER_FONT.render(testo_banner, True, WHITE)
    s_l = pygame.transform.rotate(s_ver_raw, 90)
    screen.blit(s_l, (8, (HEIGHT + UI_HEIGHT) // 2 - s_l.get_height() // 2)) 
    s_r = pygame.transform.rotate(s_ver_raw, -90)
    screen.blit(s_r, (WIDTH - 35, (HEIGHT + UI_HEIGHT) // 2 - s_r.get_height() // 2)) 

    # --- TABELLONE PUNTEGGI ---
    scoreboard_rect = pygame.Rect(SIDE_MARGIN, 40, GAME_WIDTH, 45)
    pygame.draw.rect(screen, DARK_BLUE, scoreboard_rect)
    pygame.draw.rect(screen, GOLD, scoreboard_rect, 3)
    
    y_info = 50 
    
    # Pulsante PAUSA (piccolo)
    btn_rules_rect = pygame.Rect(SIDE_MARGIN + 10, 48, 80, 30)
    pygame.draw.rect(screen, GOLD, btn_rules_rect, border_radius=5)
    lbl_btn = SMALL_BTN_FONT.render("PAUSA", True, DARK_BLUE)
    screen.blit(lbl_btn, (btn_rules_rect.centerx - lbl_btn.get_width()//2, btn_rules_rect.centery - lbl_btn.get_height()//2))

    # Punteggi 
    lbl_score = GAME_FONT.render(f"PALLONI: {score}", True, WHITE)
    lbl_level = GAME_FONT.render(f"LIVELLO: {level}", True, GOLD) 
    lbl_goal = GAME_FONT.render(f"OBIETTIVO: 20", True, WHITE)

    screen.blit(lbl_score, (SIDE_MARGIN + 120, y_info)) 
    screen.blit(lbl_level, (WIDTH // 2 - lbl_level.get_width() // 2, y_info))
    screen.blit(lbl_goal, (WIDTH - SIDE_MARGIN - 210, y_info))
    
    return btn_rules_rect

def draw_game_elements(snake_list, food_pos, obstacles):
    for obs in obstacles:
        pygame.draw.rect(screen, RED, (obs[0], obs[1], GRID, GRID), border_radius=4)
        pygame.draw.rect(screen, WHITE, (obs[0], obs[1], GRID, GRID), 1)
    
    pygame.draw.circle(screen, WHITE, (food_pos[0] + GRID//2, food_pos[1] + GRID//2), 9)
    pygame.draw.circle(screen, BLACK, (food_pos[0] + GRID//2, food_pos[1] + GRID//2), 4)
    
    for i, (x, y) in enumerate(snake_list):
        if i == len(snake_list) - 1:
            draw_logo_head(x, y)
        else:
            color = AZZURRO if i % 2 == 0 else WHITE
            pygame.draw.rect(screen, color, (x, y, GRID, GRID), border_radius=6)

def draw_rules_background():
    box_rect = pygame.Rect(WIDTH//2-400, 100, 800, 520) 
    pygame.draw.rect(screen, GREY, box_rect, border_radius=15)
    pygame.draw.rect(screen, AZZURRO, box_rect, 3, border_radius=15)
    
    screen.blit(TITLE_FONT.render("SNAKE NAPOLI", True, AZZURRO), (WIDTH//2 - 180, 120))
    
    text_f = pygame.font.SysFont("Arial", 22)
    regole = [
        ("OBIETTIVO:", "Raccogli i palloni. Il punteggio non si azzera mai!", AZZURRO),
        ("COMANDI:", "Usa le FRECCETTE per muoverti.", GOLD), 
        ("NEMICO:", "Sorci Romani (Rossi). Non toccarli!", RED),
        ("LIVELLO 1 (0-5):", "Riscaldamento. Campo libero.", WHITE),
        ("LIVELLO 2 (5-10):", "Campo con 35 ostacoli fissi.", WHITE),
        ("LIVELLO 3 (10-20):", "Finale. I Sorci si muovono e il serpente si azzera!", WHITE),
        ("PAUSA:", "Premi SPAZIO o il tasto PAUSA per il menu.", GOLD), 
        ("BORDI:", "Non uscire dal campo azzurro.", AZZURRO)
    ]
    
    y = 190
    for l, d, c in regole:
        screen.blit(text_f.render(l, True, c), (WIDTH//2-370, y))
        screen.blit(text_f.render(d, True, WHITE), (WIDTH//2-140, y))
        y += 40 

# --- LOGICA ---

def spawn_food(snake_list, obstacles):
    while True:
        x = random.randrange(SIDE_MARGIN + GRID*2, GAME_WIDTH + SIDE_MARGIN - GRID*2, GRID)
        y = random.randrange(UI_HEIGHT + GRID, HEIGHT - SIDE_MARGIN - GRID*2, GRID)
        food_rect = pygame.Rect(x, y, GRID, GRID)
        if (x, y) not in snake_list and not any(food_rect.colliderect(pygame.Rect(o[0], o[1], GRID, GRID)) for o in obstacles):
            return x, y

def reset_game_state():
    # Resetta tutto il gioco
    start_x = (WIDTH // 2 // GRID * GRID)
    start_y = (UI_HEIGHT + (GAME_HEIGHT // 2 // GRID * GRID))
    snake_list = [(start_x - GRID*2, start_y), (start_x - GRID, start_y), (start_x, start_y)]
    snake_dx, snake_dy = GRID, 0 
    score = 0
    level = 1
    obstacles = [] 
    food_x, food_y = spawn_food(snake_list, obstacles)
    return snake_list, snake_dx, snake_dy, score, level, obstacles, food_x, food_y

# --- SCHERMATE E STATI ---

def show_tutorial():
    waiting = True
    while waiting:
        screen.fill(DARK_BLUE)
        draw_rules_background()
        
        btn_play = draw_button(pygame.Rect(WIDTH//2-100, 560, 200, 45), "GIOCA", GREEN)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and btn_play.collidepoint(e.pos):
                waiting = False 
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                waiting = False
        
        pygame.display.flip()
        clock.tick(30)

def show_level_transition(next_level, description):
    """Mostra una schermata intermedia che spiega il nuovo livello."""
    pygame.time.set_timer(pygame.USEREVENT, 0) # Blocca movimento
    
    # Sfondo e box
    screen.fill(BLACK)
    draw_banners_and_ui(0, next_level-1) # UI statica sullo sfondo
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 20, 60, 230)) # Blu scuro semi-trasparente
    screen.blit(overlay, (0,0))
    
    # Testi
    font_big = pygame.font.SysFont("Arial", 60, bold=True)
    font_desc = pygame.font.SysFont("Arial", 35, bold=True)
    
    t_level = font_big.render(f"LIVELLO {next_level}", True, GOLD)
    
    # Gestione descrizione su più righe se c'è un " - "
    lines = description.split(" - ")
    
    screen.blit(t_level, (WIDTH//2 - t_level.get_width()//2, HEIGHT//2 - 100))
    
    y_off = 0
    for line in lines:
        t_desc = font_desc.render(line, True, WHITE)
        screen.blit(t_desc, (WIDTH//2 - t_desc.get_width()//2, HEIGHT//2 - 20 + y_off))
        y_off += 50

    pygame.display.flip()
    
    # Attende 3 secondi processando eventi per non bloccare finestra
    end_time = pygame.time.get_ticks() + 3000
    while pygame.time.get_ticks() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.wait(100)

def pause_game():
    pygame.time.set_timer(pygame.USEREVENT, 0) # Blocca timer
    paused = True
    action = "resume"
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200)) 
    screen.blit(overlay, (0,0))
    
    while paused:
        draw_rules_background()
        
        btn_resume = draw_button(pygame.Rect(WIDTH//2 - 100, 560, 200, 45), "RIPRENDI", GREEN)
        btn_restart = draw_button(pygame.Rect(WIDTH//2 - 320, 560, 200, 45), "RICOMINCIA", GOLD, BLACK)
        btn_quit = draw_button(pygame.Rect(WIDTH//2 + 120, 560, 200, 45), "ESCI", RED)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_resume.collidepoint(e.pos):
                    paused = False
                    action = "resume"
                elif btn_restart.collidepoint(e.pos):
                    paused = False
                    action = "restart"
                elif btn_quit.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()
            
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                paused = False
                action = "resume"
        
        pygame.display.flip()
        clock.tick(30)
    
    if action == "resume":
        pygame.time.set_timer(pygame.USEREVENT, 100) # Riavvia timer solo se riprendi
        
    return action

def count_down(snake_list, food_pos, obstacles, score, level):
    pygame.time.set_timer(pygame.USEREVENT, 0)
    
    font_cd = pygame.font.SysFont("Arial", 120, bold=True)
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        draw_banners_and_ui(score, level)
        pygame.draw.rect(screen, AZZURRO, (SIDE_MARGIN, UI_HEIGHT, GAME_WIDTH, GAME_HEIGHT), 2)
        draw_game_elements(snake_list, food_pos, obstacles)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0,0))
        
        text = font_cd.render(str(i), True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        
        pygame.display.flip()
        pygame.time.wait(1000)
        pygame.event.pump() 

def show_game_over(msg):
    pygame.time.set_timer(pygame.USEREVENT, 0) # FERMA TUTTO
    while True:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0,0))
        
        font_go = pygame.font.SysFont("Arial", 40, bold=True)
        lines = msg.split(" - ")
        y = HEIGHT // 2 - 100
        for line in lines:
            t = font_go.render(line.strip(), True, RED)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y))
            y += 60

        btn_retry = draw_button(pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 + 80, 200, 60), "RIPROVA", GREEN)
        btn_quit = draw_button(pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 80, 200, 60), "ESCI", RED)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(e.pos):
                    return True # Ritorna al main loop
                if btn_quit.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(30)

def show_victory():
    pygame.time.set_timer(pygame.USEREVENT, 0) # FERMA TUTTO
    
    while True:
        screen.fill(BLACK)
        draw_banners_and_ui(20, 3)
        pygame.draw.rect(screen, GOLD, (SIDE_MARGIN, UI_HEIGHT, GAME_WIDTH, GAME_HEIGHT), 5)
        
        font_v = pygame.font.SysFont("Arial", 45, bold=True)
        t1 = font_v.render("ABBIAMO VINTO LO SCUDETTO!", True, GOLD)
        t2 = font_v.render("I SORCI ROMANI A CASA!", True, WHITE)
        
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 80))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 20))
        
        btn_restart = draw_button(pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 + 80, 200, 60), "RICOMINCIA", GOLD, BLACK)
        btn_quit = draw_button(pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 80, 200, 60), "CHIUDI GIOCO", RED)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_restart.collidepoint(e.pos):
                    return # Torna al main loop
                if btn_quit.collidepoint(e.pos):
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(30)

# --- LOOP PRINCIPALE ---

def main_game():
    # 1. Resetta stato
    snake_list, snake_dx, snake_dy, score, level, obstacles, food_x, food_y = reset_game_state()
    input_queue = []
    
    # 2. Countdown iniziale
    count_down(snake_list, (food_x, food_y), obstacles, score, level)
    pygame.event.clear() 
    pygame.time.set_timer(pygame.USEREVENT, 100) 

    running = True
    while running:
        screen.fill(BLACK)
        
        btn_rules_rect = draw_banners_and_ui(score, level)
        pygame.draw.rect(screen, AZZURRO, (SIDE_MARGIN, UI_HEIGHT, GAME_WIDTH, GAME_HEIGHT), 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            clicked_pause = (event.type == pygame.MOUSEBUTTONDOWN and btn_rules_rect.collidepoint(event.pos))
            pressed_space = (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
            
            if clicked_pause or pressed_space:
                action = pause_game() 
                if action == "restart":
                    return 

            # MOVIMENTO
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: input_queue.append((0, -GRID))
                elif event.key == pygame.K_DOWN: input_queue.append((0, GRID))
                elif event.key == pygame.K_LEFT: input_queue.append((-GRID, 0))
                elif event.key == pygame.K_RIGHT: input_queue.append((GRID, 0))
            
            if event.type == pygame.USEREVENT:
                if input_queue:
                    nx, ny = input_queue.pop(0)
                    if (nx != -snake_dx or nx == 0) and (ny != -snake_dy or ny == 0):
                        snake_dx, snake_dy = nx, ny
                
                new_h = (snake_list[-1][0] + snake_dx, snake_list[-1][1] + snake_dy)
                
                # Collisioni Muri
                if (new_h[0] < SIDE_MARGIN or new_h[0] >= WIDTH - SIDE_MARGIN or 
                    new_h[1] < UI_HEIGHT or new_h[1] >= HEIGHT - SIDE_MARGIN):
                    if show_game_over("NON SEI DEGNO DI - PORTARE LA MAGLIA DEL NAPOLI"): return
                
                # Collisione Corpo
                if new_h in snake_list:
                    if show_game_over("NON SEI DEGNO DI - PORTARE LA MAGLIA DEL NAPOLI"): return
                
                # Collisione Ostacoli
                head_rect = pygame.Rect(new_h[0], new_h[1], GRID, GRID)
                if any(head_rect.colliderect(pygame.Rect(o[0], o[1], GRID, GRID)) for o in obstacles):
                    if show_game_over("NON SEI DEGNO DI - PORTARE LA MAGLIA DEL NAPOLI"): return

                snake_list.append(new_h) 
                
                if new_h[0] == food_x and new_h[1] == food_y:
                    score += 1
                    transition = False
                    
                    if score == 5: 
                        # TRANSIZIONE LIVELLO 2
                        show_level_transition(2, "35 OSTACOLI FISSI - IL GIOCO SI FA DURO")
                        level = 2
                        obstacles = []
                        for _ in range(35):
                            ox = random.randrange(SIDE_MARGIN + GRID*3, GAME_WIDTH + SIDE_MARGIN - GRID*3, GRID)
                            oy = random.randrange(UI_HEIGHT + GRID*3, HEIGHT - SIDE_MARGIN - GRID*3, GRID)
                            obstacles.append([ox, oy, 0]) 
                        transition = True
                            
                    elif score == 10: 
                        # TRANSIZIONE LIVELLO 3
                        show_level_transition(3, "I SORCI ORA SI MUOVONO! - IL SERPENTE RIPARTE DA ZERO")
                        level = 3
                        obstacles = [[250, 300, 6], [450, 500, -6], [650, 300, 6], [850, 500, -6]]
                        start_x = (WIDTH // 2 // GRID * GRID)
                        start_y = (UI_HEIGHT + (GAME_HEIGHT // 2 // GRID * GRID))
                        snake_list = [(start_x - GRID*2, start_y), (start_x - GRID, start_y), (start_x, start_y)]
                        snake_dx, snake_dy = GRID, 0
                        transition = True

                    if transition:
                        pygame.time.set_timer(pygame.USEREVENT, 0)
                        draw_game_elements(snake_list, (food_x, food_y), obstacles) 
                        count_down(snake_list, (food_x, food_y), obstacles, score, level)
                        pygame.event.clear() # PULIZIA EVENTI FONDAMENTALE DOPO TRANSIZIONE
                        pygame.time.set_timer(pygame.USEREVENT, 100) 

                    food_x, food_y = spawn_food(snake_list, obstacles)
                else:
                    del snake_list[0]

        if level == 3:
            for obs in obstacles:
                obs[1] += obs[2] 
                if obs[1] <= UI_HEIGHT + 5 or obs[1] >= HEIGHT - SIDE_MARGIN - GRID - 5:
                    obs[2] *= -1
                obs_rect = pygame.Rect(obs[0], obs[1], GRID, GRID)
                if any(obs_rect.colliderect(pygame.Rect(s[0], s[1], GRID, GRID)) for s in snake_list):
                     if show_game_over("NON SEI DEGNO DI - PORTARE LA MAGLIA DEL NAPOLI"): return

        if score >= 20:
            draw_game_elements(snake_list, (food_x, food_y), obstacles)
            show_victory()
            return 

        draw_game_elements(snake_list, (food_x, food_y), obstacles)
        pygame.display.flip()
        clock.tick(60) 

# --- AVVIO PROGRAMMA ---
show_tutorial() # Eseguito solo UNA volta all'avvio
while True:
    main_game() # Eseguito a ogni riavvio/sconfitta
