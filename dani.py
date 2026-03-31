import pygame
import math
import random
import sys

# Inizializzazione
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# ======================
# CONFIGURAZIONE
# ======================
WIDTH, HEIGHT = 1200, 700
BOTTOM_BAR_HEIGHT = 120
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie TD - Real Spinning Minigun")
CLOCK = pygame.time.Clock()

# Font
FONT = pygame.font.SysFont("arial", 14)
BIG_FONT = pygame.font.SysFont("arial", 18, bold=True)
WAVE_FONT = pygame.font.SysFont("arial", 36, bold=True)
REWARD_FONT = pygame.font.SysFont("arial", 60, bold=True)
LABEL_FONT = pygame.font.SysFont("arial", 16, bold=True)

# Colori
WHITE, BLACK, GRAY = (255,255,255), (0,0,0), (100,100,100)
GREEN, RED, BLUE = (0,200,0), (200,0,0), (0,120,255)
BROWN, GOLD, ORANGE, YELLOW, PURPLE = (139,69,19), (255,215,0), (255,140,0), (255,255,0), (160, 32, 240)
DARK_GREEN = (20, 80, 20)

PATH_POINTS = [(0,300), (300,300), (300,200), (500,200), (500,420), (700,420), (700,300), (1100,300)]
PATH_WIDTH = 80
BASE_RECT = pygame.Rect(1080, 240, 80, 120)
MAX_WAVES, MAX_TOWERS = 20, 20

TOWER_TYPES = {
    1: {"name": "Melee", "cost": 120, "color": BLUE, "range": 95, "damage": 25, "cooldown": 0.75},
    2: {"name": "Archer", "cost": 250, "color": GREEN, "range": 260, "damage": 16, "cooldown": 0.7},
    3: {"name": "Grenadier", "cost": 450, "color": ORANGE, "range": 180, "damage": 45, "cooldown": 1.8},
    4: {"name": "Minigunner", "cost": 1500, "color": RED, "range": 210, "damage": 4, "cooldown": 0.1},
}

# ======================
# FUNZIONE DISEGNO MODELLI
# ======================
def draw_troop_model(surface, x, y, tid, color, stun_timer, last_attack, cooldown, angle):
    is_stunned = stun_timer > 0
    main_color = color if not is_stunned else GRAY
    atk_progress = min(1.0, last_attack / cooldown)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    
    # Corpo base
    pygame.draw.circle(surface, (20, 20, 20), (int(x)+2, int(y)+2), 18)
    pygame.draw.circle(surface, main_color, (int(x), int(y)), 16)

    if tid == 1: # MELEE: Spada a tempo
        slash_anim = (0.2 - atk_progress) * 12 if (not is_stunned and atk_progress < 0.2) else 0
        sw_angle = angle + 0.8 - (slash_anim * 1.5)
        pygame.draw.line(surface, (220, 220, 220), (x, y), (x+math.cos(sw_angle)*30, y+math.sin(sw_angle)*30), 5)
        pygame.draw.line(surface, (100, 50, 0), (x, y), (x+math.cos(sw_angle)*8, y+math.sin(sw_angle)*8), 7)

    elif tid == 2: # ARCHER
        pull = 0 if is_stunned else (8 * atk_progress)
        arc_pts = [(x + math.cos(angle + i*0.1)*18, y + math.sin(angle + i*0.1)*18) for i in range(-10, 11)]
        pygame.draw.lines(surface, WHITE, False, arc_pts, 3)
        pygame.draw.line(surface, (200,200,200), arc_pts[0], (x - cos_a*pull, y - sin_a*pull), 1)
        pygame.draw.line(surface, (200,200,200), arc_pts[-1], (x - cos_a*pull, y - sin_a*pull), 1)
        if atk_progress > 0.6 and not is_stunned:
            pygame.draw.line(surface, BROWN, (x-cos_a*pull, y-sin_a*pull), (x+cos_a*(22-pull), y+sin_a*(22-pull)), 2)

    elif tid == 3: # GRENADIER
        pygame.draw.line(surface, (40, 40, 40), (x, y), (x + cos_a * 24, y + sin_a * 24), 12)
        pygame.draw.circle(surface, (60, 60, 60), (int(x + cos_a*8), int(y + sin_a*8)), 9)

    elif tid == 4: # REAL SPINNING MINIGUN
        weapon_x = x + math.cos(angle + 0.5) * 12
        weapon_y = y + math.sin(angle + 0.5) * 12
        pygame.draw.circle(surface, (30,30,30), (int(weapon_x), int(weapon_y)), 8) # Ricevitore
        
        spin = pygame.time.get_ticks() * 0.05 if (not is_stunned and atk_progress < 0.5) else 0
        for i in range(3):
            offset_a = spin + (i * 2.09)
            off_dist = math.sin(offset_a) * 4 
            
            barrel_end_x = weapon_x + cos_a * 26 - sin_a * off_dist
            barrel_end_y = weapon_y + sin_a * 26 + cos_a * off_dist
            
            b_color = (20, 20, 20) if math.cos(offset_a) > 0 else (50, 50, 50)
            pygame.draw.line(surface, b_color, (weapon_x, weapon_y), (barrel_end_x, barrel_end_y), 3)

    pygame.draw.circle(surface, (40, 40, 40), (int(x), int(y)), 7)

