import pygame
import random
from collections import defaultdict
from config import Config
from logic import find_all_non_redundant_specific_conditions
import numpy as np

# ---------------------------------------------------------------------------------
# --- ヘルパー関数 ---

def _get_unique_attributes(item_list):
    """
    アイテムリストから、各アイテムを一意に特定できる属性を返す。
    Stage 0/1/2 すべてで使用可能。
    """
    unique_attrs = {}
    
    # 属性の値と出現回数を抽出
    all_attrs = defaultdict(lambda: defaultdict(int)) # {key: {value: count}}
    for item in item_list:
        for k, v in item['status'].items():
            if k not in ['距離', '数']: 
                all_attrs[k][v] += 1

    # 各アイテムに対して、他と重複しない属性を一つ見つける
    for item in item_list:
        item_name = item['name']
        found_unique = False
        
        # 属性をランダムにシャッフルして、最初にユニークなものを見つける
        shuffled_keys = list(item['status'].keys())
        random.shuffle(shuffled_keys)
        
        for k in shuffled_keys:
            v = item['status'].get(k)
            if v and k not in ['距離', '数']:
                # その属性値を持つアイテムが一つだけなら、それは一意
                if all_attrs[k].get(v) == 1:
                    unique_attrs[item_name] = {'key': k, 'value': v}
                    found_unique = True
                    break

        if not found_unique:
             unique_attrs[item_name] = {'key': 'FAILED', 'value': 'FAILED'} 

    return unique_attrs

def _calculate_distance(pos1, pos2):
    return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2

# ---------------------------------------------------------------------------------

