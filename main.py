import numpy as np
import asyncio
import pygame
import pickle
import os
import random
import hashlib
# from steamworks import STEAMWORKS

# 分割したモジュールをインポート
from config import Config
from dsp import SoundGenerator
from logic import WordManager
from scene_manager import SceneManager 
from board_manager import BoardManager 
from ui_manager import UIManager 
from event_manager import EventManager
from dream_manager import DreamManager
from make_dictionary import generate_initial_dictionary

# -----------------------------
# ゲーム本体クラス (コントローラー)
# -----------------------------
class LackGame:
    def __init__(self):
        pygame.init()
        
        # --- ウインドウサイズ可変対応の初期化 ---
        self.logical_w = Config.WIDTH
        self.logical_h = Config.HEIGHT
        icon = pygame.image.load(Config.ICON_PATH)
        pygame.display.set_icon(icon)
        
        # 実際の表示ウインドウ (リサイズ可能)
        self.display_window = pygame.display.set_mode(
            (self.logical_w, self.logical_h), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption("LR7")
        self.bgm_active = False
        self.bgm_loaded = False
        
        # ゲーム内描画用キャンバス (固定解像度)
        self.screen = pygame.Surface((self.logical_w, self.logical_h))
        
        # スケーリング用変数の初期化
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self._update_scale()
        
        # -------------------------------------
        # 1. ドット座標の初期化
        # -------------------------------------
        self.dots, self.dot_base_x = self._init_dots_coords()
        
        # -------------------------------------
        # 2. セーブデータ管理の初期化
        # -------------------------------------
        self.save_file = Config.DIC_PATH
        self.scene_manager = SceneManager(self.screen)
        self.dream_manager = DreamManager(self.screen)
        self.dream_manager.setup_dream()
        self._load_save_data()
        self.scene_manager = SceneManager(self.screen, language=self.language)
        
        # -------------------------------------
        # 3. サウンドとロジックの初期化
        # -------------------------------------
        self.sound_gen = SoundGenerator(dots=[d.center for d in self.dots])
        self.word_manager = WordManager(self.dots, self.difficulty, self.language)
        self.sys_font = pygame.font.Font(None, 32) # デバッグ・テスト用フォント (pygame同梱フォント)
        
        # -------------------------------------
        # 4. マネージャーの初期化
        # -------------------------------------
        self.ui_manager = UIManager(self.screen, self.dots, self.master_volume, self.difficulty, initial_fullscreen=self.saved_is_fullscreen, language=self.language)
        self.board_manager = BoardManager(self.screen, self.ui_manager.item_images, language=self.language)
        self.event_manager = EventManager(self, self.ui_manager, self.word_manager, language=self.language)
        
        # -------------------------------------
        # 5. ゲーム状態の初期化
        # -------------------------------------
        self.current_scene_id = self.scene_manager.current_scene_id 
        self._check_canvas_tampering()

        # ドット操作関連の変数 (Dot UI)
        self.selected = []          # 選択されたドットのインデックス
        self.path = []              # 描画のための座標パス
        self.used_lines = set()     # 使用済みの線のセット (パターン判定用)
        self.current_pos = None     # マウスの現在位置
        self.dragging = False       # ドラッグ中フラグ
        self.last_dot_index = None  # 最後に触れたドットのインデックス
        self.special_reentry_used = False # 特別再入場(0番ドット)の使用フラグ
        self.draw_special_circle = False  # 特別再入場時の描画フラグ
        self.next_voice = True      # ランダムパターンを自動再生するトリガー
        self.disable_random_highlight = False # ランダムパターンのハイライトを無効化するフラグ

        # 音声再生同期のための変数 (フレームベースで制御)
        self.playing_pattern_list = [] # 再生待ちのパターンデータリスト
        self.current_play_index = -1   # 現在再生中のパターンのインデックス
        self.time_to_next_pattern = 0  # 次のパターンを再生するまでの残り時間 (ミリ秒)
        self.PATTERN_DELAY_MS = 250    # パターン間の最小遅延時間
        self.ecg_timer = 0
        self.ecg_continuous_sound = None

        # タイトル画面の初期認証
        self.waiting_for_start_pattern = True
        self.sound_gen.set_master_volume(self.master_volume)
        
        # "始"と"終"のラインセットを事前に計算し保持 (タイトル画面認証用)
        start_pattern_data = self.word_manager.generate_random_pattern(["始"])
        self.required_start_lines = start_pattern_data[0]["used_lines"] if start_pattern_data else set()
        
        end_pattern_data = self.word_manager.generate_random_pattern(["終"])
        self.required_end_lines = end_pattern_data[0]["used_lines"] if end_pattern_data else set()
        
        self.signature_data = self.word_manager.generate_random_pattern(["⇔", "死"])
        
        # タイトル画面の初期パターンを生成
        self._set_initial_random_pattern(["始"])
        self.esc_pressed_once = False
        
        # Steamworks Initialization (Commented out)
        # try:
        #     self.steamworks = STEAMWORKS()
        #     self.steamworks.initialize()
        #     print("Steam Initialized!")
        # except Exception as e:
        #     print(f"Steam could not be initialized: {e}")
        #     self.steamworks = None

    def _init_dots_coords(self):
        """UI_Managerで使うドットの座標を計算する"""
        grid_x, grid_y = Config.WIDTH // 12, Config.HEIGHT // 6 
        dots = []
        base_x = grid_x 
        for row in range(3):
            for col in range(2):
                if col == 0 and row == 1: continue
                x = base_x + col * Config.SPACING_X 
                y = grid_y + row * Config.SPACING_Y
                dots.append(pygame.Rect(x - Config.RADIUS, y - Config.RADIUS, Config.RADIUS * 2, Config.RADIUS * 2))
        return dots, base_x

    def _update_scale(self):
        """ウインドウサイズ変更時に倍率とオフセットを再計算する"""
        window_w, window_h = self.display_window.get_size()
        
        scale_w = window_w / self.logical_w
        scale_h = window_h / self.logical_h
        self.scale = min(scale_w, scale_h)
        
        new_w = int(self.logical_w * self.scale)
        new_h = int(self.logical_h * self.scale)
        self.offset_x = (window_w - new_w) // 2
        self.offset_y = (window_h - new_h) // 2

    def _convert_mouse_pos(self, pos):
        """実際のウインドウ上のマウス座標を、ゲーム内論理座標に変換する"""
        x, y = pos
        logic_x = (x - self.offset_x) / self.scale
        logic_y = (y - self.offset_y) / self.scale
        return (int(logic_x), int(logic_y))

    def _generate_data_hash(self, data_dict):
        """セーブデータ辞書（ハッシュを除く）から検証用ハッシュを作成"""
        temp_dict = {k: v for k, v in data_dict.items() if k != "saved_save_hash"}
        data_string = str(sorted(temp_dict.items())).encode("utf-8")
        return hashlib.sha256(data_string).hexdigest()

    def _check_canvas_tampering(self):
        """キャンバスファイルの更新日時を確認し、外部編集を検知する"""
        if not os.path.exists(Config.IMAGE_TEST_PATH):
            return

        current_canvas_hash = self.ui_manager.get_canvas_hash()
        if self.is_data_tampered:
            self.initial_scene = "title_screen"
            self.saved_canvas_hash = self.ui_manager.overwrite_with_warning()
            self._save_data()
        if not self.saved_canvas_hash:
            self.saved_canvas_hash = current_canvas_hash
            self._save_data()
            return
        if current_canvas_hash != self.saved_canvas_hash:
            self.saved_canvas_hash = self.ui_manager.overwrite_with_warning()
            self._save_data()

    def _load_save_data(self):
        path = Config.DIC_PATH
        if os.path.exists(path):
            try:
                with open(self.save_file, 'rb') as f:
                    all_data = pickle.load(f)
            
                payload = {k: v for k, v in all_data.items() if k != "saved_save_hash"}
                saved_hash = all_data.get("saved_save_hash", "")
            
                if saved_hash == "" or saved_hash == self._generate_data_hash(payload):
                    self.is_data_tampered = False
                else:
                    self.is_data_tampered = True

                save_part = all_data.get("save", {})
                self.saved_window_size = save_part.get("window_size", (Config.WIDTH, Config.HEIGHT))
                self.saved_is_fullscreen = save_part.get("is_fullscreen", False)
                self.triggered_events = set(save_part.get("triggered_events", []))
                self.current_day = save_part.get("current_day", 0)
                self.stage = save_part.get("stage", 0)
                self.hunger = save_part.get("hunger", 0)
                self.dignity = save_part.get("dignity", 20)
                self.dirty = save_part.get("dirty", 2)
                self.held_item = save_part.get("held_item", None)
                self.board_available_today = save_part.get("board_available_today", True)
                self.water_available_today = save_part.get("water_available_today", True)
                self.sheet_available_today = save_part.get("sheet_available_today", True)
                self.toilet_used = save_part.get("toilet_used", False)
                self.toilet_refreshed = save_part.get("toilet_refreshed", False)
            
                if self.current_day == 0:
                    self.initial_scene = "end_dream"
                else:
                    self.initial_scene = save_part.get("current_scene_id", "title_screen")
                self.difficulty = save_part.get("difficulty", Config.DEFAULT_DIFFICULTY)
                self.master_volume = save_part.get("master_volume", Config.DEFAULT_VOLUME)
                self.correct_streak = save_part.get("correct_streak", 0)
                self.incorrect_streak = save_part.get("incorrect_streak", 0)
                self.fail_streak = save_part.get("fail_streak", 0)
                self.num_difficulties = save_part.get("num_difficulties", 1)
                self.image_edited = save_part.get("image_edited", False)
                self.cleared = save_part.get("cleared", False)
                self.language = save_part.get("language", "JP")
                self.saved_canvas_hash = save_part.get("saved_canvas_hash", "")
                self.original_dic = all_data.get("original", {"始": ['形容詞', '時', ['ay', []]]})
                self.master_dic = all_data.get("master", {"始": ['形容詞', '時', ['ay', []]]})
                self.master_en_dic = all_data.get("master_en", {"始": ['形容詞', '時', ['ay', []]]})
                self.user_dic = all_data.get("user", {})
                
                if self.saved_is_fullscreen:
                    self.display_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    self.display_window = pygame.display.set_mode(self.saved_window_size, pygame.RESIZABLE)
                self.ui_manager = UIManager(self.screen, self.dots, self.master_volume, self.difficulty, initial_fullscreen=self.saved_is_fullscreen, language=self.language)
                self._update_scale()
            except Exception:
                self.is_data_tampered = True
        else:
            dictionary = generate_initial_dictionary()
            with open(self.save_file, 'wb') as f:
                pickle.dump(dictionary, f)
            self._load_save_data()
                
    def _save_data(self):
        if self.difficulty in ["Bachelor", "Master"]:
            self.user_dic = self.word_manager.user_dictionary
        elif self.language == "JP":
            self.master_dic = self.word_manager.user_dictionary
        else:
            self.master_en_dic = self.word_manager.user_dictionary
        
        win_w, win_h = self.display_window.get_size()
        payload = {
            'original': self.original_dic,
            'master': self.master_dic,
            'master_en': self.master_en_dic,
            'user': self.user_dic,
            'save': {
                "window_size": (win_w, win_h),
                "is_fullscreen": self.ui_manager.is_fullscreen,
                "current_scene_id": self.scene_manager.current_scene_id,
                "triggered_events": list(self.triggered_events),
                "current_day": self.current_day,
                "stage": self.stage,
                "hunger": self.hunger,
                "dignity": self.dignity,
                "dirty": self.dirty,
                "held_item": self.held_item,
                "board_available_today": self.board_available_today,
                "water_available_today": self.water_available_today,
                "sheet_available_today": self.sheet_available_today,
                "toilet_used": self.toilet_used,
                "toilet_refreshed": self.toilet_refreshed,
                "difficulty": self.difficulty,
                "master_volume": self.master_volume,
                "correct_streak": self.correct_streak,
                "incorrect_streak": self.incorrect_streak,
                "fail_streak": self.fail_streak,
                "num_difficulties": self.num_difficulties,
                "image_edited": self.image_edited,
                "cleared": self.cleared,
                "language": self.language,
                "saved_canvas_hash": self.saved_canvas_hash,
            }
        }
        all_data = {
            **payload,
            "saved_save_hash": self._generate_data_hash(payload)
        }
        try:
            with open(self.save_file, 'wb') as f:
                pickle.dump(all_data, f)
        except Exception:
            pass

    def reset_game_state(self, full_reset=False):
        """ゲームの状態を初期化する。full_reset=Trueの場合はシステム設定も初期化"""
        self.initial_scene = "end_dream"
        self.triggered_events = set()
        self.current_day = 0
        self.stage = 0
        self.hunger = 0
        self.dignity = 20
        self.dirty = 2
        self.held_item = None
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.fail_streak = 0
        self.board_available_today = True
        self.water_available_today = True
        self.sheet_available_today = True
        self.toilet_used = False
        self.toilet_refreshed = False
        self.cleared = False
        self.ui_manager.dots_visible = True 
        self.ui_manager.patterns_visible = False 
        self.ui_manager.dic_ui_visible = False
        self.ui_manager.image_ui_visible = False
        
        if hasattr(self, 'dream_manager'):
            self.dream_manager.setup_dream()
            self.ecg_timer = 0
            
        if full_reset:
            self.difficulty = Config.DEFAULT_DIFFICULTY
            self.master_volume = Config.DEFAULT_VOLUME
            self.num_difficulties = 1
            if hasattr(self, 'ui_manager'):
                self.ui_manager.init_canvas_surface()
            self.image_edited = False
            generate_initial_dictionary()
        elif self.difficulty in ["Bachelor", "Master"]:
            if hasattr(self, 'word_manager'):
                for key in self.word_manager.user_dictionary:
                    self.word_manager.user_dictionary[key][1] = False
                self.word_manager.save_user_dic()
        
        self._save_data()
        self.signature_data = self.word_manager.generate_random_pattern(["⇔", "死"])
        self._set_initial_random_pattern(["始"])
        self.waiting_for_start_pattern = True
        
    def _trigger_once_event(self, event_id):
        if event_id in self.triggered_events:
            return False
        self.event_manager.trigger_event(event_id)
        self.triggered_events.add(event_id)
        self._save_data()
        return True

    def _set_initial_random_pattern(self, sentence):
        """指定された単語群からパターンを生成し、UIに設定する"""
        random_patterns = self.word_manager.generate_random_pattern(sentence)
        if self.difficulty == "Master":
            dic_updated = False
            for pdata in random_patterns:
                key_tuple = tuple(sorted(list(set(pdata['used_lines']))))
                if key_tuple not in self.word_manager.user_dictionary:
                    self.word_manager.user_dictionary[key_tuple] = ["?", False]
                    dic_updated = True
            
            if dic_updated and self.difficulty in ["Bachelor", "Master"]:
                self.word_manager.save_user_dic()
        self.ui_manager.set_random_patterns(random_patterns)
        self.next_voice = True
        return random_patterns

    def clear_pattern(self):
        """現在の描画中のドットパターンをクリアする"""
        self.selected.clear()
        self.path.clear()
        self.used_lines.clear()
        self.current_pos = None
        self.last_dot_index = None
        self.special_reentry_used = False
        self.draw_special_circle = False

    def play_patterns(self, pattern_list):
        """パターンリストを再生キューに設定する (フレームごとに制御)"""
        self.playing_pattern_list = pattern_list 
        self.current_play_index = -1            
        self.time_to_next_pattern = 0           
        self.disable_random_highlight = False
            
    def _handle_scene_action(self, hitbox):
        action = hitbox.get("action")
        target = hitbox.get("target")
        content = hitbox.get("content")
        
        if action == "move":
            if target == "factory":
                self.dignity -= 1
            if self.current_day < 5 and target == "in_jail":
                return
            if content == "DAY_BED_INTRO":
                if self.current_day <= 5:
                    target = "train_seat"
                    self.ui_manager.patterns_visible = True 
                else: 
                    self.ui_manager.patterns_visible = False 
                self.ui_manager.dots_visible = False
                self.ui_manager.dic_ui_visible = False
                self.ui_manager.image_ui_visible = False 
            if "end" in self.current_scene_id:
                self.cleared = True
                self._save_data()
                self.hunger = 1.8
                self.ui_manager.dots_visible = False 
                self.ui_manager.patterns_visible = False 
                self.ui_manager.dic_ui_visible = False
                self.ui_manager.image_ui_visible = False 
                
                # if self.current_scene_id == "end_over":
                #     self.unlock_achievement("ACH_CLEAR_END_3")
                # if self.current_scene_id == "end_clear":
                #     self.unlock_achievement("ACH_CLEAR_END_2")
                # if self.current_scene_id == "end_true":
                #     self.unlock_achievement("ACH_CLEAR_END_1")
                
            if self.current_scene_id == "end_true_":
                self.scene_manager.start_tv_transition(target, current_day=self.current_day)
                self.event_manager.trigger_event("TITLE")
                if self.num_difficulties < 3:
                    if self.num_difficulties == 1:
                        self.event_manager.trigger_event("RELEASE_MASTER")
                    self.event_manager.trigger_event("RELEASE_DOCTOR")
                    self.num_difficulties = 3
            else:
                self.scene_manager.start_transition(target, current_day=self.current_day)
            
            if self.current_day == 0:
                self.current_day += 1
                self.ui_manager.set_patterns([])
                self.ui_manager.dots_visible = False 
                self.ui_manager.patterns_visible = True 
                self.ui_manager.dic_ui_visible = False
                self.ui_manager.image_ui_visible = False 
            
            if content:
                event_names = content.split(',')
                for event_name in event_names:
                    event_name = event_name.strip()
                    
                    # 1. 常時イベントの処理 (イベントIDが 'ONCE_' で始まるもの)
                    if event_name.startswith("ONCE_"):
                        event_id = event_name.replace("ONCE_", "")
                        self._trigger_once_event(event_id)

                    # 2. 日次イベントの処理 (イベントIDが 'DAY_' で始まるもの)
                    elif event_name.startswith("DAY_"):
                        event_day_id = f"{event_name}_{self.current_day}"
                        self._trigger_once_event(event_day_id)
                    else:
                        self.event_manager.trigger_event(event_name)
                        
        elif action == "text":
            self.event_manager.trigger_event(content)
            
        elif action == "question":
            current_choices = hitbox.get("choices", [])
            if content == "TOILET_CHOICE":
                if self.held_item != "charcoal":
                    current_choices = [choice for choice in current_choices if choice.get("content") != "TOILET_REFRESH"]
                    if not self.water_available_today:
                        return
                elif not self.water_available_today:
                    current_choices = [choice for choice in current_choices if choice.get("content") != "TOILET_ACTION"]
                if self.toilet_used:
                    if self.toilet_refreshed:
                        content = "TOILET_RECHOICE_REFRESH"
                    else:
                        content = "TOILET_RECHOICE"
                elif self.toilet_refreshed:
                    content = "TOILET_RECHOICE_REFRESH"
            
            if content == "BATH_CHOICE":
                if self.dirty <= 0:
                    current_choices = [choice for choice in current_choices if choice.get("content") != "BATH_ACTION"]
                    if not self.water_available_today:
                        return
                elif not self.water_available_today:
                    current_choices = [choice for choice in current_choices if choice.get("content") != "TOILET_BADACTION"]
            
            if content == "SHEETS_CHOICE":
                if not self.sheet_available_today or self.dirty <= 0:
                    return
            if content == "EAT_CHOICE" and self.held_item not in ["meal", "food"]:
                self.event_manager.trigger_event("NO_MEAL")
                return
            if content == "SHOP_CHOICE" and self.held_item is not None:
                self.event_manager.trigger_event("NONAVAILABLE")
                return
            if content == "CHARCOAL_CHOICE" and self.held_item is not None:
                self.event_manager.trigger_event("NONAVAILABLE")
                return
            if self.current_scene_id == "end_true":
                self.hunger = -4
            
            self.event_manager.trigger_event(content)
            self.event_manager.open_question(current_choices)
            
        elif action == "stop":
            self.scene_manager.start_transition(target)
            
        elif action == "test":
            if not self.board_available_today:
                self.event_manager.trigger_event("BOARD_ALREADY_USED")
                return
            if self.board_manager.is_question_active:
                self.incorrect_streak += 1
                if self.incorrect_streak >= 4:
                    self.board_available_today = False 
                    self.event_manager.trigger_event("BOARD_PASSED")
                    self.scene_manager.start_transition("classroom")
                    self.held_item = "meal"
                    self._save_data()
                    return
                else:
                    self.event_manager.trigger_event("QUESTION_SKIP_PENALTY")
            self.board_manager.reset_board_state()
            self.ui_manager.set_patterns([])
            sentence = ""
            while sentence == "" or sentence is None:
                sentence = self.board_manager.setup_game_data(stage=self.stage, correct_count=self.correct_streak)
            self._set_initial_random_pattern(sentence)
            
        elif action == "sleep":
            self._save_data()
            self.ui_manager.set_patterns([])
            self._set_initial_random_pattern("")
            if self.board_available_today:
                self.event_manager.trigger_event("REST")
                return
            elif self.water_available_today:
                self.event_manager.trigger_event("TOILET")
                return
            else:
                if self.current_day <= 5:
                    if self.hunger >= 0:
                        self.event_manager.trigger_event("HUNGER")
                        return
                    self.hunger = max(self.hunger + 2, 0)
                    self.dignity -= self.dirty
                    self.dirty += self.current_day * 2
                else:
                    if self.hunger >= 1:
                        self.event_manager.trigger_event("HUNGER")
                        return
                    self.hunger = max(self.hunger + 1, 0)
                    self.dignity -= self.dirty
                    self.dirty += self.current_day
                
                if self.toilet_used and not self.toilet_refreshed:
                    self.dirty += 8
                if self.incorrect_streak >= 4:
                    self.fail_streak += 1
                
                if self.correct_streak >= 10:
                    self.stage += 1
                    self.fail_streak = 0
                elif self.stage == 2 and self.correct_streak == 9:
                    self.dignity *= 2
                if self.fail_streak >= 3:
                    self.stage = 0
                
                if self.stage == 3:
                    self.current_scene_id = "end_clear"
                    self.event_manager.trigger_event("GAME_CLEAR")
                    if self.num_difficulties < 3:
                        if self.num_difficulties == 1:
                            self.event_manager.trigger_event("RELEASE_MASTER")
                        self.event_manager.trigger_event("RELEASE_DOCTOR")
                        self.num_difficulties = 3
                    self.hunger = 1.5
                    self.dignity = 20
                    self.dirty = 2
                    self.ui_manager.dots_visible = False 
                    self.ui_manager.patterns_visible = True 
                    self.ui_manager.dic_ui_visible = False
                    self.ui_manager.image_ui_visible = False 
                elif self.dignity <= 0 or self.current_day >= 14:
                    self.current_scene_id = "end_over"
                    self.event_manager.trigger_event("GAME_OVER_1")
                    self.hunger = 1.5
                    self.dignity = 20
                    self.dirty = 2
                    self.ui_manager.dots_visible = True 
                    self.ui_manager.patterns_visible = True 
                    self.ui_manager.dic_ui_visible = False
                    self.ui_manager.image_ui_visible = False 
                elif self.dignity > 110:
                    self.current_scene_id = "end_true"
                    self.event_manager.trigger_event("GAME_CLEAR_TRUE")
                    self.hunger = 1.5
                    self.dignity = 20
                    self.dirty = 2
                    self.ui_manager.dots_visible = False 
                    self.ui_manager.patterns_visible = False 
                    self.ui_manager.dic_ui_visible = False
                    self.ui_manager.image_ui_visible = False 
                else:
                    if self.correct_streak >= 10:
                        self.current_scene_id = "end_dream"
                    else:
                        self.current_scene_id = "black"
                    self.ui_manager.dots_visible = False 
                    self.ui_manager.patterns_visible = False 
                    self.ui_manager.dic_ui_visible = False
                    self.ui_manager.image_ui_visible = False 
                
                self.correct_streak = 0
                self.incorrect_streak = 0
                self.current_day += 1
                self.board_available_today = True
                self.water_available_today = True
                self.sheet_available_today = True
                self.held_item = None
                self.board_manager.reset_board_state()
                self.scene_manager.start_transition(self.current_scene_id)
                if self.current_scene_id == "end_dream":
                    self.dream_manager.setup_dream(self.stage)
                    
        elif action == "draw":
            if self.held_item == "charcoal":
                self.scene_manager.set_scene("drawing_canvas")
            else:
                self.event_manager.trigger_event("draw")
        elif action == "life":
            if self.dream_manager.add_life_at_center():
                self._create_tick_sound().play()

    def _create_tick_sound(self):
        sample_rate = 44100
        duration = random.uniform(0.04, 0.06)
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        f1 = 2500
        f2 = 3500
        metal_wave = (np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f2 * t))
        noise = np.random.uniform(-1, 1, len(t))
        mix_ratio = random.uniform(0.6, 0.8)
        wave = metal_wave * (1 - mix_ratio) + noise * mix_ratio
        decay = random.randint(120, 200)
        envelope = np.exp(-decay * t)
        wave = (wave * envelope * 32767).astype(np.int16)
        stereo_wave = np.repeat(wave[:, np.newaxis], 2, axis=1)
        sound = pygame.sndarray.make_sound(stereo_wave)
        sound.set_volume(self.master_volume * random.uniform(0.1, 0.3))
    
        return sound

    def toggle_screen_mode(self):
        """フルスクリーンとウィンドウモードを切り替える"""
        if self.ui_manager.is_fullscreen:
            self.display_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display_window = pygame.display.set_mode(
                (self.logical_w, self.logical_h), 
                pygame.RESIZABLE
            )
        self._update_scale()

    # def unlock_achievement(self, name):
    #     if self.steamworks:
    #         info = self.steamworks.get_achievement(name)
    #         if info == 0:
    #             self.steamworks.set_achievement(name)
    #             self.steamworks.store_stats()
    #             print(f"Achievement Unlocked: {name}")

    def _inverse_title_transform(self, pos):
        """タイトル画面の描画補正(10度回転/1.22倍)を打ち消して論理座標に戻す"""
        cx, cy = Config.WIDTH // 2, Config.HEIGHT // 2
        angle = -10
        scale = 1.22
        dx = pos[0] - cx
        dy = pos[1] - cy
        rad = np.radians(-angle)
        cos_v = np.cos(rad)
        sin_v = np.sin(rad)
        rx = dx * cos_v - dy * sin_v
        ry = dx * sin_v + dy * cos_v
        final_x = (rx / scale) + cx
        final_y = (ry / scale) + cy
        
        return (int(final_x), int(final_y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                self._update_scale()
                continue
                
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                mouse_pos = self._convert_mouse_pos(event.pos)
                event.pos = mouse_pos
                if hasattr(event, 'rel'):
                    event.rel = (int(event.rel[0] / self.scale), int(event.rel[1] / self.scale))

            # -------------------------------------
            # 1. タイピングモード処理
            # -------------------------------------
            if self.ui_manager.typing_mode:
                pygame.key.start_text_input()

                if event.type == pygame.TEXTINPUT:
                    self.ui_manager.input_text += event.text
                    self.ui_manager.editing_text = ""

                elif event.type == pygame.TEXTEDITING:
                    self.ui_manager.editing_text = event.text

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.ui_manager.editing_text == "":
                            matched_key = None
                            if self.ui_manager.typing_target_key_tuple is not None:
                                matched_key = self.ui_manager.typing_target_key_tuple
                            elif self.ui_manager.typing_target_index is not None:
                                matched_entry = next((item for w_idx, item in self.ui_manager.matched_words 
                                                if w_idx == self.ui_manager.typing_target_index), None)
                                matched_key = matched_entry[1] if matched_entry else None
                            
                            if matched_key and self.ui_manager.input_text != "":
                                current_entry = self.word_manager.user_dictionary.get(matched_key, [self.ui_manager.input_text, False])
                                if not current_entry[1]:
                                    current_entry[0] = self.ui_manager.input_text 
                                    self.word_manager.user_dictionary[matched_key] = current_entry
                                    if self.difficulty in ["Bachelor", "Master"]:
                                        self.word_manager.save_user_dic()
                        
                            pygame.key.stop_text_input()
                            self.ui_manager.typing_mode = False
                            self.ui_manager.typing_target_index = None
                            self.ui_manager.typing_target_key_tuple = None
                    
                    elif event.key == pygame.K_BACKSPACE:
                        if self.ui_manager.editing_text == "":
                            self.ui_manager.input_text = self.ui_manager.input_text[:-1]
                continue

            # -------------------------------------
            # 2. トランジション中は操作不能
            # -------------------------------------
            if self.scene_manager.transition_state != "none":
                continue 

            # -------------------------------------
            # 3. MOUSEWHEEL (辞書UIのスクロール)
            # -------------------------------------
            if event.type == pygame.MOUSEWHEEL and self.ui_manager.dic_ui_visible:
                self.ui_manager.dic_scroll_y += event.y * 20
                min_scroll = min(0, -(self.ui_manager.dic_content_height - Config.HEIGHT + 50))
                self.ui_manager.dic_scroll_y = max(min_scroll, min(0, self.ui_manager.dic_scroll_y)) # 範囲制限

            # -------------------------------------
            # 4. MOUSEBUTTONDOWN
            # -------------------------------------
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.esc_pressed_once:
                    self.esc_pressed_once = False
                else:
                    if event.button == 3 and self.current_scene_id == "drawing_canvas":
                        if self.ui_manager.canvas_rect.collidepoint(event.pos):
                            local_pos = (event.pos[0] - self.ui_manager.canvas_rect.x, 
                                         event.pos[1] - self.ui_manager.canvas_rect.y)
                            self.ui_manager.is_erasing = True
                            self.ui_manager.erase_on_canvas(local_pos)
                    elif event.button == 1:
                
                        # a. テキスト表示中はテキスト送り
                        if self.event_manager.is_waiting_for_choice:
                            idx = self.ui_manager.get_clicked_choice(event.pos, self.event_manager.current_choices)
                            if idx is not None:
                                choice = self.event_manager.current_choices[idx]
                                event_id = choice.get("content")
                                if event_id == "EAT_ACTION":
                                    if self.current_scene_id != "dining":
                                        self.dignity -= 1
                                    if self.held_item == "food":
                                        self.hunger -= 1
                                        self.event_manager.trigger_event("FOOD")
                                    elif self.correct_streak >= 10:
                                        self.hunger -= 3
                                        self.event_manager.trigger_event("GOOD_MEAL")
                                    elif self.incorrect_streak >= 4:
                                        self.hunger -= 1
                                        self.event_manager.trigger_event("BAD_MEAL")
                                    self.held_item = None
                                if event_id == "TOILET_ACTION":
                                    self.water_available_today = False
                                    self.toilet_used = True
                                if event_id == "TOILET_REFRESH":
                                    self.toilet_refreshed = True
                                    self.dignity += 20
                                    self.held_item = None
                                if event_id == "TOILET_BADACTION":
                                    self.water_available_today = False
                                    self.dignity -= 1
                                if event_id == "BATH_ACTION":
                                    self.dirty += 2
                                    self.dignity -= 2
                                if event_id == "SHOP_ACTION":
                                    self.held_item = "food"
                                    self.dignity -= 1
                                if event_id == "CHARCOAL_ACTION":
                                    self.held_item = "charcoal"
                                if event_id == "SHEETS_ACTION":
                                    self.sheet_available_today = False
                                    self.dirty //= 2
                                self.event_manager.close_question()
                                if "content" in choice:
                                    self.event_manager.trigger_event(choice["content"])
                                if "target" in choice and choice["target"]:
                                    self.scene_manager.start_transition(choice["target"])
                                return
                        if self.event_manager.event_queue and self.event_manager.event_queue[0]["type"] == "text":
                            if self.event_manager.next_text_page():
                                continue
                            else:
                                continue
                        
                        if self.current_scene_id == "title_screen":
                            # タイトル画面設定UIは正立座標(event.pos)を使用
                            action, value = self.ui_manager.handle_title_settings_mousedown(event.pos, self.current_day, self.num_difficulties)
                            if action == "difficulty_changed" and self.current_day == 0:
                                self.difficulty = Config.DIFFICULTY_LEVELS[value]
                                self.word_manager = WordManager(self.dots, self.difficulty, self.language)
                                self.event_manager.word_manager = self.word_manager
                                self.ui_manager.matched_words = [] 
                                self.ui_manager.set_patterns([])
                                self.ui_manager.set_random_patterns([])
                                self.signature_data = self.word_manager.generate_random_pattern(["⇔", "死"])
                                self._set_initial_random_pattern(["始"])
                            elif action == "volume_changed":
                                self.master_volume = value
                                self.sound_gen.set_master_volume(self.master_volume)
                            elif action == "language_changed":
                                self.language = value
                                self.word_manager = WordManager(self.dots, self.difficulty, self.language)
                                self.ui_manager = UIManager(self.screen, self.dots, self.master_volume, self.difficulty, initial_fullscreen=self.saved_is_fullscreen, language=self.language)
                                self.event_manager = EventManager(self, self.ui_manager, self.word_manager, language=self.language)
                                self.scene_manager = SceneManager(self.screen, language=self.language)
                                self.board_manager = BoardManager(self.screen, self.ui_manager.item_images, language=self.language)
                                self.ui_manager.matched_words = [] 
                                self.ui_manager.set_patterns([])
                                self.ui_manager.set_random_patterns([])
                                self.signature_data = self.word_manager.generate_random_pattern(["⇔", "死"])
                                self._set_initial_random_pattern(["始"])
                            elif action == "reset_clicked" and self.current_day > 0:
                                self.reset_game_state(full_reset=False)
                            elif action == "toggle_fullscreen":
                                if value:
                                    self.display_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                                else:
                                    self.display_window = pygame.display.set_mode((self.logical_w, self.logical_h), pygame.RESIZABLE)
                                self._update_scale()
                            elif action == "end_post":
                                self.current_scene_id = "end_post"
                                self.event_manager.trigger_event("GAME_END")
                                self.scene_manager.set_scene(self.current_scene_id)
                        
                        elif self.current_scene_id == "drawing_canvas":
                            if self.ui_manager.canvas_rect.collidepoint(event.pos):
                                local_pos = (event.pos[0] - self.ui_manager.canvas_rect.x, 
                                            event.pos[1] - self.ui_manager.canvas_rect.y)
                                
                                self.ui_manager.is_drawing = True
                                self.ui_manager.draw_on_canvas(local_pos)
                    
                        # b. UI表示切替トグルボタン
                        if "end" not in self.current_scene_id:
                            if self.current_scene_id != "title_screen":
                                if self.difficulty == "Bachelor":
                                    if self.ui_manager.dot_toggle_rect.collidepoint(event.pos):
                                        self.ui_manager.dots_visible = not self.ui_manager.dots_visible
                                        continue
                                if self.ui_manager.dic_toggle_rect.collidepoint(event.pos):
                                    self.ui_manager.dic_ui_visible = not self.ui_manager.dic_ui_visible
                                    continue
                                if self.ui_manager.image_toggle_rect.collidepoint(event.pos):
                                    if not self.ui_manager.image_data_loaded:
                                        dummy_image_path = "image_default.png" 
                                        self.ui_manager.show_image_ui(dummy_image_path)
                                        self.ui_manager.image_ui_visible = True
                                    else:
                                        # 2回目以降: パネルの開閉をトグル
                                        self.ui_manager.image_ui_visible = not self.ui_manager.image_ui_visible
                                    continue
                            else:
                                self.ui_manager.draw_title_settings(self.current_day, self.num_difficulties, mouse_pos)
                                if not self.cleared:
                                    if self.ui_manager.dot_toggle_rect.collidepoint(event.pos):
                                        self.ui_manager.dots_visible = not self.ui_manager.dots_visible
                                        continue
                        elif self.current_scene_id == "end_over":
                            if self.ui_manager.dot_toggle_rect.collidepoint(event.pos):
                                self.ui_manager.dots_visible = not self.ui_manager.dots_visible
                                continue
                        if not self.cleared:
                            if self.ui_manager.pat_toggle_rect.collidepoint(event.pos):
                                self.ui_manager.patterns_visible = not self.ui_manager.patterns_visible
                                continue

                        # c. 辞書UI内のクリック (テキスト編集/決定)
                        dic_panel_rect = pygame.Rect(Config.WIDTH - self.ui_manager.dic_ui_width + self.ui_manager.dic_ui_offset_x, 0, self.ui_manager.dic_ui_width, Config.HEIGHT)
                        hit_in_dic_ui_element = False 
                
                        if self.ui_manager.dic_ui_visible and dic_panel_rect.collidepoint(event.pos):
                    
                            # 1. テキスト編集クリック判定
                            for text_rect, key_tuple in self.ui_manager.dic_text_hitboxes:
                                if text_rect.collidepoint(event.pos):
                                    existing_entry = self.word_manager.user_dictionary.get(key_tuple, ["", False])
                                    if not existing_entry[1]:
                                        self.ui_manager.typing_mode = True
                                        self.ui_manager.typing_target_key_tuple = key_tuple 
                                        self.ui_manager.input_text = "" if existing_entry[0] == "?" else existing_entry[0]
                                        hit_in_dic_ui_element = True
                                    break 
                    
                            # 2. fixボタンクリック判定
                            if not hit_in_dic_ui_element:
                                for decide_rect, key_tuple in self.ui_manager.dic_decide_hitboxes:
                                    if decide_rect.collidepoint(event.pos):
                                        current_entry = self.word_manager.user_dictionary.get(key_tuple)
                                        if current_entry and not current_entry[1]:
                                            current_entry[1] = not current_entry[1] # 決定フラグをトグル
                                            self.word_manager.user_dictionary[key_tuple] = current_entry
                                            self.word_manager.save_user_dic()
                                        hit_in_dic_ui_element = True
                                        break
                    
                            if hit_in_dic_ui_element:
                                continue 

                        # d. Dots (ドット操作開始)
                        # ドット操作用に座標をチェックする変数を準備
                        # タイトル画面かつDay0の場合のみ、マウス座標を回転させて判定に使用する
                        if self.current_scene_id == "title_screen" and self.current_day == 0:
                            current_dots_offset_x = Config.dots_offset_x
                            current_dots_offset_y = Config.dots_offset_y
                            say_check_rect = self.ui_manager.button_rect.move(current_dots_offset_x, current_dots_offset_y)
                            dot_check_pos = self._inverse_title_transform(event.pos) # ドット用座標
                        else:
                            current_dots_offset_x = self.ui_manager.dot_offset_x - 10
                            current_dots_offset_y = 0
                            say_check_rect = self.ui_manager.button_rect.move(self.ui_manager.dot_offset_x, 0)
                            dot_check_pos = event.pos # 通常座標
                        
                        if self.ui_manager.dots_visible or say_check_rect.collidepoint(dot_check_pos) or (self.current_scene_id == "title_screen" and self.current_day == 0):
                            dot_hit = False
                        
                            for i, d in enumerate(self.dots):
                                check_rect = d.move(current_dots_offset_x, current_dots_offset_y)
                            
                                if check_rect.collidepoint(dot_check_pos):
                                    if self.current_scene_id in ["title_screen", "end_over"]:
                                        self.ui_manager.set_patterns([])
                                    dot_hit = True
                                    self.selected.clear()
                                    self.path.clear()
                                    self.used_lines.clear()
                                    self.selected.append(i)
                                    self.path.append(dot_check_pos) # 記録するパスは変換後の座標
                                    self.current_pos = None
                                    self.dragging = True
                                    self.last_dot_index = i
                                    self.special_reentry_used = False
                                    break
                            if dot_hit:
                                continue 

                        # e. Dot UI (DECODEボタン: ユーザーパターン再生/辞書登録)
                        if say_check_rect.collidepoint(dot_check_pos):
                            if not self.ui_manager.dots_visible:
                                self.ui_manager.dots_visible = True
                        
                            self.play_patterns(self.ui_manager.patterns) # ユーザーパターン再生キューに設定
                        
                            # タイトル画面専用処理
                            if self.current_scene_id == "title_screen":
                                if len(self.ui_manager.patterns) == 1:
                                    user_lines = self.ui_manager.patterns[0]["used_lines"]
                                    if user_lines == self.required_end_lines:
                                        self.current_scene_id = "end_"
                                        self.running = False # "終"で終了
                                        continue
                                    if user_lines == self.required_start_lines:
                                        self.scene_manager.start_transition(self.initial_scene) # "始"で遷移
                                        self.waiting_for_start_pattern = False
                                        self.ui_manager.dots_visible = False
                                        self.ui_manager.patterns_visible = False 
                                        self.ui_manager.set_random_patterns([])
                                        continue
                                continue 
                            
                            if self.current_scene_id == "end_over":
                                user_lines = self.ui_manager.patterns[0]["used_lines"]
                                if user_lines == self.required_end_lines:
                                    self.ui_manager.dots_visible = False 
                                    self.ui_manager.patterns_visible = False 
                                    self.hunger = 1.8
                                    self.current_scene_id = "end_over_"
                                    self.event_manager.trigger_event("GAME_OVER_2")
                                    self.scene_manager.start_transition(self.current_scene_id)
                                    if self.num_difficulties < 2:
                                        self.num_difficulties = 2
                                        self.event_manager.trigger_event("RELEASE_MASTER")
                        
                            # 通常のDECODE処理 (パターン上書きとハイライト決定)
                            new_matched_words = self.ui_manager.matched_words[:]
                        
                            user_keys = []
                            for p in self.ui_manager.patterns:
                                if "used_lines" in p:
                                    user_keys.append(tuple(sorted(list(p["used_lines"]))))
                        
                            for user_key in user_keys:
                                for idx, rand_p in enumerate(self.ui_manager.random_patterns):
                                    rand_lines = rand_p["used_lines"]
                                    rand_key = tuple(sorted(list(rand_lines)))
                                
                                    if set(user_key) == set(rand_key):
                                        existing_user_entry = self.word_manager.user_dictionary.get(rand_key)
                                        is_decided = existing_user_entry and existing_user_entry[1]
                                    
                                        if not is_decided and not any(x[0] == idx for x in self.ui_manager.matched_words):
                                            user_p_for_copy = next((p for p in self.ui_manager.patterns if tuple(sorted(list(p.get("used_lines", set())))) == user_key), None)
                                        
                                            if user_p_for_copy:
                                                self.ui_manager.random_patterns[idx] = user_p_for_copy.copy()
                                                self.ui_manager.random_patterns[idx]["key"] = rand_key 
                                            
                                                if rand_key not in self.word_manager.user_dictionary:
                                                    self.word_manager.user_dictionary[rand_key] = ["?", False]
                                                    self.word_manager.save_user_dic()
                                                new_matched_words.append((idx, rand_key))
                                        
                                        user_pattern_index = -1
                                        for i in range(len(self.ui_manager.patterns) - 1, -1, -1):
                                            p_key_check = tuple(sorted(list(self.ui_manager.patterns[i].get("used_lines", set()))))
                                            if p_key_check == user_key:
                                                user_pattern_index = i
                                                break

                                        if user_pattern_index != -1:
                                            self.clear_pattern() # パターンスタックをクリア

                            self.ui_manager.matched_words = new_matched_words
                            continue

                        # f. Random Pattern (画面上のパターンアイコンクリック: 再生/編集モード切替)
                        pattern_hit = False
                        for idx, rect in enumerate(self.ui_manager.random_pattern_rects):
                            if rect.collidepoint(event.pos):
                                pattern_hit = True
                                current_lines = self.ui_manager.random_patterns[idx]["used_lines"]
                                pattern_key = tuple(sorted(list(set(current_lines))))
                                existing_entry = self.word_manager.user_dictionary.get(pattern_key, ["", False])
                                is_decided = existing_entry[1]
                            
                                is_matched = any(w_idx == idx for w_idx, _ in self.ui_manager.matched_words)
                            
                                if self.difficulty == "Master" or is_matched or is_decided:
                                    if not is_decided:
                                        self.ui_manager.typing_mode = True
                                        self.ui_manager.typing_target_index = idx 
                                        self.ui_manager.typing_target_key_tuple = pattern_key 
                                        initial_text = existing_entry[0]
                                        self.ui_manager.input_text = "" if initial_text == "?" else initial_text
                                else:
                                    pdata = self.ui_manager.random_patterns[idx]
                                    path_pts = pdata["path"]
                                    indices = self.ui_manager.pattern_to_indices(path_pts, self.dots)
                                    sound = self.sound_gen.generate_sound(indices, path_pts)
                                    sound.play()
                            
                                break
                        if pattern_hit:
                            continue 

                        # g. シーンHitbox判定 (移動・調べる)
                        scene_action_triggered = False
                        for hitbox in self.scene_manager.get_hitboxes():
                            rect = pygame.Rect(hitbox["rect"])
                        
                            is_board_hitbox = (self.current_scene_id == "classroom" and 
                                                rect.collidepoint(event.pos) and 
                                                hitbox.get("target") == "board_view")
                        
                            if is_board_hitbox and not self.board_available_today:
                                self.event_manager.trigger_event("BOARD_ALREADY_USED")
                                scene_action_triggered = True
                                break

                            if rect.collidepoint(event.pos):
                                self._handle_scene_action(hitbox)
                                scene_action_triggered = True
                                break 
                    
                        if scene_action_triggered:
                            continue

                        # h. アイテムクリック (board_viewでのみ有効)
                        if self.current_scene_id == "board_view":
                            sentence, is_correct = self.board_manager.handle_item_click(event.pos)
                        
                            if is_correct is not None:
                                # --- 合格/不合格判定とアクション ---
                                if is_correct:
                                    self.correct_streak += 1
                                    self.incorrect_streak = 0
                                else:
                                    self.incorrect_streak += 1

                                # 合格判定
                                if self.correct_streak >= 10 or self.incorrect_streak >= 4:
                                    self.board_available_today = False
                                    self.event_manager.trigger_event("BOARD_PASSED")
                                    self.scene_manager.start_transition("classroom")
                                    self.held_item = "meal"
                                    self._save_data()
                            
                            if sentence:
                                self._set_initial_random_pattern(sentence)
                                self.ui_manager.set_patterns([]) # 正解したらユーザーパターンをクリア
                            continue

            # -------------------------------------
            # 5. MOUSEBUTTONUP (ドット操作終了)
            # -------------------------------------
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                if self.current_scene_id == "drawing_canvas":
                    self.ui_manager.is_erasing = False
                    self.ui_manager.reset_draw_pos()
                else:
                    self.ui_manager.pop_user_pattern()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.current_scene_id == "drawing_canvas":
                    self.ui_manager.is_drawing = False
                    self.ui_manager.reset_draw_pos()
                    return
                # Handle Title Settings UP (event.posは正立座標なのでそのまま渡す)
                action, value = self.ui_manager.handle_title_settings_mouseup()
                if action == "volume_drag_end":
                    self.master_volume = value
                    self.sound_gen.set_master_volume(self.master_volume)
                    self.signature_data = self.word_manager.generate_random_pattern(["⇔", "死"])
                    self._set_initial_random_pattern(["始"])
                    continue
                self.dragging = False
                if len(self.path) > 1:
                    final_path = list(self.path)
                    if self.current_day == 0:
                        final_path = [(x - Config.dots_offset_x, y - Config.dots_offset_y) for (x, y) in final_path]
                    user_pattern_data = {"path": final_path, "used_lines": self.used_lines.copy()}
                    self.ui_manager.add_user_pattern(user_pattern_data)
                self.selected.clear()
                self.path.clear()
                self.used_lines.clear()
                self.current_pos = None
                self.last_dot_index = None
                self.special_reentry_used = False
                self.draw_special_circle = False

            # -------------------------------------
            # 6. MOUSEMOTION (ドット操作中)
            # -------------------------------------
            elif event.type == pygame.MOUSEMOTION:
                if self.current_scene_id == "title_screen":
                    # UIモーション判定には正立座標(event.pos)を使う
                    action, value = self.ui_manager.handle_title_settings_motion(event.pos)
                    if action == "volume_changed":
                        self.master_volume = value
                        self.sound_gen.set_master_volume(self.master_volume)
                
                if self.current_scene_id == "drawing_canvas":
                    if self.current_scene_id == "drawing_canvas":
                        local_pos = (event.pos[0] - self.ui_manager.canvas_rect.x, 
                                     event.pos[1] - self.ui_manager.canvas_rect.y)
                    if self.ui_manager.is_drawing:
                        self.ui_manager.draw_on_canvas(local_pos)
                    elif self.ui_manager.is_erasing:
                        self.ui_manager.erase_on_canvas(local_pos)
                
                if self.dragging:
                    # ドット操作中用の座標計算
                    if self.current_scene_id == "title_screen" and self.current_day == 0:
                        dot_check_pos = self._inverse_title_transform(event.pos)
                        current_offset_x = Config.dots_offset_x
                        current_offset_y = Config.dots_offset_y
                    else:
                        dot_check_pos = event.pos
                        current_offset_x = self.ui_manager.dot_offset_x - 10
                        current_offset_y = 0

                    self.current_pos = dot_check_pos # 描画のために変換後の座標を保持
                    now_dot = None

                    for i, d in enumerate(self.dots):
                        check_rect = d.move(current_offset_x, current_offset_y)
                        if check_rect.collidepoint(dot_check_pos):
                            now_dot = i
                        
                            # 特別再入場処理 (ドット0での複雑な処理)
                            if i == 0 and self.last_dot_index is None:
                                lastx, lasty = self.path[-1]
                                if self.current_day == 0:
                                    check_rect = self.dots[0].move(current_offset_x, current_offset_y)
                                else:
                                    check_rect = self.dots[0].move(self.ui_manager.dot_offset_x - 10, 0)
                                if check_rect.collidepoint(lastx, lasty) and not self.special_reentry_used:
                                    self.selected.append(0)
                                    self.draw_special_circle = True
                                    # Catmull-Romのためのパス調整ロジック
                                    if len(self.path) > 1:
                                        x1, y1 = self.path[-1]
                                        x2, y2 = self.path[-2]
                                        loop_ratio = 0.2
                                        self.path.append((x1 + (x1 - x2)*loop_ratio, y1 + (y1 - y2)*loop_ratio))
                                        if x2-check_rect.center[0] < y2-check_rect.center[1]:
                                            self.path.append((x1 + (x1 + y1 - x2 - y2)*loop_ratio, y1 + (-x1 + y1 + x2 - y2)*loop_ratio))
                                            self.path.append((x1 + (y1 - y2)*loop_ratio, y1 - (x1 - x2)*loop_ratio))
                                        else:
                                            self.path.append((x1 + (x1 - y1 - x2 + y2)*loop_ratio, y1 + (x1 + y1 - x2 - y2)*loop_ratio))
                                            self.path.append((x1 - (y1 - y2)*loop_ratio, y1 + (x1 - x2)*loop_ratio))
                                    else:
                                        self.path.append((self.path[-1][0], self.path[-1][1] - 30))
                                        self.path.append((self.path[-2][0] - 30, self.path[-2][1] - 30))
                                        self.path.append((self.path[-3][0] - 30, self.path[-3][1]))
                                    self.path.append(self.path[-4])
                                    self.special_reentry_used = True
                                    self.used_lines.add((0, 0))
                                    break
                        
                            if self.selected:
                                last = self.selected[-1]
                                if (last==1 and i==4) or (last==4 and i==1):
                                    if not ((2,1) in self.used_lines or (1,2) in self.used_lines or (2,4) in self.used_lines or (4,2) in self.used_lines):
                                        self.selected.append(2)
                                        x1, y1 = self.dots[1].center
                                        x4, y4 = self.dots[4].center
                                        self.path.append(((x1 + x4) / 2 + current_offset_x, (y1 + y4) / 2 + current_offset_y))
                                        self.used_lines.add(tuple(sorted((last, 2))))
                                        last=2
                                    else:
                                        break
                                line = tuple(sorted((last, i)))
                                if i!=last and line not in self.used_lines and (i,last) not in self.used_lines:
                                    self.selected.append(i)
                                    self.path.append(dot_check_pos)
                                    self.used_lines.add(line)
                            break
                    self.last_dot_index = now_dot
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_scene_id == "drawing_canvas":
                        self.saved_canvas_hash = self.ui_manager.save_drawing()
                        self.ui_manager.reset_draw_pos()
                        self.scene_manager.set_scene("atelier")
                        self.event_manager.trigger_event("finish")
                        self.held_item = None
                        self._save_data()
                    elif self.esc_pressed_once:
                        self.running = False
                    else:
                        self.esc_pressed_once = True
                        
    def draw(self):
        """全ての要素を描画する"""
        mouse_pos = self._convert_mouse_pos(pygame.mouse.get_pos())
        if not (self.waiting_for_start_pattern and self.current_day == 0):
            self.scene_manager.draw_background()
        if self.current_scene_id == "board_view":
            self.board_manager.draw_board_grid(mouse_pos) 
        if self.current_scene_id == "end_dream":
            self.dream_manager.draw()

        darkness_alpha = min(self.dirty * 6, 180)
        if darkness_alpha > 0:
            dark_overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT))
            dark_overlay.fill((0, 0, 0))
            dark_overlay.set_alpha(darkness_alpha)
            self.screen.blit(dark_overlay, (0, 0))

        # self.scene_manager.draw_debug_hitboxes(self.sys_font)
        
        self.ui_manager.update_slide_animation(max(20-self.dignity, 0))
        is_playing_random = (self.playing_pattern_list == self.ui_manager.random_patterns or
                             (self.playing_pattern_list and 
                              all(p in self.ui_manager.random_patterns for p in self.playing_pattern_list)))
        highlight_index = self.current_play_index if self.playing_pattern_list else -1
        
        if "end" not in self.current_scene_id:
            if self.current_scene_id != "title_screen":
                if self.difficulty == "Bachelor":
                    self.ui_manager.draw_dot_ui(self.selected, self.current_pos, self.draw_special_circle, mouse_pos)
                self.ui_manager.draw_dic_ui(self.word_manager, mouse_pos)
                self.ui_manager.draw_image_ui(mouse_pos)
            else:
                if self.current_day == 0:
                    self.ui_manager.draw_signature_ui(self.signature_data, self.selected, self.current_pos, self.draw_special_circle, self.waiting_for_start_pattern)
                    self.ui_manager.draw_title_settings(self.current_day, self.num_difficulties, mouse_pos)
                else:
                    self.ui_manager.draw_title_settings(self.current_day, self.num_difficulties, mouse_pos)
                    if not self.cleared:
                        self.ui_manager.draw_dot_ui(self.selected, self.current_pos, self.draw_special_circle, mouse_pos)
        elif self.current_scene_id == "end_over":
            self.ui_manager.draw_dot_ui(self.selected, self.current_pos, self.draw_special_circle, mouse_pos)
        if not self.cleared and self.current_day > 0:
            self.ui_manager.draw_pattern_ui(
                self.waiting_for_start_pattern, self.word_manager, mouse_pos, 
                highlight_index=highlight_index, is_playing_random=is_playing_random,
                disable_random_highlight=self.disable_random_highlight
            )
        
        if self.scene_manager.current_scene_id == "drawing_canvas" or self.initial_scene == "title_screen":
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(self.ui_manager.canvas_surf, self.ui_manager.canvas_rect.topleft)
            pygame.draw.rect(self.screen, (200, 200, 200), self.ui_manager.canvas_rect, 3)
            
        self.ui_manager.draw_typing_input()

        if self.scene_manager.transition_state == "none":
            self.ui_manager.render_text_box()
            if self.event_manager.is_waiting_for_choice:
                self.ui_manager.draw_question_ui(self.event_manager.current_choices, mouse_pos)
        self.scene_manager.draw_fade()
        
        if self.esc_pressed_once:
            overlay = pygame.Surface((self.logical_w, self.logical_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            text_surf = self.ui_manager.sys_font.render("再度エスケープキーで終了" if self.language == "JP" else "Press ESC again to exit", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(self.logical_w // 2, self.logical_h // 2))
            self.screen.blit(text_surf, text_rect)

        scaled_surf = pygame.transform.scale(
            self.screen, 
            (int(self.logical_w * self.scale), int(self.logical_h * self.scale))
        )
        
        self.display_window.fill((0, 0, 0))
        self.display_window.blit(scaled_surf, (self.offset_x, self.offset_y))
        
        pygame.display.update()

    async def run(self):
        clock = pygame.time.Clock()
        self.running = True
        self.current_bgm_volume = 0.0
        FADE_TIME_SECONDS = 3.0
        try:
            if os.path.exists(Config.BGM_PATH):
                pygame.mixer.music.load(Config.BGM_PATH)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.pause()
                self.bgm_loaded = True
        except Exception:
            pass
            
        while self.running:
            dt = clock.tick(60)
            if self.bgm_loaded:
                if (not self.board_available_today and self.current_scene_id != "title_screen") and not self.bgm_active:
                    pygame.mixer.music.set_volume(0)
                    self.current_bgm_volume = 0.0
                    pygame.mixer.music.unpause()
                    self.bgm_active = True
                elif (self.board_available_today or self.current_scene_id == "title_screen") and self.bgm_active:
                    pygame.mixer.music.pause()
                    self.bgm_active = False
                if self.bgm_active:
                    if self.current_bgm_volume < self.master_volume:
                        step = self.master_volume / (FADE_TIME_SECONDS * 60)
                        self.current_bgm_volume = min(self.current_bgm_volume + step, self.master_volume)
                        pygame.mixer.music.set_volume(self.current_bgm_volume)
                    else:
                        pygame.mixer.music.set_volume(self.master_volume)
            
            self.current_scene_id = self.scene_manager.current_scene_id 
            self.scene_manager.update_transition(fade_speed=10-self.hunger*5)
            self.handle_events()
            
            if self.scene_manager.transition_state == "none":
                self.event_manager.update(dt)
                
            if self.playing_pattern_list:
                self.time_to_next_pattern -= dt 
                
                if self.time_to_next_pattern <= 0:
                    self.current_play_index += 1
                    
                    if self.current_play_index < len(self.playing_pattern_list):
                        pdata = self.playing_pattern_list[self.current_play_index]
                        path_pts = pdata["path"]
                        
                        indices = self.ui_manager.pattern_to_indices(path_pts, self.dots) 
                        sound = self.sound_gen.generate_sound(indices, path_pts)
                        sound.play()
                        
                        sound_duration_ms = int(len(path_pts) * 150)
                        self.time_to_next_pattern = sound_duration_ms + self.PATTERN_DELAY_MS
                        
                    else:
                        self.playing_pattern_list = []
                        self.current_play_index = -1
                        self.time_to_next_pattern = 0
            
            if self.current_scene_id == "end_dream":
                self.dream_manager.update(dt)
                self.current_vol = ((self.dream_manager.alpha+200) / 455.0)
                
                if not self.dream_manager.is_finished:
                    self.ecg_timer += dt
                    self.current_vol = ((self.dream_manager.alpha+200) / 455.0) * self.master_volume
                
                if not self.dream_manager.is_finished:
                    self.ecg_timer += dt
                    if self.ecg_timer > 4100:
                        hb_sound = self.sound_gen.get_ecg_heartbeat()
                        hb_sound.set_volume(self.current_vol)
                        hb_sound.play()
                        self.ecg_timer = 0
                else:
                    if self.ecg_continuous_sound is None:
                        self.ecg_continuous_sound = self.sound_gen.get_ecg_flatline(dur=2.0)
                        self.ecg_continuous_sound.play(loops=-1)
                    self.ecg_continuous_sound.set_volume(self.current_vol)
                    
                if self.dream_manager.should_transition():
                    if self.dream_manager.alpha <= -200:
                        if self.ecg_continuous_sound:
                            self.ecg_continuous_sound.stop()
                            self.ecg_continuous_sound = None
                    
                    self.current_scene_id = "black"
                    self.scene_manager.start_transition("black")
                    
            if self.dream_manager.should_transition() and self.ecg_continuous_sound:
                if self.current_vol <= 0:
                    self.ecg_continuous_sound.stop()
                    self.ecg_continuous_sound = None
                else:
                    self.current_vol = max(0, self.current_vol-1/150)
                    self.ecg_continuous_sound.set_volume(self.current_vol)
            
            self.draw()
            
            if self.next_voice and self.ui_manager.random_patterns and not self.playing_pattern_list:
                self.play_patterns(self.ui_manager.random_patterns)
                self.next_voice = False
            
            # ブラウザ(pygbag)のイベントループに制御を返す。
            # デスクトップ(通常のpygame)実行時も無害なため常時呼び出す。
            await asyncio.sleep(0)
                
        if "end" not in self.current_scene_id and self.current_scene_id != "title_screen":
            self._save_data()
        pygame.quit()

async def main():
    game = LackGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())