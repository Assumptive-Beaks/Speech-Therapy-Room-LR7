import os
import sys
from pathlib import Path

# -----------------------------
# 設定・定数クラス
# -----------------------------
class Config:
    if hasattr(sys, '_MEIPASS'):
        BASE_DIR = sys._MEIPASS
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    _assets = os.path.join(BASE_DIR, "assets")
    ASSETS_DIR = _assets
    
    GAME_NAME = "LR7"
    if sys.platform == "emscripten":
        # ブラウザ(pygbag)環境: LOCALAPPDATAやPath.home()は存在しない/意味を持たないため、
        # 実行時カレントディレクトリ配下の相対パスを使う。
        # これはpygbagが提供する仮想ファイルシステム上に作成される。
        # 注意: このディレクトリはブラウザセッション内では読み書きできるが、
        # ページを閉じて再度開いた際に内容が保持される保証はない
        # (pygbag側でIndexedDB永続化が有効化されていない限り)。
        SAVE_DIR = Path(f"save_{GAME_NAME}")
    elif sys.platform == "win32":
        # Windows: C:\Users\ユーザー名\AppData\Local\LR7
        SAVE_DIR = Path(os.getenv('LOCALAPPDATA')) / GAME_NAME
    else:
        # Mac/Linux: ホームディレクトリの .LR7
        SAVE_DIR = Path.home() / f".{GAME_NAME}"
    
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    WIDTH, HEIGHT = 800, 600
    BG_COLOR = (20, 20, 20)
    DOT_COLOR = (180, 180, 180)
    DOT_ACTIVE_COLOR = (80, 160, 255)
    LINE_COLOR = (80, 160, 255)
    BUTTON_BG = (100, 200, 100)
    BUTTON_TEXT = (255, 255, 255)
    PLAY_BUTTON_BG = (200, 100, 100)
    
    RADIUS = 22
    SPACING_X, SPACING_Y = 80, 80
    
    DIC_PATH = os.path.join(str(SAVE_DIR), "save.pickle")
    IMAGE_TEST_PATH = os.path.join(str(SAVE_DIR), "image_test.png")
    FONT_PATH = os.path.join(ASSETS_DIR, "cinecaption226.ttf")
    HAND_PATH = os.path.join(ASSETS_DIR, "crayon_1-1.ttf")
    ICON_PATH = os.path.join(ASSETS_DIR, "icon.png")
    BGM_PATH = os.path.join(ASSETS_DIR, "room.ogg")
    
    TYPE_SPEED = 80
    HIGHLIGHT_DURATION = 500

    # アイテム定義
    ITEM_DEFINITIONS = {
        'apple': {'色':'赤色','形':'-','三態':'神為','大きさ':'-','固さ':'+','善悪':'+', '距離': None, '数': None}, 
        'bee': {'色': '黄色', '形': '-', '三態': '神為', '大きさ': '-', '固さ': '-', '善悪': '-', '距離': None, '数': None}, 
        'car': {'色': '水色', '形': '+', '三態': '他為', '大きさ': '+', '固さ': '+', '善悪': '-', '距離': None, '数': None}, 
        'coin': {'色': '黄色', '形': '-', '三態': '他為', '大きさ': '-', '固さ': '+', '善悪': '-', '距離': None, '数': None}, 
        'crocodile': {'色': '緑色', '形': '+', '三態': '神為', '大きさ': '+', '固さ': '+', '善悪': '-', '距離': None, '数': None}, 
        'crow': {'色': '黒色', '形': '-', '三態': '神為', '大きさ': '-', '固さ': '-', '善悪': '+', '距離': None, '数': None}, 
        'doll': {'色': '水色', '形': '-', '三態': '他為', '大きさ': '-', '固さ': '-', '善悪': '+', '距離': None, '数': None}, 
        'fire': {'色': '赤色', '形': None, '三態': '神為', '大きさ': '+', '固さ': '-', '善悪': '-', '距離': None, '数': None}, 
        'gorilla': {'色': '黒色', '形': '-', '三態': '神為', '大きさ': '+', '固さ': '-', '善悪': '-', '距離': None, '数': None}, 
        'greenonion': {'色': '緑色', '形': '+', '三態': '神為', '大きさ': '-', '固さ': '-', '善悪': '+', '距離': None, '数': None}, 
        'hammer': {'色': '黒色', '形': '+', '三態': '他為', '大きさ': '-', '固さ': '+', '善悪': '-', '距離': None, '数': None}, 
        'hole': {'色': None, '形': '-', '三態': '我為', '大きさ': '-', '固さ': '-', '善悪': '-', '距離': None, '数': None}, 
        'hospital': {'色':'赤色','形': '+','三態':'他為','大きさ':'+','固さ':'+','善悪':'+', '距離': None, '数': None}, 
        'jeans': {'色':'青色','形': '+','三態':'他為','大きさ':'-','固さ':'+','善悪':'+', '距離': None, '数': None}, 
        'memory': {'色': None, '形': None, '三態': '我為', '大きさ': '+', '固さ': '-', '善悪': '-', '距離': None, '数': None}, 
        'sandcastle': {'色': '黄色', '形': '+', '三態': '他為', '大きさ': '+', '固さ': '-', '善悪': '+', '距離': None, '数': None}, 
        'snowman': {'色': '白色', '形': '-', '三態': '他為', '大きさ': '+', '固さ': '-', '善悪': '+', '距離': None, '数': None},
        'thunder': {'色': '白色', '形': '+', '三態': '神為', '大きさ': '+', '固さ': '-', '善悪': '-', '距離': None, '数': None},  
        'tree': {'色': '黄色', '形': '+', '三態': '神為', '大きさ': '+', '固さ': '+', '善悪': '+', '距離': None, '数': None}, 
        'urchin': {'色': '紫色', '形': '-', '三態': '神為', '大きさ': '-', '固さ': '+', '善悪': '-', '距離': None, '数': None}, 
        'water': {'色': None, '形': None, '三態': '他為', '大きさ': '-', '固さ': '-', '善悪': '+', '距離': None, '数': None}, 
        'whale': {'色': '青色', '形': '-', '三態': '神為', '大きさ': '+', '固さ': '+', '善悪': '+', '距離': None, '数': None}, 
        'wine': {'色': '紫色', '形': '+', '三態': '他為', '大きさ': '-', '固さ': '-', '善悪': '+', '距離': None, '数': None}, 
   }
    
    # オセロ盤のパラメータ
    BOARD_SIZE = 420
    BOARD_COLS = 6
    BOARD_ROWS = 6
    CELL_SIZE = BOARD_SIZE // BOARD_COLS
    
    # 画像ファイルパスのマップを内包表記で動的に生成
    ITEM_IMAGE_NAMES = [
        'apple', 'bee', 'car', 'coin', 'crocodile', 'crow', 'doll', 'fire', 'gorilla', 'greenonion', 
        'hammer', 'hole', 'hospital', 'jeans', 'memory', 'sandcastle', 'snowman', 'thunder', 'tree', 'urchin', 
        'water', 'whale','wine',
    ]
    ITEM_IMAGE_MAP = {}
    for name in ITEM_IMAGE_NAMES:
        ITEM_IMAGE_MAP[name] = os.path.join(_assets, f"{name}.png")

    del _assets
    
    # --- 難易度と音量設定 ---
    DIFFICULTY_LEVELS = ["Bachelor", "Master", "Doctor"]
    DEFAULT_DIFFICULTY = "Bachelor"
    DEFAULT_VOLUME = 0.5 
    UI_RIGHT_X = WIDTH - 180
    UI_BUTTON_WIDTH = 150
    VOLUME_BAR_W = UI_BUTTON_WIDTH
    VOLUME_BAR_H = 10
    VOLUME_BAR_RECT = (UI_RIGHT_X, HEIGHT - 150, VOLUME_BAR_W, VOLUME_BAR_H)
    VOLUME_TEXT_POS = (UI_RIGHT_X, HEIGHT - 175)
    DIFFICULTY_RECT_WIDTH = UI_BUTTON_WIDTH
    DIFFICULTY_RECT_HEIGHT = 30
    DIFFICULTY_SPACING = 5
    DIFFICULTY_STACK_HEIGHT = 4 * DIFFICULTY_RECT_HEIGHT + 3 * DIFFICULTY_SPACING
    DIFFICULTY_TOP_Y = VOLUME_TEXT_POS[1] - 30 - DIFFICULTY_STACK_HEIGHT
    DIFFICULTY_UI_POS = (UI_RIGHT_X, DIFFICULTY_TOP_Y)
    
    dots_offset_x, dots_offset_y = 370, 50
    
    # デバッグモードフラグ
    DEBUG_MODE = True