class BoardManager:
    def __init__(self, screen, item_images, language="JP"):
        self.screen = screen
        self.item_images = item_images
        self.language = language
        
        # 共通データ
        self.board_items = []
        self.off_board_items = [] 
        self.is_question_active = False
        self.active_question_data = None
        self.current_stage = None
        
        # Stage 2用データ
        self.selected_item = None 
        self.click_mode = 'SELECT'
        
        self.status_panel_rect = pygame.Rect(570, 120, 220, 180)
        self.sys_font_small = pygame.font.Font(Config.FONT_PATH, 18)
        self.sys_font = pygame.font.Font(Config.FONT_PATH, 32)

    # --- 共通ユーティリティ ---
    
    def _find_empty_cell(self, occupied_cells):
        while True:
            r = random.randint(0, Config.BOARD_ROWS - 1)
            c = random.randint(0, Config.BOARD_COLS - 1)
            if (r, c) not in occupied_cells:
                return r, c

    def _get_off_board_area_info(self):
        board_size = Config.BOARD_SIZE
        cell_size = Config.CELL_SIZE
        cols = Config.BOARD_COLS
        start_x = (Config.WIDTH - board_size) // 2
        start_y = (Config.HEIGHT - board_size) // 2 + board_size + 5
        width = cols * cell_size
        height = cell_size + 10
        rect = pygame.Rect(start_x, start_y, width, height)
        return rect, start_x, start_y, cell_size

    def reset_board_state(self):
        """ボード上のアイテムと質問の状態を全てリセットする"""
        self.board_items.clear()
        self.off_board_items.clear() 
        self.is_question_active = False
        self.active_question_data = None
        self.selected_item = None 
        self.click_mode = 'SELECT' 
        self.current_stage = None

    # -------------------------------------------------------------------------
    # --- 生成ロジック (Stageごとに分岐) ---
    # -------------------------------------------------------------------------

    def _generate_board_items(self, stage=None):
        """ステージに応じてボードアイテムを生成する"""
        self.board_items.clear()
        self.off_board_items.clear()
        self.game_session_seed = random.randint(0, 999999)
        occupied_cells = set()
        all_item_names = [name for name in Config.ITEM_DEFINITIONS.keys() if name not in ['hammer', 'memory']]
        
        if stage == 0:
            return self._generate_stage_0(all_item_names, occupied_cells)
        elif stage == 1:
            return self._generate_stage_1(all_item_names, occupied_cells)
        elif stage == 2:
            return self._generate_stage_2(all_item_names, occupied_cells)
        return None

    def _generate_stage_0(self, all_names, occupied_cells):
        if len(all_names) < 2: return None
        
        item_type1, item_type2 = random.sample(all_names, 2)
        c1, c2 = random.sample(range(1, 8), 2)
        
        # 配置
        temp_items = []
        for name, count in [(item_type1, c1), (item_type2, c2)]:
            for _ in range(count):
                r, c = self._find_empty_cell(occupied_cells)
                occupied_cells.add((r, c))
                status = Config.ITEM_DEFINITIONS[name].copy()
                status['距離'] = '-' if r < Config.BOARD_ROWS // 2 else '+'
                temp_items.append({'name': name, 'pos': (r, c), 'status': status, 'flipped': random.random() < 0.02})
        
        # 数ステータスの設定
        counts = {item_type1: c1, item_type2: c2}
        for item in temp_items:
            item['status']['数'] = str(counts[item['name']])
            self.board_items.append(item)
            
        return (item_type1, item_type2, c1, c2)

    def _generate_stage_1(self, all_names, occupied_cells):
        total_num = random.randint(3, 7)
        if len(all_names) < 3: return None
        
        # 3種類以上選定
        selected_names = random.sample(all_names, 3)
        items_to_gen = list(selected_names)
        remaining = total_num - 3
        if remaining > 0:
            items_to_gen.extend(random.choices(selected_names, k=remaining))
        random.shuffle(items_to_gen)
        
        # 配置
        temp_items = []
        item_counts = defaultdict(int)
        for name in items_to_gen:
            item_counts[name] += 1
            r, c = self._find_empty_cell(occupied_cells)
            occupied_cells.add((r, c))
            status = Config.ITEM_DEFINITIONS[name].copy()
            status['距離'] = '-' if r < Config.BOARD_ROWS // 2 else '+'
            temp_items.append({'name': name, 'pos': (r, c), 'status': status, 'flipped': random.random() < 0.02})
            
        # 数ステータス
        for item in temp_items:
            item['status']['数'] = str(item_counts[item['name']])
            self.board_items.append(item)
            
        return True

    def _generate_stage_2(self, all_names, occupied_cells):
        if len(all_names) < 6: return None
        item_names = random.sample(all_names, 6)
        
        # Board (3個)
        for name in item_names[:3]:
            r, c = self._find_empty_cell(occupied_cells)
            occupied_cells.add((r, c))
            status = Config.ITEM_DEFINITIONS[name].copy()
            status['距離'] = '-' if r < Config.BOARD_ROWS // 2 else '+'
            status['数'] = '1'
            self.board_items.append({'name': name, 'pos': (r, c), 'status': status, 'flipped': random.random() < 0.02})
            
        # Off-Board (3個)
        for i, name in enumerate(item_names[3:]):
            status = Config.ITEM_DEFINITIONS[name].copy()
            status['距離'] = '外'
            status['数'] = '1'
            self.off_board_items.append({'name': name, 'pos': (0, i), 'status': status, 'flipped': random.random() < 0.02})
        return True

    # -------------------------------------------------------------------------
    # --- 質問生成 (Setup) ---
    # -------------------------------------------------------------------------

    def setup_game_data(self, stage=None, correct_count=0):
        """ステージごとの質問生成を振り分け"""
        self.current_stage = stage
        self.selected_item = None
        self.click_mode = 'SELECT'
        force_destroy_memory = (correct_count == 9)
        
        while True:
            sentence = None
            
            if stage == 0:
                sentence = self._setup_stage_0()
            elif stage == 1:
                sentence = self._setup_stage_1()
            elif stage == 2:
                sentence = self._setup_stage_2(force_destroy_memory)
                
            if sentence:
                return sentence
        return None

    def _setup_stage_0(self):
        data = self._generate_board_items(stage=0)
        if not data: return None
        target = random.choice(self.board_items)
        other_item = next(i for i in self.board_items if i['name'] != target['name'])
        candidate_keys = []
        for k in ['色', '数']:
            t_val = target['status'].get(k)
            o_val = other_item['status'].get(k)
            if t_val is not None and t_val != o_val:
                candidate_keys.append(k)
        if not candidate_keys:
            return None
        chosen_key = random.choice(candidate_keys)
        val = target['status'][chosen_key]
        self.active_question_data = {
            'answer_name': target['name'],
            'sentence': [val],
            'question_type': 'SELECT'
        }
        self.is_question_active = True
        return [val]

    def _setup_stage_1(self):
        if not self._generate_board_items(stage=1): return None
        
        # 複合条件生成
        all_conditions = find_all_non_redundant_specific_conditions(self.board_items)
        valid_list = []
        for name, cond_list in all_conditions.items():
            for cond in cond_list:
                valid_list.append({'target_name': name, 'condition': cond})
        
        if not valid_list: return None
        
        chosen = random.choice(valid_list)
        target_name = chosen['target_name']
        condition = chosen['condition']
        
        # 文生成
        sentence = ["何", "⇔"]
        for k, v in sorted(condition.items()):
            if k in ["色", "数", "三態"]: sentence.append(v)
            else: sentence.extend([k, v])
            
        self.active_question_data = {
            'answer_name': target_name,
            'sentence': sentence,
            'question_type': 'SELECT'
        }
        self.is_question_active = True
        return sentence

    def _setup_stage_2(self, force_destroy_memory=False):
        if not self._generate_board_items(stage=2): return None
        
        items_on = self.board_items
        items_off = self.off_board_items
        if not items_on or not items_off: return None
        
        if force_destroy_memory:
            action = "壊す"
        else:
            action = random.choice(["近づく", "遠ざかる", "失う", "得る", "組む", "壊す"])
        sentence = []
        
        if action in ["近づく", "遠ざかる", "組む"]:
            if len(items_on) < 2: return None
            u_attrs = _get_unique_attributes(items_on)
            if any(a['key'] == 'FAILED' for a in u_attrs.values()): return None
            
            pairs = []
            for i1 in items_on:
                for i2 in items_on:
                    if i1 != i2:
                        dist = _calculate_distance(i1['pos'], i2['pos'])
                        if action == "近づく" and dist <= 1:
                            continue
                        if action == "遠ざかる" and i1['pos'] in [(0, 0), (0, Config.BOARD_COLS - 1), (Config.BOARD_ROWS - 1, 0), (Config.BOARD_ROWS - 1, Config.BOARD_COLS - 1)]:
                            continue
                        pairs.append((i1, i2))
            if not pairs: return None
            
            subj, obj = random.choice(pairs)
            
            s_attr = u_attrs[subj['name']]
            o_attr = u_attrs[obj['name']]
            
            for a in [s_attr]:
                k, v = a['key'], a['value']
                if k in ["色", "数", "三態"]: sentence.append(v)
                else: sentence.extend([k, v])
            
            sentence.append(action)
            sentence.append("→")

            for a in [o_attr]:
                k, v = a['key'], a['value']
                if k in ["色", "数", "三態"]: sentence.append(v)
                else: sentence.extend([k, v])

            self.active_question_data = {
                'subject_name': subj['name'],
                'object_name': obj['name'],
                'required_action': action,
                'initial_distance': _calculate_distance(subj['pos'], obj['pos']),
                'sentence': sentence,
                'question_type': 'MOVE'
            }
            
        elif action == "壊す":
            if force_destroy_memory:
                memory_idx = random.randint(0, len(self.board_items) - 1)
                target_item = self.board_items[memory_idx]
                target_item['name'] = 'memory'
                target_item['status'] = Config.ITEM_DEFINITIONS['memory'].copy()
                target_item['status']['距離'] = '-' if target_item['pos'][0] < Config.BOARD_ROWS // 2 else '+'
                target_item['status']['数'] = '1'
                obj = target_item
                u_attrs_on = _get_unique_attributes(items_on)
                o_attr = u_attrs_on['memory']
                if o_attr['key'] == 'FAILED': return None
            else:
                obj = random.choice(self.board_items)
                u_attrs_on = _get_unique_attributes(items_on)
                if u_attrs_on[obj['name']]['key'] == 'FAILED': return None
                o_attr = u_attrs_on[obj['name']]
            
            hammer_idx = random.randint(0, len(self.off_board_items) - 1)
            self.off_board_items[hammer_idx]['name'] = 'hammer'
            self.off_board_items[hammer_idx]['status'] = Config.ITEM_DEFINITIONS['hammer'].copy()
            self.off_board_items[hammer_idx]['status']['距離'] = '外'
            self.off_board_items[hammer_idx]['status']['数'] = '1'
            
            u_attrs_off = _get_unique_attributes(self.off_board_items)
            s_attr = u_attrs_off['hammer']
            if s_attr['key'] == 'FAILED': return None
            
            k_s, v_s = s_attr['key'], s_attr['value']
            if k_s in ["色", "数", "三態"]: sentence.append(v_s)
            else: sentence.extend([k_s, v_s])
            
            sentence.append("壊す")
            sentence.append("→")
            
            k_o, v_o = o_attr['key'], o_attr['value']
            if k_o in ["色", "数", "三態"]: sentence.append(v_o)
            else: sentence.extend([k_o, v_o])
            
            self.active_question_data = {
                'subject_name': 'hammer',
                'object_name': obj['name'],
                'required_action': '壊す',
                'sentence': sentence,
                'question_type': 'MOVE'
            }

        elif action == "失う":
            subj = random.choice(items_off)
            u_attrs = _get_unique_attributes(items_off)
            if u_attrs[subj['name']]['key'] == 'FAILED': return None
            attr = u_attrs[subj['name']]
            sentence.extend(["神為", "距離", "+", action])
            k, v = attr['key'], attr['value']
            if k in ["色", "数", "三態"]: sentence.append(v)
            else: sentence.extend([k, v])
            self.active_question_data = {'subject_name': subj['name'], 'object_name': None, 'required_action': action, 'sentence': sentence, 'question_type': 'LOSE'}
            
        elif action == "得る":
            obj = random.choice(items_on)
            u_attrs = _get_unique_attributes(items_on)
            if u_attrs[obj['name']]['key'] == 'FAILED': return None
            attr = u_attrs[obj['name']]
            sentence.extend(["神為", "距離", "+", action])
            k, v = attr['key'], attr['value']
            if k in ["色", "数", "三態"]: sentence.append(v)
            else: sentence.extend([k, v])
            self.active_question_data = {'subject_name': obj['name'], 'object_name': None, 'required_action': action, 'sentence': sentence, 'question_type': 'GAIN'}

        self.is_question_active = True
        return sentence

    # -------------------------------------------------------------------------
    # --- クリック処理 (Handle Click) ---
    # -------------------------------------------------------------------------

    def handle_item_click(self, mouse_pos):
        """マウス入力をステージごとに振り分け"""
        if not self.is_question_active:
            return ["神為", "距離", "-", "時", "+", "始", "→", "我為", "善悪", "+"], None

        board_size = Config.BOARD_SIZE
        cell_size = Config.CELL_SIZE
        start_x = (Config.WIDTH - board_size) // 3
        start_y = (Config.HEIGHT - board_size) // 2

        c = (mouse_pos[0] - start_x) // cell_size
        r = (mouse_pos[1] - start_y) // cell_size
        click_pos = (r, c)
        
        clicked_on_board = next((item for item in self.board_items if item['pos'] == click_pos), None)
        
        if self.current_stage in [0, 1]:
            return self._handle_click_simple(clicked_on_board)
            
        elif self.current_stage == 2:
            rect, off_x, off_y, _ = self._get_off_board_area_info()
            clicked_off_board = None
            is_off_area = False
            off_pos = None

            if rect.collidepoint(mouse_pos):
                is_off_area = True
                c_off = (mouse_pos[0] - off_x) // cell_size
                off_pos = (0, c_off)
                clicked_off_board = next((item for item in self.off_board_items if item['pos'] == off_pos), None)

            if self.click_mode == 'SELECT':
                if clicked_on_board:
                    return self._handle_stage_2_logic(clicked_on_board, None, 'BOARD', click_pos)
                elif clicked_off_board:
                    return self._handle_stage_2_logic(None, clicked_off_board, 'OFF_BOARD', None)
            
            elif self.click_mode == 'MOVE':
                if (clicked_on_board and clicked_on_board == self.selected_item) or \
                   (clicked_off_board and clicked_off_board == self.selected_item):
                    self.selected_item = None
                    self.click_mode = 'SELECT'
                    return "", None
                
                if 0 <= r < Config.BOARD_ROWS and 0 <= c < Config.BOARD_COLS:
                    return self._handle_stage_2_logic(clicked_on_board, None, 'BOARD', click_pos)
                elif is_off_area:
                    return self._handle_stage_2_logic(None, clicked_off_board, 'OFF_BOARD', off_pos)

        return "", None

    def _handle_click_simple(self, clicked_item):
        """Stage 0/1 用の判定"""
        if clicked_item:
            ans_name = self.active_question_data['answer_name']
            is_correct = (clicked_item['name'] == ans_name)
            
            self.is_question_active = False
            self.active_question_data = None
            
            if is_correct:
                return ["神為", "距離", "+", "得る", "→", "我為"], True
            else:
                return ["神為", "距離", "+", "失う", "→", "我為"], False
        return "", None

    def _handle_stage_2_logic(self, clicked_on, clicked_off, location_type, click_pos):
        q_type = self.active_question_data.get('question_type')
        
        if self.click_mode == 'SELECT':
            target = clicked_on if location_type == 'BOARD' else clicked_off
            if target:
                self.selected_item = target
                
                if location_type == 'BOARD' and target in self.board_items:
                    self.board_items.remove(target)
                    self.board_items.append(target)
                
                self.click_mode = 'MOVE'
            return "", None
            
        elif self.click_mode == 'MOVE':
            sel_item = self.selected_item
            sel_name = sel_item['name']
            from_board = (sel_item in self.board_items)
            from_off = (sel_item in self.off_board_items)
            is_correct = False
            
            if location_type == 'BOARD':
                new_pos = click_pos
                s_name = self.active_question_data.get('subject_name')
                o_name = self.active_question_data.get('object_name')
                action = self.active_question_data.get('required_action')

                if from_board:
                    sel_item['pos'] = new_pos
                    self.board_items.remove(sel_item)
                    self.board_items.append(sel_item)
                elif from_off:
                    self.off_board_items.remove(sel_item)
                    sel_item['pos'] = new_pos
                    sel_item['status']['距離'] = '-' if new_pos[0] < Config.BOARD_ROWS // 2 else '+'
                    sel_item['status']['数'] = '1'
                    self.board_items.append(sel_item)
                    
                obj_item = next((i for i in self.board_items if i['name'] == o_name and i != sel_item), None)
                
                if obj_item and sel_name == s_name:
                    curr_dist = _calculate_distance(new_pos, obj_item['pos'])
                    
                    if action == "組む" or action == "壊す":
                        if curr_dist == 0: is_correct = True
                    elif action == "近づく":
                        if curr_dist < self.active_question_data['initial_distance']: is_correct = True
                    elif action == "遠ざかる":
                        if curr_dist > self.active_question_data['initial_distance']: is_correct = True
                
                if q_type == 'LOSE' and from_off and sel_name == s_name:
                    is_correct = True

            elif location_type == 'OFF_BOARD':
                new_pos_off = click_pos
                
                if from_board:
                    self.board_items.remove(sel_item)
                    sel_item['pos'] = new_pos_off
                    sel_item['status']['距離'] = '外'
                    sel_item['status']['数'] = '1'
                    self.off_board_items.append(sel_item)
                    
                    if q_type == 'GAIN' and sel_name == self.active_question_data['subject_name']:
                        is_correct = True

                elif from_off:
                    sel_item['pos'] = new_pos_off

            self.selected_item = None
            self.click_mode = 'SELECT'
            self.is_question_active = False
            return (["神為", "距離", "+", "得る", "→", "我為"], True) if is_correct else (["神為", "距離", "+", "失う", "→", "我為"], False)

    # -------------------------------------------------------------------------
    # --- 描画 (Draw) ---
    # -------------------------------------------------------------------------

    def draw_board_grid(self, mouse_pos=(0, 0)):
        board_size = Config.BOARD_SIZE
        cell_size = Config.CELL_SIZE
        start_x = (Config.WIDTH - board_size) // 3
        start_y = (Config.HEIGHT - board_size) // 2

        t = pygame.time.get_ticks() * 0.01
        for item in self.board_items:
            self._blit_individual_item(item, start_x, start_y, cell_size, False, mouse_pos, t)

        if self.current_stage == 2:
            rect, off_x, off_y, _ = self._get_off_board_area_info()
            pygame.draw.rect(self.screen, (20, 20, 20), rect, border_radius=10)
            pygame.draw.rect(self.screen, (80, 80, 80), rect, width=2, border_radius=10)
            
            for item in self.off_board_items:
                self._blit_individual_item(item, off_x, off_y, cell_size, True, mouse_pos, t)
        
        self._draw_status_panel(mouse_pos)

    def _draw_items(self, item_list, start_x, start_y, cell_size, is_off_board=False, mouse_pos=None):
        t = pygame.time.get_ticks() * 0.01
        selected_item_to_draw_last = None
        
        for item in item_list:
            if self.selected_item and item == self.selected_item:
                selected_item_to_draw_last = (item, is_off_board)
                continue
            self._blit_individual_item(item, start_x, start_y, cell_size, is_off_board, mouse_pos, t)
        if selected_item_to_draw_last:
            item, is_off = selected_item_to_draw_last
            self._blit_individual_item(item, start_x, start_y, cell_size, is_off, mouse_pos, t)
            
    def _blit_individual_item(self, item, start_x, start_y, cell_size, is_off_board, mouse_pos, t):
        if is_off_board:
            col = item['pos'][1]
            x = start_x + col * cell_size + 2
            y = start_y + 5 
        else:
            r, c = item['pos']
            x = start_x + c * cell_size + 2
            y = start_y + r * cell_size + 2
        
        img = self.item_images.get(item['name'])
        if img:
            if item.get('flipped', False):
                img = pygame.transform.flip(img, True, False)

            item_rect = pygame.Rect(x, y, img.get_width(), img.get_height())
            is_hover = mouse_pos and item_rect.collidepoint(mouse_pos)
            is_selected = self.selected_item and item == self.selected_item

            offset_x, offset_y = 0, 0
            if is_selected or is_hover:
                amp = 2.0 if is_selected else 1.0
                offset_x = np.sin(t) * amp
                offset_y = np.cos(t * 1.3) * amp

            draw_x, draw_y = x + offset_x, y + offset_y

            border_color = (255, 215, 0) if is_selected else ((255, 255, 255) if is_hover else None)
            if border_color:
                mask = pygame.mask.from_surface(img)
                outline_surf = mask.to_surface(setcolor=border_color, unsetcolor=(0, 0, 0, 0))
                outline_surf.set_colorkey((0, 0, 0))
                thickness = 2
                for dx, dy in [(-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness)]:
                    self.screen.blit(outline_surf, (draw_x + dx, draw_y + dy))
            
            self.screen.blit(img, (draw_x, draw_y))

    def _draw_status_panel(self, mouse_pos):
        panel_rect = self.status_panel_rect
        
        border_color = (100, 80, 40)
        bg_color = (30, 30, 35)

        pygame.draw.rect(self.screen, border_color, panel_rect, border_radius=10)
        inner_rect = panel_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, bg_color, inner_rect, border_radius=8)

        if inner_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (255, 255, 255), inner_rect, width=1, border_radius=8)

        if self.is_question_active:
            lamp_color = (50, 200, 255) if self.click_mode == 'MOVE' else (255, 200, 50)
            if self.current_stage == 2:
                if self.click_mode == 'SELECT':
                    status_text = '選択' if self.language == "JP" else 'SELECT'
                elif self.click_mode == 'MOVE':
                    status_text = '移動' if self.language == "JP" else 'MOVE'
            else:
                status_text = '思考中' if self.language == "JP" else 'THINKING'
        else:
            lamp_color = (150, 50, 50)
            status_text = "開始" if self.language == "JP" else 'READY'

        lamp_pos = (inner_rect.left + 25, inner_rect.top + 25)
        pygame.draw.circle(self.screen, lamp_color, lamp_pos, 6)
        
        mode_surf = self.sys_font_small.render(status_text, True, (180, 180, 180))
        self.screen.blit(mode_surf, (inner_rect.left + 40, inner_rect.top + 17))

        pygame.draw.line(self.screen, (60, 60, 70), (inner_rect.left + 20, inner_rect.top + 50), (inner_rect.right - 20, inner_rect.top + 50), 1)

        text_color = (200, 200, 200)
        update_surf = self.sys_font.render("更新" if self.language == "JP" else 'UPDATE', True, text_color)
        update_rect = update_surf.get_rect(center=(inner_rect.centerx, inner_rect.top + 110))
            
        self.screen.blit(update_surf, update_rect)