import pygame
import numpy as np
from config import Config

class DreamManager:
    def __init__(self, screen):
        self.screen = screen
        self.rows = 40
        self.cols = 40
        self.cell_size = Config.HEIGHT // self.rows
        self.offset_x = (Config.WIDTH - (self.cols * self.cell_size)) // 2
        self.offset_y = (Config.HEIGHT - (self.rows * self.cell_size)) // 2
        self.grid = np.zeros((self.rows, self.cols))
        self.history = []
        self.is_finished = False
        self.update_timer = 0
        self.UPDATE_INTERVAL = 300
        self.finish_timer = 0
        self.TRANSITION_DELAY = 7500
        self.alpha = 0
        self.fade_speed = 1

    def setup_dream(self, pattern_type=0):
        """指定された盤面で初期化"""
        self.pattern_type = pattern_type
        self.grid = np.zeros((self.rows, self.cols))
        if pattern_type == 0:
            grider = [[0, 1, 0], 
                      [0, 0, 1], 
                      [1, 1, 1]]
            self.grid[1:4, 1:4] = grider
            self.UPDATE_INTERVAL = 25
        elif pattern_type == 1:
            clock2 = [[0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], 
                      [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], 
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                      [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0], 
                      [1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0], 
                      [1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0], 
                      [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1], 
                      [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1], 
                      [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],  
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 
                      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]]
            self.grid[self.rows//2-6:self.rows//2+6, self.cols//2-6:self.cols//2+6] = clock2
            self.UPDATE_INTERVAL = 1000
        elif pattern_type == 2:
            pulsar = [[1, 0, 0, 0, 1], 
                      [1, 0, 0, 0, 1], 
                      [1, 0, 0, 0, 1]]
            self.grid[self.rows//2-1:self.rows//2+2, self.cols//2-2:self.cols//2+3] = pulsar
            self.UPDATE_INTERVAL = 90
        self.has_added_life = False
        self.history = []
        self.is_finished = False
        self.finish_timer = 0
        self.alpha = 0
    
    def add_life_at_center(self):
        """クリックされた画面座標から、対応する特定のセルを誕生させる"""
        if self.alpha < 255 or self.grid[self.rows//2, self.cols//2] == 1:
            return False
        if self.pattern_type == 0:
            if np.sum(self.grid) != 5:
                return False
            self.has_added_life = True
        else:
            if self.has_added_life:
                return False
            self.has_added_life = True
        self.grid[self.rows//2, self.cols//2] = 1
        return True

    def should_transition(self):
        """指定した時間が経過し、遷移すべき状態かを返す"""
        return self.is_finished and self.finish_timer >= self.TRANSITION_DELAY

    def update(self, dt):
        """世代交代と、グライダーの性質に合わせた接続ロジック（ひねりのあるトーラス）"""
        if self.is_finished:
            self.finish_timer += dt
        
        self.update_timer += dt
        if not self.is_finished and self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
        if self.is_finished:
                self.alpha = max(-220, self.alpha - self.fade_speed)
        if self.update_timer < self.UPDATE_INTERVAL:
            return
        self.update_timer %= self.UPDATE_INTERVAL


        new_grid = np.zeros((self.rows, self.cols))
        shift_x = 0

        for r in range(self.rows):
            for c in range(self.cols):
                total = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if nr < 0:
                            nr = self.rows - 1
                            nc = (nc - shift_x) % self.cols
                        elif nr >= self.rows:
                            nr = 0
                            nc = (nc + shift_x) % self.cols
                        else:
                            nc = nc % self.cols
                        
                        total += self.grid[nr, nc]

                if self.grid[r, c] == 1:
                    new_grid[r, c] = 1 if 2 <= total <= 3 else 0
                else:
                    new_grid[r, c] = 1 if total == 3 else 0

        if len(self.history) >= 2:
            if np.array_equal(new_grid, self.history[0]):
                self.is_finished = True

        self.history.append(self.grid.copy())
        if len(self.history) > 2:
            self.history.pop(0)
            
        self.grid = new_grid

    def draw(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r, c] == 1:
                    color = (160, 160, 255)
                    
                    rect_pos = (
                        self.offset_x + c * self.cell_size - self.cell_size // 2,
                        self.offset_y + r * self.cell_size - self.cell_size // 2,
                        self.cell_size - 1,
                        self.cell_size - 1
                    )
                    
                    if self.alpha >= 255:
                        pygame.draw.rect(self.screen, color, rect_pos)
                    else:
                        s = pygame.Surface((self.cell_size - 1, self.cell_size - 1))
                        s.set_alpha(self.alpha)
                        s.fill(color)
                        self.screen.blit(s, (rect_pos[0], rect_pos[1]))
        if self.alpha > 0:
            self._draw_guidelines()

    def _draw_guidelines(self):
        """中央の判定エリアを矩形と外側のL字で囲み、スナイパーの照準のように描画する"""
        center_r, center_c = self.rows // 2, self.cols // 2
        
        # セルの描画基準座標
        gap_left = self.offset_x + center_c * self.cell_size - self.cell_size // 2
        gap_top = self.offset_y + center_r * self.cell_size - self.cell_size // 2
        side = self.cell_size - 1
        
        # 右と下をさらに1ピクセル外側へ拡張
        gap_right = gap_left + side
        gap_bottom = gap_top + side

        line_color = (255, 100, 100)
        line_alpha = max(0, min(255, self.alpha // 2))
        full_color = (*line_color, line_alpha)
        
        guide_surf = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        
        # 十字線の中心（セルの中心）
        center_h = gap_left + (side // 2)
        center_v = gap_top + (side // 2)

        # 1. 十字線の描画
        pygame.draw.line(guide_surf, full_color, (center_h, 0), (center_h, gap_top), 1)
        pygame.draw.line(guide_surf, full_color, (center_h, gap_bottom), (center_h, Config.HEIGHT), 1)
        pygame.draw.line(guide_surf, full_color, (0, center_v), (gap_left, center_v), 1)
        pygame.draw.line(guide_surf, full_color, (gap_right, center_v), (Config.WIDTH, center_v), 1)

        # 2. 中央の四角形を描画
        rect_width = gap_right - gap_left + 1
        rect_height = gap_bottom - gap_top + 1
        target_rect = (gap_left, gap_top, rect_width, rect_height)
        pygame.draw.rect(guide_surf, full_color, target_rect, 1)

        # 3. さらに外側のL字描画
        # 中央の矩形からどれくらい離すか（マージン）と、L字の長さを設定
        margin = 4 
        l_length = self.cell_size // 3
        
        # 外側の境界座標
        o_left = gap_left - margin
        o_top = gap_top - margin
        o_right = gap_right + margin
        o_bottom = gap_bottom + margin

        # 左上
        pygame.draw.lines(guide_surf, full_color, False, [(o_left, o_top + l_length), (o_left, o_top), (o_left + l_length, o_top)], 1)
        # 右上
        pygame.draw.lines(guide_surf, full_color, False, [(o_right, o_top + l_length), (o_right, o_top), (o_right - l_length, o_top)], 1)
        # 左下
        pygame.draw.lines(guide_surf, full_color, False, [(o_left, o_bottom - l_length), (o_left, o_bottom), (o_left + l_length, o_bottom)], 1)
        # 右下
        pygame.draw.lines(guide_surf, full_color, False, [(o_right - l_length, o_bottom), (o_right, o_bottom), (o_right, o_bottom - l_length)], 1)

        self.screen.blit(guide_surf, (0, 0))