import pygame
import random
import os
pygame.init()
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 650
# Colori
BLACK = (10, 10, 15)
WHITE = (240, 240, 240)
GRAY = (40, 40, 45)
RED = (255, 70, 70)
GOLD = (255, 210, 0)
CYAN = (0, 230, 255)
PINK = (255, 105, 180) 
COLORS = [
    (0, 255, 255), (50, 100, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (160, 32, 240), (255, 0, 0),
    (255, 105, 180), (144, 238, 144) 
]

# Forme 
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[4, 5, 9, 10], [2, 6, 5, 9]],  # Z
    [[6, 7, 9, 10], [1, 5, 6, 10]], # S
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]], # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]], # L
    [[1, 4, 5, 6], [1, 5, 6, 9], [4, 5, 6, 9], [1, 4, 5, 9]], # T
    [[1, 2, 5, 6]], 
    [[2, 5, 8], [4, 5, 6]], # Diagonale 3 blocchi
    [[0, 5, 10], [2, 5, 8]] # Freccia obliqua / Grande Diagonale
]

def get_high_score():
    if not os.path.exists("highscore.txt"): return 0
    with open("highscore.txt", "r") as f:
        try: return int(f.read())
        except: return 0
def save_high_score(score): #Rcord
    if score > get_high_score():
        with open("highscore.txt", "w") as f: f.write(str(score))
class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.new_piece()
    def new_piece(self):
        self.shape_idx = self.next_shape_idx
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx % len(COLORS)]
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        if self.intersects(): self.game_over = True

    def get_coords(self, x_off=None, y_off=None, shape_idx=None, rot=None):
        x_off = self.x if x_off is None else x_off
        y_off = self.y if y_off is None else y_off
        rot = self.rotation if rot is None else rot
        s_idx = self.shape_idx if shape_idx is None else shape_idx
        positions = []
        shape_format = SHAPES[s_idx][rot % len(SHAPES[s_idx])]
        for i in shape_format:
            positions.append((x_off + i % 4, y_off + i // 4))
        return positions

    def intersects(self):
        for px, py in self.get_coords():
            if px < 0 or px >= GRID_WIDTH or py >= GRID_HEIGHT: return True
            if py >= 0 and self.grid[py][px]: return True
        return False

    def freeze(self):
        for px, py in self.get_coords():
            if py >= 0: self.grid[py][px] = self.color
        self.break_lines()
        self.new_piece()

    def break_lines(self):
        lines = 0
        for r in range(GRID_HEIGHT):
            if 0 not in self.grid[r]:
                lines += 1
                del self.grid[r]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        self.score += (lines ** 2) * 100

    def move_down(self):
        self.y += 1
        if self.intersects():
            self.y -= 1
            self.freeze()

def run_game():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris remastredddddd")
    clock = pygame.time.Clock()
    
    f_mid = pygame.font.SysFont('Consolas', 24, bold=True)
    f_small = pygame.font.SysFont('Consolas', 18)

    while True:
        diff_selected = False
        fall_limit = 20
        high_score = get_high_score()

        while not diff_selected:
            screen.fill(BLACK)
            screen.blit(f_mid.render("TETRIS REMASTARED :)", True, PINK), (SCREEN_WIDTH//2 - 90, 150))
            screen.blit(f_small.render(f"BEST SCORE: {high_score}", True, GOLD), (SCREEN_WIDTH//2 - 80, 200))
            screen.blit(f_small.render("[N] NORMALE", True, WHITE), (SCREEN_WIDTH//2 - 60, 280))
            screen.blit(f_small.render("[D] DIFFICILE", True, RED), (SCREEN_WIDTH//2 - 60, 320))
            pygame.display.flip()
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_n: fall_limit, diff_selected = 20, True
                    if e.key == pygame.K_d: fall_limit, diff_selected = 6, True
        game = Tetris()
        timer = 0
        playing = True

        while playing:
            screen.fill(BLACK)
            timer += 1
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return
                if e.type == pygame.KEYDOWN:
                    if not game.game_over:
                        if e.key == pygame.K_LEFT:
                            game.x -= 1
                            if game.intersects(): game.x += 1
                        if e.key == pygame.K_RIGHT:
                            game.x += 1
                            if game.intersects(): game.x -= 1
                        if e.key == pygame.K_UP:
                            old = game.rotation
                            game.rotation = (game.rotation + 1) % len(game.shape)
                            if game.intersects(): game.rotation = old
                        if e.key == pygame.K_DOWN: game.move_down()
                        if e.key == pygame.K_SPACE:
                            while not game.intersects(): game.y += 1
                            game.y -= 1
                            game.freeze()
                    else:
                        save_high_score(game.score)
                        playing = False

            if not game.game_over and timer > fall_limit:
                game.move_down()
                timer = 0

            # Disegno Griglia
            grid_x, grid_y = 30, 30
            for r in range(GRID_HEIGHT):
                for c in range(GRID_WIDTH):
                    rect = (grid_x + c*BLOCK_SIZE, grid_y + r*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(screen, GRAY, rect, 1)
                    if game.grid[r][c]:
                        pygame.draw.rect(screen, game.grid[r][c], (rect[0]+1, rect[1]+1, BLOCK_SIZE-2, BLOCK_SIZE-2))

            if not game.game_over:
                for px, py in game.get_coords():
                    if py >= 0:
                        pygame.draw.rect(screen, game.color, (grid_x + px*BLOCK_SIZE+1, grid_y + py*BLOCK_SIZE+1, BLOCK_SIZE-2, BLOCK_SIZE-2))
            ui_x = grid_x + (GRID_WIDTH * BLOCK_SIZE) + 30
            screen.blit(f_small.render("SCORE", True, WHITE), (ui_x, 50))
            screen.blit(f_mid.render(str(game.score), True, CYAN), (ui_x, 75))
            screen.blit(f_small.render("NEXT", True, WHITE), (ui_x, 150))

            next_coords = game.get_coords(x_off=0, y_off=0, shape_idx=game.next_shape_idx, rot=0)
            for nx, ny in next_coords:
                pygame.draw.rect(screen, COLORS[game.next_shape_idx % len(COLORS)], (ui_x + nx*20, 190 + ny*20, 18, 18))

            if game.game_over:
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0,0,0,180)); screen.blit(s, (0,0))
                screen.blit(f_mid.render("GAME OVER", True, RED), (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 20))
                screen.blit(f_small.render("Tasto per Menu", True, WHITE), (SCREEN_WIDTH//2 - 65, SCREEN_HEIGHT//2 + 20))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    run_game()
