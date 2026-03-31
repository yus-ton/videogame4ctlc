# menu.py
# Retro Launcher anni '90 + config testi (JSON) + chiptune 8-bit (WAV)
#
# Requisiti:
# - Metti nella stessa cartella di questo file:
#     - pycade_menu_text_config.json
#     - chiptune_8bit_loop.wav
# - I progetti devono stare nelle posizioni indicate nel JSON (path relativi).
#
# Avvio:
#   python menu.py

import json
import os
import sys
import time
import random
import subprocess
from pathlib import Path

import pygame


# ----------------------------- Config -----------------------------
WIDTH, HEIGHT = 980, 640
FPS = 60

BG = (10, 10, 18)
FG = (240, 240, 240)
DIM = (160, 160, 160)
ACCENT = (255, 210, 80)
ACCENT2 = (80, 220, 255)
RED = (255, 90, 90)

CONFIG_FILE = "auracade.json"


def load_config(root: Path) -> dict:
    cfg_path = root / CONFIG_FILE
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Config non trovata: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_get(d: dict, path: str, default):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def run_project(project: dict, root: Path):
    # Path e cwd
    rel_file = project["file"]
    abs_path = (root / rel_file).resolve()
    cwd = abs_path.parent
    entry = abs_path.name

    if not abs_path.is_file():
        raise FileNotFoundError(rel_file)

    # Avvio con lo stesso python del menu
    cmd = [sys.executable, entry]
    return subprocess.run(cmd, cwd=str(cwd))


# ----------------------------- Retro visuals -----------------------------
def draw_scanlines(surface):
    w, h = surface.get_size()
    for y in range(0, h, 4):
        pygame.draw.line(surface, (0, 0, 0), (0, y), (w, y), 1)


def draw_starfield(surface, stars):
    w, h = surface.get_size()
    for s in stars:
        s["x"] = (s["x"] - s["spd"]) % w
        pygame.draw.circle(surface, s["c"], (int(s["x"]), int(s["y"])), s["r"])


def blit_text(surface, font, msg, x, y, color=FG):
    img = font.render(msg, True, color)
    surface.blit(img, (x, y))


def center_text(surface, font, msg, y, color=FG):
    img = font.render(msg, True, color)
    rect = img.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(img, rect)


def wrap_lines(text: str, max_chars: int) -> list[str]:
    # wrapping semplice basato su numero caratteri, sufficiente per pannello descrizione
    words = text.split()
    lines, cur = [], []
    count = 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if count + add > max_chars and cur:
            lines.append(" ".join(cur))
            cur = [w]
            count = len(w)
        else:
            cur.append(w)
            count += add
    if cur:
        lines.append(" ".join(cur))
    return lines

def wrap_text_px(font, text, max_width_px):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = w if not cur else cur + " " + w
        if font.size(test)[0] <= max_width_px:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ----------------------------- Main -----------------------------
