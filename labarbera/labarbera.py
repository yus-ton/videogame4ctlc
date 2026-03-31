import pygame
import sys
import math
import random
import os

# --- CONFIGURAZIONE ---
USA_IMMAGINI_ESTERNE = False 

# --- COSTANTI ---
LARGHEZZA, ALTEZZA = 1000, 700
FPS = 60
SUB_STEPS = 5 # Fisica precisa

# --- COLORI ---
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
ROSSO_CUORE = (220, 50, 50)
ORO_BONUS = (255, 215, 0)
ARANCIO_ESPLOSIONE = (255, 140, 0)

# Colori Coriandoli
COLORI_CORIANDOLI = [
    (255, 0, 0), (0, 255, 0), (50, 100, 255), (255, 255, 0), 
    (0, 255, 255), (255, 0, 255), (255, 165, 0), (255, 255, 255)
]

# Palette Tigerball
TEAL_SFONDO = (50, 160, 160)
TEAL_CHIARO = (70, 180, 180)
LEGNO_CHIARO = (210, 160, 100)
LEGNO_SCURO = (160, 110, 60)
GIALLO_TIGRE = (240, 220, 50)
GIALLO_CESTA = (220, 200, 40)
NERO_DISEGNO = (20, 20, 20)
BLU_BLOCCO = (50, 150, 200)
VERDE_BLOCCO = (50, 180, 50)
GRIGIO_BOMBA = (40, 40, 40)

# --- INIZIALIZZAZIONE ---
pygame.init()
schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Tigerball Clone - FINAL VERSION")
clock = pygame.time.Clock()

# Font
try:
    font_ui = pygame.font.SysFont('Comic Sans MS', 30, bold=True)
    font_instr = pygame.font.SysFont('Comic Sans MS', 24, bold=False)
    font_grande = pygame.font.SysFont('Comic Sans MS', 80, bold=True)
    font_bonus = pygame.font.SysFont('Comic Sans MS', 60, bold=True)
    font_score = pygame.font.SysFont('Comic Sans MS', 40, bold=True)
    font_piccolo = pygame.font.SysFont('Comic Sans MS', 20, bold=True)
except:
    font_ui = pygame.font.SysFont('Arial', 30, bold=True)
    font_instr = pygame.font.SysFont('Arial', 24, bold=False)
    font_grande = pygame.font.SysFont('Arial', 80, bold=True)
    font_bonus = pygame.font.SysFont('Arial', 60, bold=True)
    font_score = pygame.font.SysFont('Arial', 40, bold=True)
    font_piccolo = pygame.font.SysFont('Arial', 20, bold=True)

# --- SISTEMA DI SALVATAGGIO (FILE) ---
FILE_RECORD = "record.txt"

def carica_record():
    if not os.path.exists(FILE_RECORD):
        return 0
    try:
        with open(FILE_RECORD, "r") as f:
            return int(f.read())
    except:
        return 0

def salva_record(nuovo_score):
    try:
        with open(FILE_RECORD, "w") as f:
            f.write(str(nuovo_score))
        return True
    except:
        pass
    return False

high_score = carica_record()

# --- ASSET GRAFICI ---
def crea_texture_sfondo(w, h, col1, col2):
    surf = pygame.Surface((w, h))
    surf.fill(col1)
    for _ in range(5000):
        x = random.randint(0, w)
        y = random.randint(0, h)
        pygame.draw.circle(surf, col2, (x, y), random.randint(1, 3))
    return surf

def crea_texture_legno(w, h):
    surf = pygame.Surface((w, h))
    surf.fill(LEGNO_CHIARO)
    for i in range(0, h, 15):
        spessore = random.randint(2, 5)
        pygame.draw.line(surf, LEGNO_SCURO, (0, i + random.randint(-2,2)), (w, i+random.randint(-2,2)), spessore)
    return surf