# ======================
# CLASSI
# ======================

class Enemy:
    def __init__(self, wave, type="normal"):
        self.type = type
        self.path_index = 0
        self.x, self.y = float(PATH_POINTS[0][0]), float(PATH_POINTS[0][1])
        base_hp = (40 + (wave * 18)) * 1.5
        
        if type == "boss":
            self.max_hp, self.speed, self.reward, self.radius, self.color = base_hp * 8, 0.6, 500, 28, (130,0,0)
        elif type == "witch":
            self.max_hp, self.speed, self.reward, self.radius, self.color = base_hp * 3, 0.65, 150, 20, PURPLE
            self.ability_range, self.ability_cooldown, self.last_ability = 220, 5.0, 0
        elif type == "fast":
            self.max_hp, self.speed, self.reward, self.radius, self.color = base_hp * 0.4, 2.6, 25, 12, YELLOW
        else:
            self.max_hp, self.speed, self.reward, self.radius, self.color = base_hp, 1.3, 35, 16, (0,180,0)
        self.hp = self.max_hp

    def update(self, dt_mult, towers):
        if self.path_index >= len(PATH_POINTS)-1: return True
        tx, ty = PATH_POINTS[self.path_index+1]
        dx, dy = tx-self.x, ty-self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt_mult
        if dist < step: self.path_index += 1
        else: self.x += (dx/dist)*step; self.y += (dy/dist)*step
        
        if self.type == "witch":
            self.last_ability += (1/60) * dt_mult
            if self.last_ability >= self.ability_cooldown:
                targets = [t for t in towers if math.hypot(self.x-t.x, self.y-t.y) <= self.ability_range]
                if targets:
                    for t in random.sample(targets, min(2, len(targets))): t.stun_timer = 3.0
                    self.last_ability = 0
        return False

    def draw(self):
        if self.type == "witch":
            s = pygame.Surface((self.ability_range*2, self.ability_range*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (160, 32, 240, 40), (self.ability_range, self.ability_range), self.ability_range, 2)
            SCREEN.blit(s, (self.x - self.ability_range, self.y - self.ability_range))
        
        pygame.draw.circle(SCREEN, (20, 40, 20), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(SCREEN, self.color, (int(self.x), int(self.y)), self.radius-2)
        eye_c = WHITE if self.type != "boss" else YELLOW
        pygame.draw.circle(SCREEN, eye_c, (int(self.x+4), int(self.y-4)), 3)
        pygame.draw.circle(SCREEN, eye_c, (int(self.x+4), int(self.y+4)), 3)

        r = max(0, self.hp / self.max_hp)
        pygame.draw.rect(SCREEN, RED, (self.x-20, self.y-self.radius-10, 40, 5))
        pygame.draw.rect(SCREEN, GREEN, (self.x-20, self.y-self.radius-10, 40*r, 5))

class Tower:
    def __init__(self, x, y, tid):
        self.tid, self.x, self.y, self.level, self.stun_timer = tid, x, y, 1, 0
        self.last_attack, self.total_spent = 0, TOWER_TYPES[tid]["cost"]
        self.aim_angle = 0
        self.apply_stats()

    def get_stats(self, lvl):
        m = 1.5 ** (lvl - 1)
        d = TOWER_TYPES[self.tid]
        return {"range": d["range"]*(1.1**(lvl-1)), "damage": d["damage"]*m, "cooldown": d["cooldown"]/(1.2**(lvl-1))}

    def apply_stats(self):
        s = self.get_stats(self.level)
        self.range, self.damage, self.cooldown, self.color = s["range"], s["damage"], s["cooldown"], TOWER_TYPES[self.tid]["color"]

    def attack(self, enemies, projectiles, slashes, dt_mult):
        target_e = None
        closest_dist = self.range
        for e in enemies:
            dist = math.hypot(self.x-e.x, self.y-e.y)
            if dist <= self.range:
                if dist < closest_dist: closest_dist = dist; target_e = e
        
        if target_e and self.stun_timer <= 0:
            self.aim_angle = math.atan2(target_e.y - self.y, target_e.x - self.x)

        if self.stun_timer > 0:
            self.stun_timer -= (1/60) * dt_mult
            return
            
        self.last_attack += (1/60) * dt_mult
        if self.last_attack >= self.cooldown and target_e:
            if self.tid == 1:
                slashes.append(SlashEffect(self.x, self.y, self.aim_angle))
                target_e.hp -= self.damage
            else:
                projectiles.append(Projectile(self.x, self.y, target_e, self.damage, 10, self.tid))
            self.last_attack = 0

    def draw(self, alpha=255, is_ghost=False, valid=True, mouse_pos=(0,0)):
        c = self.color if valid else RED
        rs = pygame.Surface((int(self.range*2), int(self.range*2)), pygame.SRCALPHA)
        pygame.draw.circle(rs, (*c, 40 if not is_ghost else 80), (int(self.range), int(self.range)), int(self.range), 2)
        SCREEN.blit(rs, (self.x - self.range, self.y - self.range))
        
        draw_angle = self.aim_angle
        if is_ghost: draw_angle = math.atan2(mouse_pos[1] - self.y, mouse_pos[0] - self.x)
        draw_troop_model(SCREEN, self.x, self.y, self.tid, self.color, self.stun_timer, self.last_attack, self.cooldown, draw_angle)

        if not is_ghost:
            SCREEN.blit(FONT.render(f"L{self.level}", True, WHITE), (self.x-8, self.y-38))
            if self.stun_timer > 0: SCREEN.blit(FONT.render("STUN!", True, YELLOW), (self.x-15, self.y+22))

class SlashEffect:
    def __init__(self, x, y, angle): self.x, self.y, self.angle, self.timer = x, y, angle, 6
    def draw(self):
        s = pygame.Surface((90, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255, 255, 255, int((self.timer/6)*200)), (0, 0, 90, 25))
        rot = pygame.transform.rotate(s, -math.degrees(self.angle))
        SCREEN.blit(rot, rot.get_rect(center=(self.x + math.cos(self.angle)*45, self.y + math.sin(self.angle)*45)))
        self.timer -= 1

class Projectile:
    def __init__(self, x, y, target, damage, speed, tid):
        self.x, self.y, self.target, self.damage, self.speed, self.tid, self.reached = x, y, target, damage, speed, tid, False
        self.is_bomb = (tid == 3)
    def move(self, dt_mult):
        dx, dy = self.target.x-self.x, self.target.y-self.y
        d = math.hypot(dx, dy)
        step = self.speed * dt_mult
        if d < step: self.reached = True
        else: self.x += (dx/d)*step; self.y += (dy/d)*step

class Explosion:
    def __init__(self, x, y, rad, dmg): self.x, self.y, self.rad, self.dmg, self.timer = x, y, rad, dmg, 10
    def draw(self):
        s = pygame.Surface((self.rad*2, self.rad*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 120, 0, int((self.timer/10)*150)), (self.rad, self.rad), self.rad)
        SCREEN.blit(s, (self.x-self.rad, self.y-self.rad)); self.timer -= 1

def can_place(pos, towers):
    if len(towers) >= MAX_TOWERS or pos[1] > HEIGHT-BOTTOM_BAR_HEIGHT-30 or BASE_RECT.collidepoint(pos): return False
    for t in towers: 
        if math.hypot(pos[0]-t.x, pos[1]-t.y) < 45: return False
    for i in range(len(PATH_POINTS)-1):
        x1, y1, x2, y2 = *PATH_POINTS[i], *PATH_POINTS[i+1]
        dx, dy = x2-x1, y2-y1
        t_val = max(0, min(1, ((pos[0]-x1)*dx + (pos[1]-y1)*dy) / (dx*dx+dy*dy) if dx*dx+dy*dy != 0 else 1))
        if math.hypot(pos[0]-(x1+t_val*dx), pos[1]-(y1+t_val*dy)) < 60: return False
    return True

# ======================
# STATO GIOCO
# ======================
money, base_hp = 1200, 100
towers, enemies, projectiles, explosions, slashes = [], [], [], [], []
current_wave, spawn_queue = 0, []
selected_t, ghost_type = None, None
game_speed, show_reward, reward_timer = 1, False, 0
game_over = victory = False

# ======================
# LOOP PRINCIPALE
# ======================
while True:
    mx, my = pygame.mouse.get_pos()
    dt = game_speed
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not game_over and not victory:
                if pygame.Rect(10, HEIGHT-110, 80, 40).collidepoint(mx, my): game_speed = 2 if game_speed==1 else 1
                elif ghost_type:
                    if money >= TOWER_TYPES[ghost_type]["cost"] and can_place((mx,my), towers):
                        towers.append(Tower(mx, my, ghost_type)); money -= TOWER_TYPES[ghost_type]["cost"]; ghost_type = None
                elif selected_t:
                    if pygame.Rect(100, HEIGHT-95, 110, 35).collidepoint(mx, my) and selected_t.level < 4:
                        cost = int(TOWER_TYPES[selected_t.tid]["cost"] * 0.9 * selected_t.level)
                        if money >= cost: money -= cost; selected_t.total_spent += cost; selected_t.level += 1; selected_t.apply_stats()
                    elif pygame.Rect(220, HEIGHT-95, 110, 35).collidepoint(mx, my):
                        money += int(selected_t.total_spent * 0.4); towers.remove(selected_t); selected_t = None
                    else:
                        selected_t = None
                        for t in towers: 
                            if math.hypot(mx-t.x, my-t.y) < 25: selected_t = t; break
                else:
                    for t in towers: 
                        if math.hypot(mx-t.x, my-t.y) < 25: selected_t = t; break
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]: ghost_type = int(event.unicode)
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q: ghost_type = selected_t = None

    if not game_over and not victory:
        if not enemies and not spawn_queue and not show_reward:
            if current_wave >= MAX_WAVES: victory = True
            elif current_wave > 0:
                money += int(250 * (1.1 ** current_wave))
                show_reward, reward_timer = True, pygame.time.get_ticks()
            else:
                current_wave += 1; spawn_queue = [Enemy(current_wave, "normal") for _ in range(8)]
        
        if show_reward and pygame.time.get_ticks() - reward_timer > 1000:
            show_reward = False; current_wave += 1
            if current_wave % 5 == 0: spawn_queue = [Enemy(current_wave, "boss")]
            else:
                for _ in range(8 + current_wave): spawn_queue.append(Enemy(current_wave, "fast" if random.random()<0.3 else "normal"))
                if current_wave % 4 == 0: spawn_queue.append(Enemy(current_wave, "witch"))

        if spawn_queue and len(spawn_queue) > 0 and random.random() < 0.2 * dt: 
            enemies.append(spawn_queue.pop(0))

        for t in towers: t.attack(enemies, projectiles, slashes, dt)
        for e in enemies[:]:
            if e.update(dt, towers): base_hp -= (40 if e.type=="boss" else 10); enemies.remove(e)
            elif e.hp <= 0: money += e.reward; enemies.remove(e)
        
        for p in projectiles[:]:
            p.move(dt)
            if p.reached or p.target not in enemies:
                if p.reached and p.target in enemies:
                    if p.is_bomb:
                        explosions.append(Explosion(p.x, p.y, 85, p.damage))
                        for e in enemies: 
                            if math.hypot(p.x-e.x, p.y-e.y) < 85: e.hp -= p.damage
                    else: p.target.hp -= p.damage
                projectiles.remove(p)
        if base_hp <= 0: game_over = True

    # --- DISEGNO ---
    SCREEN.fill(DARK_GREEN)
    for i in range(len(PATH_POINTS)-1): pygame.draw.line(SCREEN, BROWN, PATH_POINTS[i], PATH_POINTS[i+1], PATH_WIDTH)
    pygame.draw.rect(SCREEN, (60,60,60), BASE_RECT); pygame.draw.rect(SCREEN, BLACK, BASE_RECT, 3)
    
    for t in towers: t.draw()
    for s in slashes[:]: s.draw(); (slashes.remove(s) if s.timer<=0 else None)
    for e in enemies: e.draw()

    for p in projectiles:
        p_angle = math.atan2(p.target.y - p.y, p.target.x - p.x)
        if p.tid == 2: # Freccia
            end_x = p.x + math.cos(p_angle) * 15
            end_y = p.y + math.sin(p_angle) * 15
            pygame.draw.line(SCREEN, WHITE, (p.x, p.y), (end_x, end_y), 2)
        elif p.tid == 3: # Granata
            pygame.draw.circle(SCREEN, BLACK, (int(p.x), int(p.y)), 5); pygame.draw.circle(SCREEN, ORANGE, (int(p.x), int(p.y)), 3)
        else: # Minigun
            pygame.draw.circle(SCREEN, YELLOW, (int(p.x), int(p.y)), 2)

    for ex in explosions[:]: ex.draw(); (explosions.remove(ex) if ex.timer<=0 else None)
    if ghost_type:
        valid = can_place((mx, my), towers)
        Tower(mx, my, ghost_type).draw(alpha=120, is_ghost=True, valid=valid, mouse_pos=(mx,my))

    # UI BARRA INFERIORE
    pygame.draw.rect(SCREEN, GRAY, (0, HEIGHT-BOTTOM_BAR_HEIGHT, WIDTH, BOTTOM_BAR_HEIGHT))
    pygame.draw.line(SCREEN, WHITE, (0, HEIGHT-BOTTOM_BAR_HEIGHT), (WIDTH, HEIGHT-BOTTOM_BAR_HEIGHT), 3)
    SCREEN.blit(BIG_FONT.render(f"SOLDI: ${money}", True, WHITE), (350, HEIGHT-100))
    SCREEN.blit(BIG_FONT.render(f"BASE HP: {base_hp}", True, WHITE), (350, HEIGHT-50))
    SCREEN.blit(WAVE_FONT.render(f"WAVE: {current_wave}/{MAX_WAVES}", True, WHITE), (WIDTH-220, 20))

    for i in range(1, 5):
        bx = pygame.Rect(650 + (i-1)*130, HEIGHT-110, 120, 100)
        pygame.draw.rect(SCREEN, BLACK, bx, 2)
        draw_troop_model(SCREEN, bx.centerx, bx.y + 30, i, TOWER_TYPES[i]["color"], 0, 1, 1, 0)
        SCREEN.blit(FONT.render(f"[{i}] {TOWER_TYPES[i]['name']}", True, BLACK), (bx.x+10, bx.y+55))
        SCREEN.blit(BIG_FONT.render(f"${TOWER_TYPES[i]['cost']}", True, (30,30,30)), (bx.x+10, bx.y+75))

    if selected_t:
        pygame.draw.rect(SCREEN, (40,40,40), (10, HEIGHT-310, 250, 190)); pygame.draw.rect(SCREEN, WHITE, (10, HEIGHT-310, 250, 190), 2)
        
        # Statistiche Correnti e Prossime
        st = selected_t.get_stats(selected_t.level)
        nxt = selected_t.get_stats(selected_t.level + 1) if selected_t.level < 4 else None
        
        SCREEN.blit(BIG_FONT.render(f"{TOWER_TYPES[selected_t.tid]['name']} L{selected_t.level}", True, GOLD), (20, HEIGHT-300))
        
        stats_labels = [
            ("Danno:", st["damage"], nxt["damage"] if nxt else None),
            ("Range:", st["range"], nxt["range"] if nxt else None),
            ("Velocità:", 1/st["cooldown"], 1/nxt["cooldown"] if nxt else None)
        ]
        
        for i, (label, cur_val, nxt_val) in enumerate(stats_labels):
            y_pos = HEIGHT - 265 + (i * 25)
            # Testo statistica attuale
            txt = f"{label} {cur_val:.1f}"
            SCREEN.blit(FONT.render(txt, True, WHITE), (20, y_pos))
            # Se esiste un livello successivo, mostra il miglioramento
            if nxt_val:
                upgrade_txt = f" -> {nxt_val:.1f}"
                SCREEN.blit(FONT.render(upgrade_txt, True, GREEN), (120, y_pos))

        up_c = int(TOWER_TYPES[selected_t.tid]["cost"] * 0.9 * selected_t.level)
        if selected_t.level < 4:
            pygame.draw.rect(SCREEN, GREEN if money>=up_c else GRAY, (100, HEIGHT-95, 110, 35))
            SCREEN.blit(FONT.render(f"UP: ${up_c}", True, WHITE), (110, HEIGHT-85))
        else:
            SCREEN.blit(BIG_FONT.render("MAX LIVELLO", True, YELLOW), (100, HEIGHT-85))

        pygame.draw.rect(SCREEN, RED, (220, HEIGHT-95, 110, 35)); SCREEN.blit(FONT.render(f"SELL: ${int(selected_t.total_spent*0.4)}", True, WHITE), (230, HEIGHT-85))

    pygame.draw.rect(SCREEN, GOLD if game_speed==2 else WHITE, (10, HEIGHT-110, 80, 40)); SCREEN.blit(FONT.render(f"SPEED: {game_speed}x", True, BLACK), (15, HEIGHT-98))
    if show_reward:
        txt = REWARD_FONT.render("ONDATA COMPLETATA!", True, GOLD)
        SCREEN.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2-50)))
    if game_over or victory:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((150, 0, 0, 180) if game_over else (0, 150, 0, 180)); SCREEN.blit(overlay, (0, 0))
        msg = REWARD_FONT.render("GAME OVER" if game_over else "VITTORIA!", True, WHITE); SCREEN.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pygame.display.flip(); CLOCK.tick(60)