def main():
    root = Path(__file__).resolve().parent
    cfg = load_config(root)

    # Testi menu
    banners = safe_get(cfg, "menu_text.banners", ["== PY-CADE 199X =="])
    footer_tips = safe_get(cfg, "menu_text.footer_tips", ["TIP: ↑↓ / ENTER / ESC"])
    labels = safe_get(cfg, "menu_text.labels", {})
    screen_text = safe_get(cfg, "menu_text.screen_text", {})

    # Progetti
    projects = safe_get(cfg, "projects", [])
    if not projects:
        raise RuntimeError("Nessun progetto trovato nel JSON (chiave 'projects').")

    # Struttura
    structure = safe_get(cfg, "structure", {})
    show_rel_path = bool(structure.get("show_rel_path", True))
    show_desc_panel = bool(structure.get("show_description_panel", True))
    desc_fields = structure.get("description_panel_fields", ["short_tagline", "description", "controls"])
    max_desc_chars = int(structure.get("max_description_chars", 600))

    # Audio
    audio_cfg = safe_get(cfg, "audio", {})
    audio_enabled = bool(audio_cfg.get("enabled", True))
    audio_file = audio_cfg.get("file", "chiptune_8bit_loop.wav")
    audio_volume = float(audio_cfg.get("volume", 0.35))

    # Pre-check file mancanti (non blocca)
    missing = []
    for p in projects:
        rel = p.get("file", "")
        if rel:
            if not (root / rel).is_file():
                missing.append(rel)

    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption(safe_get(cfg, "meta.title", "PY-CADE 199X"))
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Avvio musichetta in loop
    if audio_enabled:
        wav_path = root / audio_file
        if wav_path.is_file():
            pygame.mixer.music.load(str(wav_path))
            pygame.mixer.music.set_volume(audio_volume)
            pygame.mixer.music.play(-1)
        else:
            # non crashiamo: semplicemente senza musica
            audio_enabled = False

    # Font
    font_big = pygame.font.Font(None, 64)
    font_med = pygame.font.Font(None, 34)
    font_small = pygame.font.Font(None, 24)

    # Starfield
    stars = []
    for _ in range(120):
        tw = random.randint(170, 240)
        stars.append(
            {
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "spd": random.uniform(0.6, 2.2),
                "r": random.choice([1, 1, 1, 2]),
                "c": (tw, tw, tw),
            }
        )

    idx = 0
    banner = random.choice(banners)
    tip = random.choice(footer_tips)
    tip_change_at = time.time() + 3.0

    error_msg = None
    if missing:
        error_msg = f"{labels.get('missing_file','FILE NON TROVATO')}: {len(missing)} (controlla i path)"

    running = True
    while running:
        # Input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

                elif e.key == pygame.K_UP:
                    idx = (idx - 1) % len(projects)

                elif e.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(projects)

                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    selected = projects[idx]
                    rel = selected.get("file", "")

                    # Stop musica menu (opzionale ma consigliato)
                    if audio_enabled:
                        pygame.mixer.music.stop()

                    # Chiudiamo pygame del menu per evitare conflitti se il gioco fa pygame.quit()
                    pygame.display.quit()
                    pygame.quit()

                    # Avvio gioco (bloccante)
                    try:
                        run_project(selected, root)
                        error_msg = None
                    except FileNotFoundError:
                        error_msg = f"{labels.get('missing_file','FILE NON TROVATO')}: {rel}"
                    except Exception as ex:
                        error_msg = f"{labels.get('launch_error','ERRORE AVVIO')}: {ex}"

                    # Riavvio pygame per tornare al menu
                    pygame.init()
                    pygame.mixer.init()
                    pygame.display.set_caption(safe_get(cfg, "meta.title", "PY-CADE 199X"))
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    clock = pygame.time.Clock()

                    font_big = pygame.font.Font(None, 64)
                    font_med = pygame.font.Font(None, 34)
                    font_small = pygame.font.Font(None, 24)

                    # Riparte musica menu
                    if audio_cfg.get("enabled", True):
                        wav_path = root / audio_file
                        if wav_path.is_file():
                            pygame.mixer.music.load(str(wav_path))
                            pygame.mixer.music.set_volume(audio_volume)
                            pygame.mixer.music.play(-1)
                            audio_enabled = True
                        else:
                            audio_enabled = False

        # Tip rotante
        now = time.time()
        if now >= tip_change_at:
            tip = random.choice(footer_tips) if footer_tips else ""
            tip_change_at = now + random.uniform(2.5, 4.5)
            banner = random.choice(banners) if banners else banner

        # Draw
        screen.fill(BG)
        draw_starfield(screen, stars)

        # Header
        header = screen_text.get("title_line", safe_get(cfg, "meta.title", "PY-CADE 199X"))
        sub = screen_text.get("subtitle_line", safe_get(cfg, "meta.subtitle", ""))

        center_text(screen, font_big, banner, 62, ACCENT2)
        center_text(screen, font_big, banner, 64, ACCENT)

        if header:
            blit_text(screen, font_small, header, 20, 10, DIM)
        if sub:
            max_sub_w = WIDTH - 40  # margini 20 a sinistra e 20 a destra
            for li, line in enumerate(wrap_text_px(font_small, sub, max_sub_w)[:2]):  # max 2 righe
                blit_text(screen, font_small, line, 20, 32 + li * 18, DIM)

        # Layout: lista a sinistra + pannello descrizione a destra
        list_x, list_y = 50, 120
        list_w, list_h = 520, HEIGHT - 220

        panel_x = list_x + list_w + 20
        panel_y = list_y
        panel_w = WIDTH - panel_x - 50
        panel_h = list_h

        pygame.draw.rect(screen, (25, 25, 40), pygame.Rect(list_x, list_y, list_w, list_h), border_radius=12)
        pygame.draw.rect(screen, (70, 70, 95), pygame.Rect(list_x, list_y, list_w, list_h), 2, border_radius=12)

        if show_desc_panel:
            pygame.draw.rect(screen, (22, 22, 34), pygame.Rect(panel_x, panel_y, panel_w, panel_h), border_radius=12)
            pygame.draw.rect(screen, (70, 70, 95), pygame.Rect(panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

        # Lista
        line_h = 34
        visible = (list_h - 40) // line_h
        top = max(0, idx - visible // 2)
        top = min(top, max(0, len(projects) - visible))

        for i in range(top, min(len(projects), top + visible)):
            y = list_y + 20 + (i - top) * line_h
            is_sel = (i == idx)

            disp = projects[i].get("display_name", projects[i].get("id", "SENZA NOME"))

            max_text_w = list_w - 24 - 60   # margini + spazio freccia
            prefix = "> " if is_sel else "  "
            lines = wrap_text_px(font_med, prefix + disp, max_text_w)

            if is_sel:
                # evidenziazione: altezza basata su quante righe mostri (+ eventuale rel path)
                extra = 22 if show_rel_path else 0
                sel_h = 26 * len(lines) + extra + 6
                pygame.draw.rect(
                    screen,
                    (45, 45, 70),
                    pygame.Rect(list_x + 12, y - 4, list_w - 24, sel_h),
                    border_radius=8,
                )

            # disegna righe titolo
            for li, line in enumerate(lines):
                blit_text(
                    screen,
                    font_med,
                    line,
                    list_x + 26,
                    y + li * 26,
                    ACCENT if is_sel else FG
                )

            # path relativo sotto il titolo (solo selezionato, come prima)
            if is_sel and show_rel_path:
                relp = projects[i].get("file", "")
                blit_text(screen, font_small, f"   ({relp})", list_x + 26, y + len(lines) * 26, DIM)

        # Pannello descrizione
        if show_desc_panel:
            sel = projects[idx]
            py = panel_y + 20

            # titolo selezionato
            blit_text(screen, font_med, sel.get("display_name", sel.get("id", "")), panel_x + 16, py, ACCENT2)
            py += 34

            tag = sel.get("short_tagline", "")
            if tag:
                max_tag_w = panel_w - 32  # padding sinistra+destra
                tag_lines = wrap_text_px(font_small, tag, max_tag_w)[:2]  # max 2 righe (cambia se vuoi)
                for line in tag_lines:
                    blit_text(screen, font_small, line, panel_x + 16, py, ACCENT)
                    py += 20
                py += 6

            # descrizione
            if "description" in desc_fields:
                desc_header = screen_text.get("description_header", "Descrizione")
                blit_text(screen, font_small, desc_header + ":", panel_x + 16, py, FG)
                py += 22

                desc = sel.get("description", "")
                desc = (desc[:max_desc_chars] + "…") if len(desc) > max_desc_chars else desc
                max_desc_w = panel_w - 32  # padding sinistra+destra
                for line in wrap_text_px(font_small, desc, max_desc_w):
                    blit_text(screen, font_small, line, panel_x + 16, py, DIM)
                    py += 20
                py += 10

            # comandi
            if "controls" in desc_fields:
                ctr_header = screen_text.get("controls_header", "Comandi")
                blit_text(screen, font_small, ctr_header + ":", panel_x + 16, py, FG)
                py += 22

                controls = sel.get("controls", [])
                if not controls:
                    blit_text(screen, font_small, "(non specificati)", panel_x + 16, py, DIM)
                    py += 20
                else:
                    max_ctrl_w = panel_w - 32
                    bullet = "• "
                    max_lines_per_cmd = 3   # limite per comando (cambia se vuoi)
                    max_cmds = 8            # come prima

                    for c in controls[:max_cmds]:
                        cmd_lines = wrap_text_px(font_small, c, max_ctrl_w - font_small.size(bullet)[0])
                        cmd_lines = cmd_lines[:max_lines_per_cmd]

                        for li, line in enumerate(cmd_lines):
                            prefix = bullet if li == 0 else "  "  # bullet solo sulla prima riga
                            blit_text(screen, font_small, prefix + line, panel_x + 16, py, DIM)
                            py += 20

                        py += 4  # spazio extra tra comandi

        # Footer
        pygame.draw.rect(screen, (20, 20, 30), pygame.Rect(0, HEIGHT - 70, WIDTH, 70))
        center_text(screen, font_small, tip, HEIGHT - 45, FG)
        center_text(screen, font_small, labels.get("press_enter", "Premi ENTER per avviare"), HEIGHT - 25, DIM)

        if error_msg:
            center_text(screen, font_small, error_msg, HEIGHT - 5, RED)

        draw_scanlines(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