def crea_palla_tigre(raggio):
    # GRAFICA FACCIA TIGRE (Come richiesto)
    surf = pygame.Surface((raggio*2, raggio*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, GIALLO_TIGRE, (raggio, raggio), raggio)
    # Strisce tigre ondulate
    for i in range(5):
        start_y = random.randint(0, raggio*2)
        points = []
        for x in range(0, raggio*2, 5):
            y = start_y + math.sin(x * 0.1) * 10
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(surf, NERO_DISEGNO, False, points, 4)
    # Bordo e occhi
    pygame.draw.circle(surf, NERO_DISEGNO, (raggio, raggio), raggio, 3)
    # Occhi
    pygame.draw.circle(surf, NERO, (raggio + 8, raggio - 5), 3)
    pygame.draw.circle(surf, NERO, (raggio - 8, raggio - 5), 3)
    return surf

def crea_blocco_disegnato(w, h, colore_base):
    surf = pygame.Surface((w, h))
    surf.fill(colore_base)
    pygame.draw.rect(surf, NERO_DISEGNO, (0,0,w,h), 4)
    cx, cy = w//2, h//2
    pygame.draw.circle(surf, NERO_DISEGNO, (cx, cy), min(w,h)//4, 3)
    pygame.draw.arc(surf, NERO_DISEGNO, (cx-w//6, cy-w//6, w//3, w//3), 0, 3.14, 3)
    return surf

def crea_cesta_disegnata(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    points = [(w*0.15, 0), (w*0.85, 0), (w, h*0.8), (w*0.8, h), (w*0.2, h), (0, h*0.8)]
    pygame.draw.polygon(surf, GIALLO_CESTA, points)
    pygame.draw.polygon(surf, NERO_DISEGNO, points, 4)
    star_pts = [(w*0.5, h*0.3), (w*0.6, h*0.5), (w*0.8, h*0.5), (w*0.65, h*0.7), 
                (w*0.7, h*0.9), (w*0.5, h*0.8), (w*0.3, h*0.9), (w*0.35, h*0.7), 
                (w*0.2, h*0.5), (w*0.4, h*0.5)]
    pygame.draw.lines(surf, NERO_DISEGNO, True, star_pts, 4)
    return surf

def crea_icona_cuore():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf, ROSSO_CUORE, (12, 15), 10)
    pygame.draw.circle(surf, ROSSO_CUORE, (28, 15), 10)
    pygame.draw.polygon(surf, ROSSO_CUORE, [(2, 20), (38, 20), (20, 38)])
    return surf

def crea_icona_bomba():
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(surf, GRIGIO_BOMBA, (25, 28), 16)
    pygame.draw.circle(surf, NERO, (25, 28), 16, 2)
    pygame.draw.circle(surf, (100, 100, 100), (20, 22), 4)
    pygame.draw.rect(surf, GRIGIO_BOMBA, (21, 8, 8, 6))
    pygame.draw.rect(surf, NERO, (21, 8, 8, 6), 2)
    pygame.draw.arc(surf, (200, 200, 200), (24, 2, 12, 12), 0, 1.5, 2)
    pygame.draw.circle(surf, ROSSO_CUORE, (36, 4), 3)
    return surf

def crea_box_punteggio_esplosione():
    w, h = 160, 90
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w//2, h//2
    points = []
    for i in range(20):
        angle = i * (2 * math.pi / 20)
        r = 40 if i % 2 == 0 else 30 
        x = cx + math.cos(angle) * (w/2.2) * (1.0 if i%2==0 else 0.8)
        y = cy + math.sin(angle) * (h/2.2) * (1.0 if i%2==0 else 0.8)
        points.append((x, y))
    pygame.draw.polygon(surf, BIANCO, points)
    pygame.draw.polygon(surf, NERO_DISEGNO, points, 4)
    return surf

# --- SETUP ASSET ---
ALTEZZA_PAVIMENTO = 50
ASSET = {}
ASSET['sfondo'] = crea_texture_sfondo(LARGHEZZA, ALTEZZA - ALTEZZA_PAVIMENTO, TEAL_SFONDO, TEAL_CHIARO)
ASSET['pavimento'] = crea_texture_legno(LARGHEZZA, ALTEZZA_PAVIMENTO)
raggio_palla = 22
ASSET['palla'] = crea_palla_tigre(raggio_palla)
ASSET['icona_cuore'] = crea_icona_cuore()
ASSET['icona_bomba'] = crea_icona_bomba()
ASSET['box_score'] = crea_box_punteggio_esplosione()

CESTA_W, CESTA_H = 130, 110
ASSET['cesta'] = crea_cesta_disegnata(CESTA_W, CESTA_H)

# --- CLASSI ---
class Pulsante:
    def __init__(self, x, y, w, h, testo, colore_bg, colore_testo):
        self.rect = pygame.Rect(x, y, w, h)
        self.testo = testo
        self.colore_bg = colore_bg
        self.colore_testo = colore_testo
        self.hover = False

    def draw(self, surface):
        colore = (min(255, self.colore_bg[0]+30), min(255, self.colore_bg[1]+30), min(255, self.colore_bg[2]+30)) if self.hover else self.colore_bg
        pygame.draw.rect(surface, colore, self.rect, border_radius=15)
        pygame.draw.rect(surface, NERO_DISEGNO, self.rect, 4, border_radius=15)
        text_surf = font_ui.render(self.testo, True, self.colore_testo)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.hover
        return False

class BloccoSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, tipo="blu"):
        super().__init__()
        colore = BLU_BLOCCO if tipo == "blu" else VERDE_BLOCCO
        self.image = crea_blocco_disegnato(w, h, colore)
        self.rect = self.image.get_rect(topleft=(x, y))

class CestaAvanzata:
    def __init__(self, x, y):
        self.image = ASSET['cesta']
        self.rect = self.image.get_rect()
        self.rect.bottom = ALTEZZA - ALTEZZA_PAVIMENTO + 10 
        self.rect.x = x
        spessore_parete = 15
        self.muro_sx = pygame.Rect(x + 5, self.rect.y + 10, spessore_parete, self.rect.height - 10)
        self.muro_dx = pygame.Rect(x + CESTA_W - spessore_parete - 5, self.rect.y + 10, spessore_parete, self.rect.height - 10)
        self.muro_bottom = pygame.Rect(x + 10, self.rect.bottom - 20, CESTA_W - 20, 20)
        self.zona_vittoria = pygame.Rect(x + spessore_parete, self.rect.y + 30, CESTA_W - 2*spessore_parete, 40)

    def get_collision_rects(self):
        return [self.muro_sx, self.muro_dx, self.muro_bottom]

class ParticellaBonus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -5)
        self.colore = random.choice([ROSSO_CUORE, GIALLO_TIGRE, BIANCO, (50, 200, 50), (50, 50, 250)])
        self.size = random.randint(5, 10)
        self.vita = 120 

    def update(self):
        self.vy += 0.2
        self.x += self.vx
        self.y += self.vy
        self.vita -= 1

    def draw(self, surface):
        if self.vita > 0:
            pygame.draw.rect(surface, self.colore, (self.x, self.y, self.size, self.size))

class ParticellaRecord:
    def __init__(self):
        self.x = random.randint(0, LARGHEZZA)
        self.y = random.randint(-LARGHEZZA, -10) 
        self.w = random.randint(8, 15)
        self.h = random.randint(8, 15)
        self.colore = random.choice(COLORI_CORIANDOLI)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(4, 9)
        self.rotazione = random.randint(0, 360)
        self.v_rot = random.uniform(-5, 5)

    def update(self):
        self.y += self.vy
        self.x += self.vx + math.sin(self.y * 0.02) * 2
        self.rotazione += self.v_rot
        if self.y > ALTEZZA:
            self.y = random.randint(-100, -10)
            self.x = random.randint(0, LARGHEZZA)

    def draw(self, surface):
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s.fill(self.colore)
        s = pygame.transform.rotate(s, self.rotazione)
        surface.blit(s, (self.x, self.y))

# --- FISICA OTTIMIZZATA ---
GRAVITA = 0.35 
RIMBALZO = 0.70
ATTRITO_ARIA = 0.998 
ATTRITO_TERRA = 0.95
LANCIO_POTENZA = 7.0 

# --- VARIABILI GLOBALI ---
STATO_MENU = "MENU"
STATO_GIOCO = "GIOCO"
STATO_GAMEOVER = "GAMEOVER"
stato_corrente = STATO_MENU

pos_palla = [0, 0]
vel_palla = [0, 0]
angolo_palla = 0.0 
scia_palla = []
is_dragging = False
start_pos = (0, 0)
palla_in_gioco = False 
livello_completato = False 

vite = 5
bombe = 3 
timer_esplosione_bomba = 0 

streak_consecutiva = 0 
particelle_bonus = []
coriandoli = [] # PER ANIMAZIONE RECORD
timer_bonus = 0 

livelli_completati = 0 
livello_corrente = 1
palla_ferma_counter = 0

cooldown_danni = 0 
ultimo_livello_tipo = ""

ostacoli = pygame.sprite.Group()
cesta = None

rect_icona_bomba = pygame.Rect(140, 20, 50, 50) 
mostra_new_record = False # Variabile controllo grafica

# POSIZIONI PULSANTI
pulsante_play = Pulsante(LARGHEZZA//2 - 100, 580, 200, 80, "GIOCA", VERDE_BLOCCO, BIANCO)
pulsante_menu = Pulsante(LARGHEZZA//2 - 100, 580, 200, 80, "MENU", BLU_BLOCCO, BIANCO)

# --- FUNZIONI LOGICA ---

def reset_palla_al_lancio():
    global pos_palla, vel_palla, scia_palla, palla_in_gioco, livello_completato, angolo_palla
    pos_palla = [150.0, ALTEZZA - ALTEZZA_PAVIMENTO - raggio_palla - 10]
    vel_palla = [0.0, 0.0]
    angolo_palla = 0.0
    scia_palla = []
    palla_in_gioco = False
    livello_completato = False

def genera_livello_procedurale(livello):
    global ultimo_livello_tipo
    ostacoli.empty()
    cesta_x = LARGHEZZA - 180 + random.randint(-20, 50)
    
    if livello == 1: tipo_scelto = "MURO_SEMPLICE"
    elif livello == 2: tipo_scelto = "FINESTRA"
    elif livello == 3: tipo_scelto = "PIATTAFORMA"
    elif livello == 4: tipo_scelto = "SCALINI"
    elif livello == 5: tipo_scelto = "TORRE"
    elif livello == 6: tipo_scelto = "PONTE" 
    else:
        tipi_disponibili = ["MURO", "FINESTRA", "TORRE", "SCALINI", "PIATTAFORMA", "PONTE", "DOPPIA_COLONNA"]
        tipo_scelto = random.choice(tipi_disponibili)
        if tipo_scelto == ultimo_livello_tipo:
            altri = [t for t in tipi_disponibili if t != tipo_scelto]
            tipo_scelto = random.choice(altri)
            
    ultimo_livello_tipo = tipo_scelto
    colore = "blu" if livello % 2 == 0 else "verde"
    mid_x = LARGHEZZA // 2

    if tipo_scelto == "MURO_SEMPLICE":
        h = 80
        ostacoli.add(BloccoSprite(mid_x, ALTEZZA - ALTEZZA_PAVIMENTO - h, 60, h, colore))
    elif tipo_scelto == "MURO":
        h = random.randint(100, 200) 
        x = random.randint(300, 550)
        ostacoli.add(BloccoSprite(x, ALTEZZA - ALTEZZA_PAVIMENTO - h, random.randint(40, 80), h, colore))
    elif tipo_scelto == "FINESTRA":
        gap_h = random.randint(180, 250) 
        gap_y = random.randint(150, 250)
        x = random.randint(400, 550)
        h_sotto = gap_y
        ostacoli.add(BloccoSprite(x, ALTEZZA - ALTEZZA_PAVIMENTO - h_sotto, 60, h_sotto, colore))
        y_sopra = ALTEZZA - ALTEZZA_PAVIMENTO - h_sotto - gap_h - 400 
        ostacoli.add(BloccoSprite(x, y_sopra, 60, 400, colore))
    elif tipo_scelto == "TORRE":
        h = random.randint(100, 220)
        x = cesta_x - random.randint(150, 200)
        ostacoli.add(BloccoSprite(x, ALTEZZA - ALTEZZA_PAVIMENTO - h, 50, h, colore))
    elif tipo_scelto == "SCALINI":
        base_x = random.randint(250, 350)
        num_scalini = random.randint(2, 3)
        for i in range(num_scalini):
            ostacoli.add(BloccoSprite(base_x + i*80, ALTEZZA - ALTEZZA_PAVIMENTO - (i+1)*40, 80, (i+1)*40, colore))
    elif tipo_scelto == "PIATTAFORMA":
        w = random.randint(150, 250)
        h = 40
        x = random.randint(300, 450)
        y = random.randint(200, 350)
        ostacoli.add(BloccoSprite(x, y, w, h, colore))
    elif tipo_scelto == "PONTE":
        w = 300
        h = 40
        x = random.randint(300, 450)
        y = random.randint(100, 150)
        ostacoli.add(BloccoSprite(x, y, w, h, colore))
    elif tipo_scelto == "DOPPIA_COLONNA":
        h = random.randint(100, 180)
        x1 = random.randint(300, 400)
        x2 = x1 + random.randint(150, 200)
        ostacoli.add(BloccoSprite(x1, ALTEZZA - ALTEZZA_PAVIMENTO - h, 40, h, colore))
        ostacoli.add(BloccoSprite(x2, ALTEZZA - ALTEZZA_PAVIMENTO - h, 40, h, colore))

    return CestaAvanzata(cesta_x, 0)

def carica_livello(num_livello):
    global cesta, palla_ferma_counter
    reset_palla_al_lancio()
    palla_ferma_counter = 0
    cesta = genera_livello_procedurale(num_livello)

def attiva_bonus_streak():
    global vite, timer_bonus, particelle_bonus
    vite += 3
    timer_bonus = 120 
    particelle_bonus = []
    for _ in range(100):
        particelle_bonus.append(ParticellaBonus(LARGHEZZA//2, ALTEZZA//2))

def check_collisione_cerchio_rect(cx, cy, r, rect):
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    dist_x = cx - closest_x
    dist_y = cy - closest_y
    distanza_sq = dist_x**2 + dist_y**2
    
    if distanza_sq < r**2:
        dist = math.sqrt(distanza_sq)
        if dist == 0: 
            l, r_side, t, b = cx - rect.left, rect.right - cx, cy - rect.top, rect.bottom - cy
            m = min(l, r_side, t, b)
            if m == l: return True, (-1, 0), r + l
            if m == r_side: return True, (1, 0), r + r_side
            if m == t: return True, (0, -1), r + t
            return True, (0, 1), r + b
        return True, (dist_x/dist, dist_y/dist), r - dist
    return False, (0,0), 0

def aggiorna_fisica_step():
    global pos_palla, vel_palla, angolo_palla
    dt = 1.0 / SUB_STEPS
    
    angolo_palla -= vel_palla[0] * 2.5 

    for _ in range(SUB_STEPS):
        vel_palla[1] += GRAVITA * dt
        pos_palla[0] += vel_palla[0] * dt
        pos_palla[1] += vel_palla[1] * dt
        
        # Muri Schermo
        if pos_palla[0] - raggio_palla < 0:
            pos_palla[0] = raggio_palla
            vel_palla[0] *= -RIMBALZO
        if pos_palla[0] + raggio_palla > LARGHEZZA:
            pos_palla[0] = LARGHEZZA - raggio_palla
            vel_palla[0] *= -RIMBALZO
        if pos_palla[1] - raggio_palla < 0:
            pos_palla[1] = raggio_palla
            vel_palla[1] *= -RIMBALZO
        
        # Pavimento
        if pos_palla[1] + raggio_palla > ALTEZZA - ALTEZZA_PAVIMENTO:
            pos_palla[1] = ALTEZZA - ALTEZZA_PAVIMENTO - raggio_palla
            vel_palla[1] *= -RIMBALZO
            vel_palla[0] *= ATTRITO_TERRA
            if abs(vel_palla[1]) < 0.5: vel_palla[1] = 0

        # Collisioni
        colliders = [o.rect for o in ostacoli] + cesta.get_collision_rects()
        for rect in colliders:
            colpito, normale, penetration = check_collisione_cerchio_rect(pos_palla[0], pos_palla[1], raggio_palla, rect)
            if colpito:
                pos_palla[0] += normale[0] * penetration
                pos_palla[1] += normale[1] * penetration
                dot = vel_palla[0] * normale[0] + vel_palla[1] * normale[1]
                vel_palla[0] -= 2 * dot * normale[0]
                vel_palla[1] -= 2 * dot * normale[1]
                vel_palla[0] *= RIMBALZO
                vel_palla[1] *= RIMBALZO

    vel_palla[0] *= ATTRITO_ARIA
    vel_palla[1] *= ATTRITO_ARIA

    if abs(vel_palla[0]) > 1 or abs(vel_palla[1]) > 1:
        scia_palla.append(tuple(pos_palla))
        if len(scia_palla) > 15: scia_palla.pop(0)

def perdi_vita():
    global vite, stato_corrente, streak_consecutiva, cooldown_danni, high_score, coriandoli, mostra_new_record
    
    if livello_completato: return
    if cooldown_danni > 0: return 
    
    streak_consecutiva = 0 
    vite -= 1
    cooldown_danni = 30 
    
    if vite <= 0:
        vite = 0
        stato_corrente = STATO_GAMEOVER
        
        # CORREZIONE LOGICA RECORD: Salva SOLO se è maggiore
        if livelli_completati > high_score:
            mostra_new_record = True
            coriandoli = [ParticellaRecord() for _ in range(300)]
            salva_record(livelli_completati)
            high_score = livelli_completati
        else:
            mostra_new_record = False
    else:
        reset_palla_al_lancio()

def usa_bomba():
    global bombe, timer_esplosione_bomba
    if bombe > 0 and timer_esplosione_bomba == 0 and not livello_completato:
        bombe -= 1
        timer_esplosione_bomba = 60 

# --- DISEGNO ---
def disegna_ui_gioco():
    # Cuori e Vite
    schermo.blit(ASSET['icona_cuore'], (20, 20))
    testo_vite = font_ui.render(str(vite), True, NERO_DISEGNO)
    schermo.blit(testo_vite, (70, 25))

    # Bombe UI
    schermo.blit(ASSET['icona_bomba'], rect_icona_bomba)
    testo_bombe = font_ui.render(str(bombe), True, NERO_DISEGNO)
    schermo.blit(testo_bombe, (rect_icona_bomba.right + 10, rect_icona_bomba.y + 5))

    # Score Box
    box_rect = ASSET['box_score'].get_rect(topright=(LARGHEZZA - 10, 10))
    schermo.blit(ASSET['box_score'], box_rect)
    testo_score = font_score.render(str(livelli_completati), True, NERO_DISEGNO)
    score_rect = testo_score.get_rect(center=box_rect.center)
    schermo.blit(testo_score, score_rect)

    # Streak
    if streak_consecutiva > 1:
        s_text = font_ui.render(f"Streak: {streak_consecutiva}", True, GIALLO_TIGRE)
        pygame.draw.rect(schermo, NERO, s_text.get_rect(topleft=(20, 90)).inflate(10,5), border_radius=5)
        schermo.blit(s_text, (20, 90))

def disegna_animazione_bomba():
    if timer_esplosione_bomba > 0:
        raggio_max = LARGHEZZA * 1.5
        progresso = (60 - timer_esplosione_bomba) / 30.0 
        r = int(raggio_max * progresso)
        
        if progresso < 1.0:
            pygame.draw.circle(schermo, ARANCIO_ESPLOSIONE, (LARGHEZZA//2, ALTEZZA//2), r)
            pygame.draw.circle(schermo, BIANCO, (LARGHEZZA//2, ALTEZZA//2), int(r*0.8))
        else:
            s = pygame.Surface((LARGHEZZA, ALTEZZA))
            s.fill(BIANCO)
            alpha = int(255 * (timer_esplosione_bomba / 30.0))
            s.set_alpha(alpha)
            schermo.blit(s, (0,0))

def disegna_menu():
    schermo.blit(ASSET['sfondo'], (0,0))
    
    # Titolo
    titolo = font_grande.render("TIGERBALL CLONE", True, GIALLO_TIGRE)
    outline = font_grande.render("TIGERBALL CLONE", True, NERO)
    schermo.blit(outline, (LARGHEZZA//2 - outline.get_width()//2 + 4, 104))
    schermo.blit(titolo, (LARGHEZZA//2 - titolo.get_width()//2, 100))
    
    # Istruzioni
    istruzioni = [
        "COME GIOCARE:",
        "1. Trascina mouse per mirare (Verde=Piano, Rosso=Forte)",
        "2. Fai canestro per superare il livello",
        "3. Premi [SPAZIO] se ti blocchi (costa 1 vita)",
        "4. STREAK: 3 Canestri di fila = +3 VITE BONUS!",
        "5. USA LA BOMBA per saltare i livelli difficili!"
    ]
    
    start_y = 230
    box_sfondo = pygame.Surface((800, 240))
    box_sfondo.set_alpha(150)
    box_sfondo.fill(NERO)
    schermo.blit(box_sfondo, (LARGHEZZA//2 - 400, start_y - 10))

    for i, riga in enumerate(istruzioni):
        colore = BIANCO
        if i == 0: colore = GIALLO_TIGRE
        elif "STREAK" in riga: colore = GIALLO_TIGRE
        elif "BOMBA" in riga: colore = ARANCIO_ESPLOSIONE
            
        t_surf = font_instr.render(riga, True, colore)
        t_rect = t_surf.get_rect(center=(LARGHEZZA//2, start_y + i*32))
        schermo.blit(t_surf, t_rect)

    # Mostra Record
    record_text = font_ui.render(f"MIGLIOR RECORD: {high_score}", True, ORO_BONUS)
    schermo.blit(record_text, record_text.get_rect(center=(LARGHEZZA//2, start_y + 250)))

    # Pulsante Gioca (SPOSTATO IN BASSO)
    pulsante_play.check_hover(pygame.mouse.get_pos())
    pulsante_play.draw(schermo)

def disegna_gameover():
    s = pygame.Surface((LARGHEZZA, ALTEZZA))
    s.set_alpha(150)
    s.fill(NERO)
    schermo.blit(s, (0,0))
    
    # Animazione Coriandoli per Record
    if len(coriandoli) > 0 and mostra_new_record:
        for c in coriandoli:
            c.update()
            c.draw(schermo)

    titolo = font_grande.render("HAI PERSO!", True, ROSSO_CUORE)
    rect_titolo = titolo.get_rect(center=(LARGHEZZA//2, 200))
    schermo.blit(titolo, rect_titolo)
    
    info = font_ui.render(f"Livelli Superati: {livelli_completati}", True, BIANCO)
    schermo.blit(info, info.get_rect(center=(LARGHEZZA//2, 300)))
    
    if mostra_new_record:
        rec_msg = font_bonus.render("NUOVO RECORD!!!", True, ORO_BONUS)
        outline = font_bonus.render("NUOVO RECORD!!!", True, NERO)
        r = rec_msg.get_rect(center=(LARGHEZZA//2, 400))
        schermo.blit(outline, (r.x+4, r.y+4))
        schermo.blit(rec_msg, r)
    else:
        rec_msg = font_ui.render(f"Record attuale: {high_score}", True, TEAL_SFONDO)
        schermo.blit(rec_msg, rec_msg.get_rect(center=(LARGHEZZA//2, 400)))

    pulsante_menu.check_hover(pygame.mouse.get_pos())
    pulsante_menu.draw(schermo)

def disegna_bonus_screen():
    s = pygame.Surface((LARGHEZZA, ALTEZZA))
    s.set_alpha(100)
    s.fill(NERO)
    schermo.blit(s, (0,0))
    testo = font_bonus.render("STREAK BONUS!", True, ORO_BONUS)
    outline = font_bonus.render("STREAK BONUS!", True, NERO)
    r = testo.get_rect(center=(LARGHEZZA//2, ALTEZZA//2 - 50))
    schermo.blit(outline, (r.x+4, r.y+4))
    schermo.blit(testo, r)
    testo_vite = font_bonus.render("+3 VITE", True, ROSSO_CUORE)
    r2 = testo_vite.get_rect(center=(LARGHEZZA//2, ALTEZZA//2 + 50))
    schermo.blit(testo_vite, r2)
    for p in particelle_bonus:
        p.update()
        p.draw(schermo)

def disegna_gioco():
    schermo.blit(ASSET['sfondo'], (0, 0))
    schermo.blit(ASSET['pavimento'], (0, ALTEZZA - ALTEZZA_PAVIMENTO))

    # Linea traiettoria DINAMICA
    if is_dragging and not livello_completato:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = start_pos[0] - mouse_x
        dy = start_pos[1] - mouse_y
        
        distanza_trascinamento = math.hypot(dx, dy)
        intensita = min(1.0, distanza_trascinamento / 350.0)
        
        r_col = int(255 * intensita)
        g_col = int(255 * (1 - intensita))
        colore_linea = (r_col, g_col, 0)

        sim_pos = list(pos_palla)
        sim_vel = [dx / LANCIO_POTENZA, dy / LANCIO_POTENZA]
        points = []
        
        collision_boxes = [o.rect for o in ostacoli] + cesta.get_collision_rects()
        collision_boxes.append(pygame.Rect(0, ALTEZZA - ALTEZZA_PAVIMENTO, LARGHEZZA, 100))

        for _ in range(30):
            sim_vel[1] += GRAVITA 
            sim_pos[0] += sim_vel[0]
            sim_pos[1] += sim_vel[1]
            points.append(tuple(sim_pos))
            
            colpito = False
            r_sim = pygame.Rect(sim_pos[0]-2, sim_pos[1]-2, 4, 4)
            for box in collision_boxes:
                if r_sim.colliderect(box):
                    colpito = True
                    break
            if colpito: break
        
        if len(points) > 1:
            pygame.draw.lines(schermo, colore_linea, False, points, 6)
            pygame.draw.lines(schermo, NERO_DISEGNO, False, points, 2)

    schermo.blit(cesta.image, cesta.rect)
    ostacoli.draw(schermo)
    
    # Disegno Scia
    for i, pos in enumerate(scia_palla):
        alpha = int(255 * (i / len(scia_palla)))
        r = int(raggio_palla * (i / len(scia_palla)) * 0.8)
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*GIALLO_TIGRE, alpha), (r, r), r)
        schermo.blit(s, (pos[0] - r, pos[1] - r))

    # Disegno Palla con ROTAZIONE
    palla_ruotata = pygame.transform.rotate(ASSET['palla'], angolo_palla)
    rect_ruotato = palla_ruotata.get_rect(center=(pos_palla[0], pos_palla[1]))
    schermo.blit(palla_ruotata, rect_ruotato)
    
    # Animazione Bomba
    if timer_esplosione_bomba > 0:
        disegna_animazione_bomba()
    
    disegna_ui_gioco()
    
    if timer_bonus > 0:
        disegna_bonus_screen()

# --- MAIN LOOP ---
gioco_attivo = True

while gioco_attivo:
    if cooldown_danni > 0:
        cooldown_danni -= 1

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            gioco_attivo = False
        
        if stato_corrente == STATO_MENU:
            if pulsante_play.is_clicked(evento):
                vite = 5
                bombe = 3 
                livelli_completati = 0
                livello_corrente = 1
                streak_consecutiva = 0
                coriandoli = [] # Reset coriandoli
                mostra_new_record = False # Reset flag record
                carica_livello(1)
                stato_corrente = STATO_GIOCO

        elif stato_corrente == STATO_GAMEOVER:
            if pulsante_menu.is_clicked(evento):
                coriandoli = [] # Reset coriandoli
                stato_corrente = STATO_MENU

        elif stato_corrente == STATO_GIOCO:
            if timer_bonus > 0:
                continue
            if timer_esplosione_bomba > 0:
                continue 

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if cooldown_danni == 0:
                        perdi_vita()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Check click su icona bomba
                if rect_icona_bomba.collidepoint(evento.pos):
                    usa_bomba()
                
                # Input normale gioco
                elif not livello_completato and not palla_in_gioco:
                    mx, my = evento.pos
                    if math.hypot(pos_palla[0]-mx, pos_palla[1]-my) < 100:
                        is_dragging = True
                        start_pos = evento.pos
                        scia_palla = []

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and is_dragging:
                is_dragging = False
                palla_in_gioco = True 
                end_pos = evento.pos
                dx = start_pos[0] - end_pos[0]
                dy = start_pos[1] - end_pos[1]
                vel_palla[0] = dx / LANCIO_POTENZA
                vel_palla[1] = dy / LANCIO_POTENZA
                palla_ferma_counter = 0

    if stato_corrente == STATO_GIOCO:
        # Gestione Animazione Bomba
        if timer_esplosione_bomba > 0:
            timer_esplosione_bomba -= 1
            if timer_esplosione_bomba == 10: 
                 print(f"Bomba usata! Livello {livello_corrente} saltato.")
                 livello_completato = True
                 pygame.display.flip()
                 pygame.time.wait(100)
                 livelli_completati += 1
                 livello_corrente += 1
                 carica_livello(livello_corrente)
        
        elif timer_bonus > 0:
            timer_bonus -= 1
            if timer_bonus == 0:
                livelli_completati += 1
                livello_corrente += 1
                carica_livello(livello_corrente)
        else:
            if not is_dragging:
                aggiorna_fisica_step()
                
                if not livello_completato and palla_in_gioco:
                    is_stopped = abs(vel_palla[0]) < 0.2 and abs(vel_palla[1]) < 0.2
                    on_ground = pos_palla[1] > ALTEZZA - ALTEZZA_PAVIMENTO - raggio_palla - 5
                    
                    if is_stopped and on_ground:
                        palla_ferma_counter += 1
                        if palla_ferma_counter > 90:
                            perdi_vita()
                            palla_ferma_counter = 0
                    
                    if pos_palla[0] < -50 or pos_palla[0] > LARGHEZZA + 50 or pos_palla[1] > ALTEZZA + 50:
                        perdi_vita()

                if not livello_completato and cesta.zona_vittoria.collidepoint((pos_palla[0], pos_palla[1])):
                    if vel_palla[1] > 0 or abs(vel_palla[1]) < 1:
                        print(f"Livello {livello_corrente} completato!")
                        livello_completato = True 
                        streak_consecutiva += 1
                        
                        if streak_consecutiva > 0 and streak_consecutiva % 3 == 0:
                            attiva_bonus_streak()
                        else:
                            pygame.display.flip()
                            pygame.time.wait(400) 
                            livelli_completati += 1
                            livello_corrente += 1
                            carica_livello(livello_corrente)

    if stato_corrente == STATO_MENU:
        disegna_menu()
    elif stato_corrente == STATO_GIOCO:
        disegna_gioco()
    elif stato_corrente == STATO_GAMEOVER:
        disegna_gioco()
        disegna_gameover()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
