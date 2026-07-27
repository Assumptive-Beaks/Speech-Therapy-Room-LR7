import pygame
import os
from config import Config
import copy
import numpy as np

class SceneManager:
    def __init__(self, screen, language="JP"):
        self.screen = screen
        self.language = language
        self.current_scene_id = "title_screen" 
        self.bg_img = None
        
        # フェードアウト・トランジション用変数
        self.fade_surface = pygame.Surface((Config.WIDTH, Config.HEIGHT))
        self.fade_surface.fill((0, 0, 0))
        self.fade_alpha = 0
        self.tv_progress = 0.0
        self.transition_state = "none" 
        self.next_scene_id = None
        
        scenes_jp = {
            "title_screen": { 
                "img_path": os.path.join(Config.ASSETS_DIR, "title.png"), 
                "hitboxes": [] 
            },
            "classroom": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x0_y4.5_z1.6_h300_p0.png"),
                "hitboxes": [
                {
                    "rect": (250, 450, 450, 150), 
                    "action": "question", 
                    "content": "EAT_CHOICE",
                    "choices": [
                        {"text": "ここで食べる", "target": "classroom", "content": "EAT_ACTION"}, 
                        {"text": "食べない", "content": "EAT_CANCEL"}
                    ]
                },
                    {"rect": (0, 420, 250, 60), "action": "move", "target": "board_view", "content": "ONCE_BOARD_INTRO"},
                    {"rect": (700, 0, 100, 600), "action": "move", "target": "dining"},
                    {"rect": (370, 70, 300, 380), "action": "move", "target": "factory"}
                ]
            },
            "factory": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x2_y3_z1.45_h240_p0.png"), 
                "hitboxes": [
                    {"rect": (160, 110, 220, 270), "action": "move", "target": "train", "content": "DAY_TRAIN_TO_ROOM"},
                    {"rect": (700, 0, 100, 600), "action": "move", "target": "classroom", "content": "DAY_CLASSROOM_TO_ROOM"}
                ]
            },
            "dining": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x1.7_y7.3_z1.45_h0_p-10.png"), 
                "hitboxes": [
                {
                    "rect": (60, 340, 640, 160), 
                    "action": "question", 
                    "content": "EAT_CHOICE",
                    "choices": [
                        {"text": "ここで食べる", "target": "dining", "content": "EAT_ACTION"}, 
                        {"text": "食べない", "content": "EAT_CANCEL"}
                    ]
                },
                    {"rect": (0, 0, 290, 320), "action": "move", "target": "classroom", "content": "DAY_CLASSROOM_TO_ROOM"},
                    {"rect": (700, 0, 100, 600), "action": "move", "target": "train", "content": "DAY_TRAIN_TO_ROOM"},
                ]
            },
            "train": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x5_y4_z1.6_h150_p0.png"), 
                "hitboxes": [
                    {"rect": (90, 40, 150, 410), "action": "move", "target": "dining"},
                    {"rect": (0, 500, 620, 100), "action": "move", "target": "atelier", "content": "DAY_ATELIER_TO_TRAIN"},
                {
                    "rect": (150, 360, 370, 230), 
                    "action": "question", 
                    "content": "EAT_CHOICE",
                    "choices": [
                        {"text": "ここで食べる", "target": "train", "content": "EAT_ACTION"}, 
                        {"text": "食べない", "content": "EAT_CANCEL"}
                    ]
                },
                    {"rect": (620, 0, 180, 600), "action": "move", "target": "factory"},
                    {"rect": (0, 190, 70, 190), "action": "move", "target": "in_jail"}
                ]
            },
            "pond": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x2_y0_z1.6_h270_p0.png"), 
                "hitboxes": [
                {
                    "rect": (0, 380, 280, 220), 
                    "action": "question", 
                    "content": "EAT_CHOICE",
                    "choices": [
                        {"text": "ここで食べる", "target": "pond", "content": "EAT_ACTION"}, 
                        {"text": "食べない", "content": "EAT_CANCEL"}
                    ]
                },
                    {
                        "rect": (280, 350, 380, 250), 
                        "action": "question", 
                        "content": "BATH_CHOICE",
                        "choices": [
                            {"text": "水に入る", "target": "pond", "content": "BATH_ACTION"}, 
                            {"text": "排泄する", "target": "pond", "content": "TOILET_BADACTION"}, 
                            {"text": "何もしない", "content": "TOILET_CANCEL"}
                        ]
                    },
                    {"rect": (670, 200, 50, 170), "action": "move", "target": "atelier"} 
                ]
            },
            "atelier": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x8_y4_z1.6_h60_p0.png"), 
                "hitboxes": [
                    {
                        "rect": (360, 280, 60, 60), 
                        "action": "question", 
                        "content": "CHARCOAL_CHOICE",
                        "choices": [
                            {"text": "持っていく", "content": "CHARCOAL_ACTION"}, 
                            {"text": "持っていかない", "content": "CHARCOAL_CANCEL"}
                        ]
                    },
                        {
                            "rect": (685, 270, 30, 100), 
                            "action": "question", 
                            "content": "CHARCOAL_CHOICE",
                            "choices": [
                                {"text": "持っていく", "content": "CHARCOAL_ACTION"}, 
                                {"text": "持っていかない", "content": "CHARCOAL_CANCEL"}
                            ]
                        },
                    {"rect": (0, 130, 120, 290), "action": "move", "target": "train", "content": "DAY_TRAIN_TO_ROOM"},
                    {"rect": (0, 500, 800, 100), "action": "move", "target": "hospice", "content": "DAY_HOSPICE_TO_ATELIER"},
                    {"rect": (580, 270, 70, 90), "action": "draw"},
                    {"rect": (620, 160, 200, 220), "action": "move", "target": "pond", "content": "ONCE_POND_TO_ATELIER"},
                ]
            },
            "drawing_canvas": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x8_y4_z1.6_h60_p0.png"),
                "hitboxes": []
            },
            "in_jail": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x8.5_y8.5_z1.6_h50_p-25.png"), 
                "hitboxes": [
                {
                    "rect": (480, 360, 320, 240), 
                    "action": "question", 
                    "content": "EAT_CHOICE",
                    "choices": [
                        {"text": "ここで食べる", "target": "in_jail", "content": "EAT_ACTION"}, 
                        {"text": "食べない", "content": "EAT_CANCEL"}
                    ]
                },
                    {
                        "rect": (0, 110, 150, 300), 
                        "action": "question", 
                        "content": "TOILET_CHOICE",
                        "choices": [
                            {"text": "チャコールを入れる", "target": "in_jail", "content": "TOILET_REFRESH"}, 
                            {"text": "排泄する", "target": "in_jail", "content": "TOILET_ACTION"}, 
                            {"text": "何もしない", "content": "TOILET_CANCEL"}
                        ]
                    },
                    {"rect": (0, 410, 100, 190), "action": "move", "target": "train"},
                    {"rect": (100, 500, 380, 100), "action": "move", "target": "train"}, 
                ]
            },
            "out_jail": {
                "img_paths": {
                    "default": os.path.join(Config.ASSETS_DIR, "tile_x8_y7_z1.6_h180_p0.png"),
                    "day3": os.path.join(Config.ASSETS_DIR, "tile_x8_y7_z1.6_h180_p0_3.png"),
                    "day4": os.path.join(Config.ASSETS_DIR, "tile_x8_y7_z1.6_h180_p0_4.png"),
                    "day5": os.path.join(Config.ASSETS_DIR, "tile_x8_y7_z1.6_h180_p0_5.png")
                },
                "hitboxes": [
                    {"rect": (0, 500, 800, 100), "action": "move", "target": "shop"} 
                ]
            },
            "shop": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x7_y7_z1.6_h270_p0.png"), 
                "hitboxes": [
                    {
                        "rect": (150, 200, 500, 260), 
                        "action": "question", 
                        "content": "SHOP_CHOICE",
                        "choices": [
                            {"text": "商品の食べ物を持ち出す", "content": "SHOP_ACTION"}, 
                            {"text": "持ち出さない", "content": "SHOP_CANCEL"}
                        ]
                    },
                    {"rect": (670, 0, 130, 600), "action": "move", "target": "out_jail"},
                    {"rect": (0, 0, 110, 600), "action": "move", "target": "hospice"},
                ]
            },
            "hospice": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x11_y5_z1.6_h90_p0.png"), 
                "hitboxes": [
                    {
                        "rect": (70, 370, 630, 130), 
                        "action": "question", 
                        "content": "SHEETS_CHOICE",
                        "choices": [
                            {"text": "体を拭く", "target": "hospice", "content": "SHEETS_ACTION"}, 
                            {"text": "拭かない", "content": "SHEETS_CANCEL"}
                        ]
                    },
                    {"rect": (570, 130, 230, 230), "action": "move", "target": "atelier"},
                    {"rect": (0, 130, 230, 230), "action": "move", "target": "shop"},
                    {"rect": (0, 500, 800, 100), "action": "move", "target": "bed"} 
                ]
            },
            "bed": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x11.25_y4.9_z1.2_h180_p0.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 450), "action": "move", "target": "hospice"},
                    {"rect": (0, 450, 800, 150), "action": "sleep", "content": None} 
                ]
            },
            "end_dream": {
                "img_path": os.path.join(Config.ASSETS_DIR, "dream.png"),
                "hitboxes": [
                    {"rect": (391, 291, 16, 16), "action": "life", "content": None} 
                ]
            },
            "black": {
                "img_path": os.path.join(Config.ASSETS_DIR, "black.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 600), "action": "move", "target": "bed", "content": "DAY_BED_INTRO"}
                ]
            },
            "board_view": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x0.525_y3.834_z2.2_h0_p-80.png"),
                "hitboxes": [
                    {"rect": (570, 120, 220, 180), "action": "test", "content": None}
                ]
            },
            "train_seat": {
                "img_path": os.path.join(Config.ASSETS_DIR, "tile_x6_y8_z1.45_h80_p0.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 500), "action": "move", "target": "dining", "content": "ONCE_TRAIN_INTRO"},
                ]
            },
            "end_clear": {
                "img_path": os.path.join(Config.ASSETS_DIR, "good_end.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 600), "action": "move", "target": "title_screen"},
                ]
            },
            "end_over": {
                "img_path": os.path.join(Config.ASSETS_DIR, "bad_end.png"), 
                "hitboxes": [
                ]
            },
            "end_over_": {
                "img_path": os.path.join(Config.ASSETS_DIR, "bad_end_.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 600), "action": "move", "target": "title_screen"},
                ]
            },
            "end_true": {
                "img_path": os.path.join(Config.ASSETS_DIR, "true_end.png"), 
                "hitboxes": [
                    {
                        "rect": (0, 0, 800, 600), 
                        "action": "question", 
                        "content": "",
                        "choices": [
                            {"text": "宣言する", "content": "TRUE_ACTION", "action": "move", "target": "end_true_"}, 
                            {"text": "訴える", "content": "TRUE_ACTION", "action": "move", "target": "end_true_"}, 
                            {"text": "叫ぶ", "content": "TRUE_ACTION", "action": "move", "target": "end_true_"}
                        ]
                    },
                ]
            },
            "end_true_": {
                "img_path": os.path.join(Config.ASSETS_DIR, "true_end.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 600), "action": "move", "target": "title_screen"},
                ]
            },
            "end_post": {
                "img_path": os.path.join(Config.ASSETS_DIR, "true_end.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 600), "action": "move", "target": "end_post_"},
                ]
            },
            "end_post_": {
                "img_path": os.path.join(Config.ASSETS_DIR, "post_end.png"), 
                "hitboxes": [
                    {"rect": (0, 0, 800, 600), "action": "move", "target": "title_screen"},
                ]
            },
        }
        scenes_en = copy.deepcopy(scenes_jp)
        choice_map = {
            "ここで食べる": "Eat here",
            "食べない": "Don't eat",
            "チャコールを入れる": "Add charcoal",
            "水に入る": "Get in the water",
            "排泄する": "Relieve myself",
            "何もしない": "Do nothing",
            "持っていく": "Take it",
            "持っていかない": "Don't take it",
            "商品の食べ物を持ち出す": "Take the food product",
            "持ち出さない": "Don't take it",
            "体を拭く": "Wipe body",
            "拭かない": "Don't wipe",
            "宣言する": "Declare",
            "訴える": "Plead",
            "叫ぶ": "Shout",
        }
        for scene_id, data in scenes_en.items():
            if "hitboxes" in data:
                for hitbox in data["hitboxes"]:
                    if "choices" in hitbox:
                        for choice in hitbox["choices"]:
                            orig_text = choice["text"]
                            if orig_text in choice_map:
                                choice["text"] = choice_map[orig_text]
        
        self.scenes = scenes_jp if self.language == "JP" else scenes_en
        self.vignette_surf = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        self._prepare_vignette()
        self._load_scene(self.current_scene_id)

    def _prepare_vignette(self):
        self.vignette_surf.fill((0, 0, 0, 180))
        steps = 40
        for i in range(steps):
            alpha = int(180 * (1.0 - (i / steps)))
            w = Config.WIDTH * (1.5 - (i / steps)) 
            h = Config.HEIGHT * (1.5 - (i / steps))
            
            rect = pygame.Rect(0, 0, w, h)
            rect.center = (Config.WIDTH // 2, Config.HEIGHT // 2)
            pygame.draw.ellipse(self.vignette_surf, (0, 0, 0, alpha), rect)

    def _load_scene(self, scene_id, current_day=0):
        if scene_id not in self.scenes:
            return
        
        self.current_scene_id = scene_id
        scene_data = self.scenes[scene_id]
        if scene_data:
            path = scene_data.get("img_path")
            
            if "img_paths" in scene_data:
                paths = scene_data["img_paths"]
                if scene_id == "out_jail":
                    if current_day == 3:
                        path = paths.get("day3")
                    elif current_day == 4:
                        path = paths.get("day4")
                    elif current_day >= 5:
                        path = paths.get("day5")
                    else:
                        path = paths.get("default")
                else:
                    path = paths.get("default")

            if path:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.bg_img = pygame.transform.smoothscale(img, (Config.WIDTH, Config.HEIGHT))
                    
                    if scene_id in ["atelier", "end_over_"]:
                        overlay_path = os.path.join(Config.SAVE_DIR, "image_test.png")
                        if os.path.exists(overlay_path):
                            overlay_surf = pygame.image.load(overlay_path).convert_alpha()
                            w, h = overlay_surf.get_size()
                            if scene_id == "atelier":
                                dest_points = [
                                    (589, 269), # 左上
                                    (579, 360), # 左下
                                    (640, 355), # 右下
                                    (648, 268)  # 右上
                                ]
                            elif scene_id == "end_over_":
                                dest_points = [
                                    (528, 261), # 左上
                                    (555, 480), # 左下
                                    (672, 463), # 右下
                                    (645, 259)  # 右上
                                ]
                            coeffs = self._find_coeffs(
                                dest_points,
                                [(0, 0), (0, h), (w, h), (w, 0)]
                            )
                            mult_surf = self._perspective_warp_to_bg(
                                overlay_surf, coeffs, Config.WIDTH, Config.HEIGHT
                            )
                            self.bg_img.blit(mult_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                except Exception:
                    s = pygame.Surface((Config.WIDTH, Config.HEIGHT))
                    color = (40, 40, 50)
                    s.fill(color)
                    self.bg_img = s
        
    def set_scene(self, scene_id):
        self.transition_state = "none"
        self._load_scene(scene_id)
        
    def start_transition(self, target_scene_id, current_day=0):
        if self.transition_state == "none":
            self.current_day = current_day
            self.next_scene_id = target_scene_id
            self.transition_state = "out" 
    
    def start_tv_transition(self, target_scene_id, current_day=0):
        if self.transition_state == "none":
            self.current_day = current_day
            self.next_scene_id = target_scene_id
            self.transition_state = "tv_out"
            self.tv_progress = 0.0
    
    def update_transition(self, fade_speed=10):
        if self.transition_state == "out":
            self.fade_alpha += fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self._load_scene(self.next_scene_id, self.current_day)
                self.transition_state = "in" 
        elif self.transition_state == "in":
            self.fade_alpha -= fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.transition_state = "none"
        elif self.transition_state == "tv_out":
            self.tv_progress += 0.15
            if self.tv_progress >= 1.0:
                self.tv_progress = 1.0
                self._load_scene(self.next_scene_id, self.current_day)
                self.fade_alpha = 255
                self.transition_state = "in"
                self.tv_progress = 0.0
        elif self.transition_state == "tv_in":
            self.tv_progress -= 0.05
            if self.tv_progress <= 0:
                self.tv_progress = 0.0
                self.transition_state = "none"

    def draw_background(self):
        if self.bg_img:
            ticks = pygame.time.get_ticks()
            
            if "end" in self.current_scene_id:
                period = 4000
                wave = 2 * abs((ticks / period) - np.floor((ticks / period) + 0.5))
                mosaic_scale = 0.7 + (wave * 0.3)
                temp_w = max(1, int(Config.WIDTH * mosaic_scale))
                temp_h = max(1, int(Config.HEIGHT * mosaic_scale))
                small_img = pygame.transform.scale(self.bg_img, (temp_w, temp_h))
                mosaic_img = pygame.transform.scale(small_img, (Config.WIDTH, Config.HEIGHT))
                self.screen.fill((0, 0, 0)) 
                self.screen.blit(mosaic_img, (0, 0))
            elif self.current_scene_id == "title_screen": 
                self.screen.fill((0, 0, 0))
                shift = 2 
                self.screen.blit(self.bg_img, (-shift, 0), special_flags=pygame.BLEND_RGB_ADD)
                self.screen.blit(self.bg_img, (shift, 0), special_flags=pygame.BLEND_RGB_ADD)
                noise_size = (Config.WIDTH // 4, Config.HEIGHT // 3)
                noise_array = np.random.randint(100, 200, (noise_size[1], noise_size[0]), dtype=np.uint8)
                noise_surf = pygame.surfarray.make_surface(np.stack([noise_array]*3, axis=-1))
                noise_surf = pygame.transform.scale(noise_surf, (Config.WIDTH, Config.HEIGHT))
                noise_surf.set_alpha(50) 
                self.screen.blit(noise_surf, (0, 0))
            else:
                amplitude = (np.sin(ticks / 30000) + 1) / 2  
                color_val = 160 + (amplitude * 60) 
                self.screen.fill((color_val, color_val, color_val))
                self.screen.blit(self.bg_img, (0, 0))
                self.screen.blit(self.vignette_surf, (0, 0))
        else:
            self.screen.fill(Config.BG_COLOR)

    def draw_fade(self):
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
        if self.tv_progress > 0:
            self._draw_tv_logic()

    def _draw_tv_logic(self):
        p = self.tv_progress
        self.screen.fill((0, 0, 0))
        
        if p < 1.0:
            h_scale = max(0.005, 1.0 - (p / 0.7)) if p < 0.7 else 0.005
            w_scale = 1.0 if p < 0.7 else max(0.0, 1.0 - ((p - 0.7) / 0.3))
            
            if w_scale > 0 and self.bg_img:
                target_w = int(Config.WIDTH * w_scale)
                target_h = int(Config.HEIGHT * h_scale)
                
                scaled_bg = pygame.transform.scale(self.bg_img, (target_w, target_h))
                
                if p > 0.8:
                    scaled_bg.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                
                pos_x = (Config.WIDTH - target_w) // 2
                pos_y = (Config.HEIGHT - target_h) // 2
                self.screen.blit(scaled_bg, (pos_x, pos_y))

    def get_hitboxes(self):
        return self.scenes.get(self.current_scene_id, {}).get("hitboxes", [])

    def _find_coeffs(self, pa, pb):
        """
        pa: 元の4点 [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
        pb: 変形後の4点 [(x, y), ...]
        """
        matrix = []
        for p1, p2 in zip(pa, pb):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

        A = np.matrix(matrix, dtype=float)
        B = np.array(pb).reshape(8)

        res = np.linalg.solve(A, B)
        return np.array(res).reshape(8)

    def _perspective_warp_to_bg(self, overlay_surf, coeffs, out_w, out_h):
        """
        PILのImage.transform(size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)相当の処理を
        numpyのみで行う(Pillow非依存化のため。pygbag/ブラウザ環境ではPillowが使えない)。

        coeffs = [a, b, c, d, e, f, g, h] は出力座標(x, y)を
        overlay_surf内の座標に写像する8係数で、_find_coeffs()の戻り値をそのまま使う。
            src_x = (a*x + b*y + c) / (g*x + h*y + 1)
            src_y = (d*x + e*y + f) / (g*x + h*y + 1)

        戻り値は、overlay_surfの写像先だけが元の絵柄で、それ以外は白(255,255,255)で
        塗られた(out_w, out_h)のpygame.Surface。呼び出し側でBLEND_RGB_MULTを使って
        背景に合成すると、写像先の部分だけが上書きされる。
        """
        a, b, c, d, e, f, g, h = coeffs

        overlay_w, overlay_h = overlay_surf.get_size()
        # pygameのsurfarrayは (幅, 高さ, ...) の順の配列を返す
        overlay_rgb = pygame.surfarray.array3d(overlay_surf).astype(np.float64)
        overlay_alpha = pygame.surfarray.array_alpha(overlay_surf).astype(np.float64)

        xs, ys = np.meshgrid(
            np.arange(out_w, dtype=np.float64),
            np.arange(out_h, dtype=np.float64),
            indexing="ij"
        )

        denom = g * xs + h * ys + 1.0
        denom = np.where(denom == 0, 1e-9, denom)
        src_x = (a * xs + b * ys + c) / denom
        src_y = (d * xs + e * ys + f) / denom

        valid = (src_x >= 0) & (src_x <= overlay_w - 1) & (src_y >= 0) & (src_y <= overlay_h - 1)

        src_x_c = np.clip(src_x, 0, overlay_w - 1)
        src_y_c = np.clip(src_y, 0, overlay_h - 1)

        x0 = np.floor(src_x_c).astype(np.int32)
        y0 = np.floor(src_y_c).astype(np.int32)
        x1 = np.clip(x0 + 1, 0, overlay_w - 1)
        y1 = np.clip(y0 + 1, 0, overlay_h - 1)

        wx = (src_x_c - x0)
        wy = (src_y_c - y0)

        def _bilinear(arr):
            v00 = arr[x0, y0]
            v10 = arr[x1, y0]
            v01 = arr[x0, y1]
            v11 = arr[x1, y1]
            if arr.ndim == 3:
                wx_ = wx[..., None]
                wy_ = wy[..., None]
            else:
                wx_ = wx
                wy_ = wy
            top = v00 * (1 - wx_) + v10 * wx_
            bottom = v01 * (1 - wx_) + v11 * wx_
            return top * (1 - wy_) + bottom * wy_

        sampled_rgb = _bilinear(overlay_rgb)
        sampled_alpha = _bilinear(overlay_alpha)
        sampled_alpha = np.where(valid, sampled_alpha, 0.0)

        alpha_norm = (sampled_alpha / 255.0)[..., None]
        mult_rgb = 255.0 * (1 - alpha_norm) + sampled_rgb * alpha_norm
        mult_rgb = np.clip(mult_rgb, 0, 255).astype(np.uint8)

        return pygame.surfarray.make_surface(mult_rgb)

    def draw_debug_hitboxes(self, sys_font):
        if not Config.DEBUG_MODE:
            return
        
        current_scene = self.scenes.get(self.current_scene_id)
        if current_scene:
            for hitbox in current_scene.get("hitboxes", []):
                rect = pygame.Rect(hitbox["rect"])
                action = hitbox.get("action")
                
                color = (255, 0, 0) 
                if action == "text": color = (0, 0, 255) 
                elif action == "play": color = (0, 255, 0) 
                elif action == "stop": color = (255, 255, 0) 
                
                pygame.draw.rect(self.screen, color, rect, 2)
                
                if action:
                    lbl = sys_font.render(action, True, color)
                    self.screen.blit(lbl, (rect.x, rect.y))