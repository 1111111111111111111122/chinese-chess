from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import json
import os
import random
from copy import deepcopy
from datetime import datetime
import threading

# ===================== 全局配置（和你原来的逻辑完全一致） =====================
LOG_FOLDER = "gamelog"
SETTING_FOLDER = "settinglog"
SETTING_FILE = os.path.join(SETTING_FOLDER, "config.json")
SYS_SETTING_FILE = os.path.join(SETTING_FOLDER, "sys_config.json")
LEVELS_FILE = "levels.json"

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
if not os.path.exists(SETTING_FOLDER):
    os.makedirs(SETTING_FOLDER)

# 开局棋盘
START_BOARD = [
    ['r','n','b','a','k','a','b','n','r'],
    [0,0,0,0,0,0,0,0,0],
    [0,'c',0,0,0,0,0,'c',0],
    ['p',0,'p',0,'p',0,'p',0,'p'],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    ['P',0,'P',0,'P',0,'P',0,'P'],
    [0,'C',0,0,0,0,0,'C',0],
    [0,0,0,0,0,0,0,0,0],
    ['R','N','B','A','K','A','B','N','R'],
]

EMPTY_BOARD = [[0 for _ in range(9)] for _ in range(10)]

LEVELS = {}
def load_levels_data():
    global LEVELS
    if os.path.exists(LEVELS_FILE):
        try:
            with open(LEVELS_FILE, "r", encoding="utf-8") as f:
                raw_levels = json.load(f)
                LEVELS = {int(k): v for k, v in raw_levels.items()}
        except Exception as e:
            print(f"加载关卡数据失败: {e}")
            LEVELS = {}
    else:
        print(f"找不到 {LEVELS_FILE} 文件！")
    for i in range(21, 101):
        if i not in LEVELS:
            LEVELS[i] = {
                "name": f"挑战第{i}关", "steps": 15,
                "desc": "后续待开发关卡。",
                "board": [
                    [0,0,0,0,"k",0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0],
                    [0,0,"R",0,0,0,0,0,0],
                    [0,0,0,0,"K",0,0,0,0]
                ]
            }

load_levels_data()

name_map = {
    'K':'帥','A':'仕','B':'相','N':'馬','R':'車','C':'炮','P':'兵',
    'k':'將','a':'士','b':'象','n':'馬','r':'車','c':'砲','p':'卒',
    0:''
}

PIECE_VALUE = {
    'K':10000, 'A':200, 'B':200, 'N':400, 'R':900, 'C':450, 'P':80,
    'k':10000, 'a':200, 'b':200, 'n':400, 'r':900, 'c':450, 'p':80
}

PST = {
    'P': [
        [ 90, 90,110,120,120,120,110, 90, 90],
        [ 90, 90,110,120,120,120,110, 90, 90],
        [ 70, 90,110,110,110,110,110, 90, 70],
        [ 40, 50, 60, 70, 80, 70, 60, 50, 40],
        [ 10, 20, 30, 40, 50, 40, 30, 20, 10],
        [  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [  0,  0,  0,  0,  0,  0,  0,  0,  0],
    ],
    'N': [
        [  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [  0,  0,  2,  0,  4,  0,  2,  0,  0],
        [  0,  2,  4,  6,  6,  6,  4,  2,  0],
        [  2,  4,  6,  8,  8,  8,  6,  4,  2],
        [  4,  6,  8, 10, 10, 10,  8,  6,  4],
        [  4,  6,  8, 10, 10, 10,  8,  6,  4],
        [  2,  4,  6,  8,  8,  8,  6,  4,  2],
        [  0,  2,  4,  6,  6,  6,  4,  2,  0],
        [  0,  0,  2,  0,  4,  0,  2,  0,  0],
        [  0, -2,  0,  0,  0,  0,  0, -2,  0],
    ],
    'R': [
        [  6,  8,  8, 10, 10, 10,  8,  8,  6],
        [  6,  8,  8, 10, 10, 10,  8,  8,  6],
        [  6,  8,  8, 10, 10, 10,  8,  8,  6],
        [  8, 10, 10, 12, 12, 12, 10, 10,  8],
        [  8, 10, 10, 12, 12, 12, 10, 10,  8],
        [  8, 10, 10, 12, 12, 12, 10, 10,  8],
        [  6,  8,  8, 10, 10, 10,  8,  8,  6],
        [  6,  8,  8, 10, 10, 10,  8,  8,  6],
        [  6,  8,  8, 10, 10, 10,  8,  8,  6],
        [  4,  6,  6,  8,  8,  8,  6,  6,  4],
    ],
    'C': [
        [  6,  6,  4,  4,  4,  4,  4,  6,  6],
        [  8,  8,  6,  6,  6,  6,  6,  8,  8],
        [  4,  4,  2,  2,  2,  2,  2,  4,  4],
        [  2,  2,  0,  0,  0,  0,  0,  2,  2],
        [  0,  2,  2,  2,  2,  2,  2,  2,  0],
        [  0,  2,  2,  2,  2,  2,  2,  2,  0],
        [  2,  2,  0,  0,  0,  0,  0,  2,  2],
        [  4,  4,  2,  2,  2,  2,  2,  4,  4],
        [  8,  8,  6,  6,  6,  6,  6,  8,  8],
        [  6,  6,  4,  4,  4,  4,  4,  6,  6],
    ],
}

# 音频加载（Kivy SoundLoader）
bgm = None
luozi_sound = None
jiangjun_sound = None
if os.path.exists("music/beijing.mp3"):
    bgm = SoundLoader.load("music/beijing.mp3")
if os.path.exists("music/luozi.mp3"):
    luozi_sound = SoundLoader.load("music/luozi.mp3")
if os.path.exists("music/jiangjun.mp3"):
    jiangjun_sound = SoundLoader.load("music/jiangjun.mp3")

# 配置读写
red_player = "棋手"
black_player = "电脑"
ai_level = "初级"
hint_level = "初级"
bgm_on = True
sound_effect_on = True
show_time_on = False

def load_config():
    global red_player, black_player, ai_level, hint_level
    default_cfg = {"red_player": "棋手", "black_player": "电脑", "ai_level": "初级", "hint_level": "初级"}
    if os.path.exists(SETTING_FILE):
        try:
            with open(SETTING_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            red_player = cfg.get("red_player", default_cfg["red_player"])
            black_player = cfg.get("black_player", default_cfg["black_player"])
            ai_level = cfg.get("ai_level", default_cfg["ai_level"])
            hint_level = cfg.get("hint_level", default_cfg["hint_level"])
        except Exception:
            red_player, black_player = default_cfg["red_player"], default_cfg["black_player"]
            ai_level, hint_level = default_cfg["ai_level"], default_cfg["hint_level"]
    else:
        red_player, black_player = default_cfg["red_player"], default_cfg["black_player"]
        ai_level, hint_level = default_cfg["ai_level"], default_cfg["hint_level"]

def save_config():
    cfg = {"red_player": red_player, "black_player": black_player, "ai_level": ai_level, "hint_level": hint_level}
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def load_sys_config():
    global bgm_on, sound_effect_on, show_time_on
    default = {"bgm":True, "effect":True, "showtime":False}
    if os.path.exists(SYS_SETTING_FILE):
        try:
            with open(SYS_SETTING_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            bgm_on = d.get("bgm", True)
            sound_effect_on = d.get("effect", True)
            show_time_on = d.get("showtime", False)
        except:
            bgm_on = True; sound_effect_on = True; show_time_on = False
    else:
        bgm_on = True; sound_effect_on = True; show_time_on = False

def save_sys_config():
    d = {"bgm":bgm_on, "effect":sound_effect_on, "showtime":show_time_on}
    with open(SYS_SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

load_config()
load_sys_config()
if bgm and bgm_on:
    bgm.loop = True
    bgm.play()

LEVEL_DELAY = {"初级": 0.3, "中级": 0.7, "高级": 1.2}
LEVEL_DEPTH = {"初级": 2, "中级": 3, "高级": 4}
LEVEL_RANDOM = {"初级": 0.30, "中级": 0.08, "高级": 0.00}

# ===================== 象棋核心规则函数（完全原样复制，无修改） =====================
def find_king(b, is_red):
    target = 'K' if is_red else 'k'
    for r in range(10):
        for c in range(9):
            if b[r][c] == target: return (r,c)
    return None

def king_face_to_face(b):
    kr_red, kc_red = find_king(b, True)
    kr_black, kc_black = find_king(b, False)
    if kr_red is None or kr_black is None: return False
    if kc_red != kc_black: return False
    min_r = min(kr_red, kr_black); max_r = max(kr_red, kr_black)
    for r in range(min_r + 1, max_r):
        if b[r][kc_red] != 0: return False
    return True

def get_raw_moves(b, r, c):
    moves = []
    piece = b[r][c]
    if piece == 0: return moves
    is_red = piece.isupper()
    p = piece.upper()

    if p == 'N':
        dirs = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        block = [(-1,0),(-1,0),(0,-1),(0,1),(0,-1),(0,1),(1,0),(1,0)]
        for i, (dr, dc) in enumerate(dirs):
            br, bc = r + block[i][0], c + block[i][1]
            if 0 <= br < 10 and 0 <= bc < 9 and b[br][bc] != 0: continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 10 and 0 <= nc < 9:
                target = b[nr][nc]
                if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
    elif p == 'R':
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 10 and 0 <= nc < 9:
                target = b[nr][nc]
                if target == 0: moves.append((nr, nc))
                else:
                    if target.isupper() != is_red: moves.append((nr, nc))
                    break
                nr += dr; nc += dc
    elif p == 'C':
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            jumped = False
            while 0 <= nr < 10 and 0 <= nc < 9:
                target = b[nr][nc]
                if not jumped:
                    if target == 0: moves.append((nr, nc))
                    else: jumped = True
                else:
                    if target != 0:
                        if target.isupper() != is_red: moves.append((nr, nc))
                        break
                nr += dr; nc += dc
    elif p == 'P':
        if is_red:
            dirs = [(-1,0)]
            if r <= 4: dirs += [(0,-1),(0,1)]
        else:
            dirs = [(1,0)]
            if r >= 5: dirs += [(0,-1),(0,1)]
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 10 and 0 <= nc < 9:
                target = b[nr][nc]
                if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
    elif p == 'A':
        dirs = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not (3 <= nc <= 5): continue
            if is_red:
                if 7 <= nr <= 9:
                    target = b[nr][nc]
                    if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
            else:
                if 0 <= nr <= 2:
                    target = b[nr][nc]
                    if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
    elif p == 'B':
        dirs = [(-2,-2),(-2,2),(2,-2),(2,2)]
        block = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for i, (dr, dc) in enumerate(dirs):
            br, bc = r + block[i][0], c + block[i][1]
            if not (0 <= br <10 and 0 <= bc <9): continue
            if b[br][bc] != 0: continue
            nr, nc = r + dr, c + dc
            if not (0 <= nr <10 and 0 <= nc <9): continue
            if is_red:
                if nr < 5: continue
            else:
                if nr > 4: continue
            target = b[nr][nc]
            if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
    elif p == 'K':
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not (3 <= nc <=5): continue
            if is_red:
                if 7 <= nr <=9:
                    target = b[nr][nc]
                    if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
            else:
                if 0 <= nr <=2:
                    target = b[nr][nc]
                    if target == 0 or (target.isupper() != is_red): moves.append((nr, nc))
    return moves

def is_checked(b, is_red):
    if king_face_to_face(b): return True
    kr, kc = find_king(b, is_red)
    if kr is None: return True
    for r in range(10):
        for c in range(9):
            piece = b[r][c]
            if piece == 0 or piece.isupper() == is_red: continue
            mvs = get_raw_moves(b, r, c)
            if (kr, kc) in mvs: return True
    return False

def get_valid_moves(b, r, c):
    piece = b[r][c]
    if piece == 0: return []
    is_red = piece.isupper()
    valid = []
    for (nr, nc) in get_raw_moves(b, r, c):
        cap = b[nr][nc]
        b[nr][nc] = piece; b[r][c] = 0
        checked = is_checked(b, is_red)
        b[r][c] = piece; b[nr][nc] = cap
        if not checked: valid.append((nr, nc))
    return valid

def has_any_valid_move(b, is_red):
    for r in range(10):
        for c in range(9):
            piece = b[r][c]
            if piece == 0 or piece.isupper() != is_red: continue
            if len(get_valid_moves(b, r, c)) > 0: return True
    return False

def is_checkmate(b, is_red):
    if not is_checked(b, is_red): return False
    return not has_any_valid_move(b, is_red)

def is_stalemate(b, is_red):
    if is_checked(b, is_red): return False
    return not has_any_valid_move(b, is_red)

def evaluate_board(b):
    score = 0
    for r in range(10):
        for c in range(9):
            p = b[r][c]
            if p == 0: continue
            base = PIECE_VALUE[p]
            pst = PST.get(p.upper())
            pos_val = 0
            if pst is not None: pos_val = pst[r][c] if p.isupper() else pst[9 - r][c]
            if p.isupper(): score += base + pos_val
            else: score -= base + pos_val
    return score

def generate_all_valid(b, is_red):
    all_moves = []
    for r in range(10):
        for c in range(9):
            p = b[r][c]
            if p == 0 or p.isupper() != is_red: continue
            for (nr, nc) in get_valid_moves(b, r, c):
                all_moves.append(((r,c), (nr, nc)))
    return all_moves

def _move_score(b, m):
    (fr, fc), (tr, tc) = m
    victim = b[tr][tc]
    if victim == 0: return 0
    return PIECE_VALUE[victim] * 10 - PIECE_VALUE[b[fr][fc]]

def generate_captures(b, is_red):
    caps = []
    for r in range(10):
        for c in range(9):
            p = b[r][c]
            if p == 0 or p.isupper() != is_red: continue
            for (nr, nc) in get_valid_moves(b, r, c):
                if b[nr][nc] != 0: caps.append(((r, c), (nr, nc)))
    return caps

def quiescence(b, alpha, beta, max_player, qdepth=0):
    if qdepth > 4: return evaluate_board(b)
    stand = evaluate_board(b)
    if max_player:
        if stand >= beta: return beta
        if stand > alpha: alpha = stand
    else:
        if stand <= alpha: return alpha
        if stand < beta: beta = stand
    moves = generate_captures(b, max_player)
    if not moves: return stand
    moves.sort(key=lambda m: _move_score(b, m), reverse=True)
    if max_player:
        for (fr, fc), (tr, tc) in moves:
            cap = b[tr][tc]
            b[tr][tc] = b[fr][fc]; b[fr][fc] = 0
            val = quiescence(b, alpha, beta, False, qdepth + 1)
            b[fr][fc] = b[tr][tc]; b[tr][tc] = cap
            if val >= beta: return beta
            if val > alpha: alpha = val
        return alpha
    else:
        for (fr, fc), (tr, tc) in moves:
            cap = b[tr][tc]
            b[tr][tc] = b[fr][fc]; b[fr][fc] = 0
            val = quiescence(b, alpha, beta, True, qdepth + 1)
            b[fr][fc] = b[tr][tc]; b[tr][tc] = cap
            if val <= alpha: return alpha
            if val < beta: beta = val
        return beta

def minimax(b, depth, alpha, beta, max_player):
    if depth == 0: return quiescence(b, alpha, beta, max_player), None
    is_red = max_player
    moves = generate_all_valid(b, is_red)
    if not moves:
        if is_checked(b, is_red): return (-100000 if max_player else 100000), None
        return 0, None
    moves.sort(key=lambda m: _move_score(b, m), reverse=True)
    best_move = None
    if max_player:
        max_val = -999999
        for (fr, fc), (tr, tc) in moves:
            cap = b[tr][tc]
            b[tr][tc] = b[fr][fc]; b[fr][fc] = 0
            val, _ = minimax(b, depth - 1, alpha, beta, False)
            b[fr][fc] = b[tr][tc]; b[tr][tc] = cap
            if val > max_val: max_val = val; best_move = ((fr, fc), (tr, tc))
            if val > alpha: alpha = val
            if beta <= alpha: break
        return max_val, best_move
    else:
        min_val = 999999
        for (fr, fc), (tr, tc) in moves:
            cap = b[tr][tc]
            b[tr][tc] = b[fr][fc]; b[fr][fc] = 0
            val, _ = minimax(b, depth - 1, alpha, beta, True)
            b[fr][fc] = b[tr][tc]; b[tr][tc] = cap
            if val < min_val: min_val = val; best_move = ((fr, fc), (tr, tc))
            if val < beta: beta = val
            if beta <= alpha: break
        return min_val, best_move

def ai_calc_thread(board_in, is_red_in, level_in, out_dict):
    d = LEVEL_DEPTH[level_in]
    score, move = minimax(board_in, d, -999999, 999999, is_red_in)
    all_mv = generate_all_valid(board_in, is_red_in)
    if not all_mv: res = None
    elif move is None: res = random.choice(all_mv)
    else: res = move
    if all_mv and random.random() < LEVEL_RANDOM[level_in]: res = random.choice(all_mv)
    out_dict["move"] = res
    out_dict["done"] = True

def board_to_tuple(b):
    return tuple(tuple(row) for row in b)

def save_log_to_file(current_log):
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_FOLDER, f"{now_str}.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(current_log, f, ensure_ascii=False, indent=2)
    return now_str

# ===================== Kivy 棋盘控件 =====================
class ChessBoardWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.BLOCK = 58
        self.OFFSET_X = 25
        self.OFFSET_Y = 25
        self.board = deepcopy(EMPTY_BOARD)
        self.turn_red = True
        self.select_pos = None
        self.valid_points = []
        self.game_over = False
        self.win_text = ""
        self.current_log = []
        self.history_stack = []
        self.in_game = False
        self.flip_board = False
        self.is_challenge_mode = False
        self.current_level_id = 1
        self.player_step_count = 0
        self.level_target_steps = 0
        self.ai_wait = False
        self.ai_result = {"done":False, "move":None}
        self.bind(size=self.draw_board)

    def reset_game(self):
        self.is_challenge_mode = False
        self.board = deepcopy(START_BOARD)
        self.turn_red = True
        self.select_pos = None
        self.valid_points = []
        self.game_over = False
        self.win_text = ""
        self.current_log = []
        self.history_stack = []
        self.in_game = True
        self.ai_wait = False
        self.ai_result = {"done":False, "move":None}
        if turn_red and red_player == "电脑":
            self.run_ai()
        self.draw_board()

    def start_challenge(self, level_id):
        if level_id not in LEVELS:
            return
        self.is_challenge_mode = True
        self.current_level_id = level_id
        self.player_step_count = 0
        self.level_target_steps = LEVELS[level_id]["steps"]
        self.board = deepcopy(LEVELS[level_id]["board"])
        self.turn_red = True
        self.select_pos = None
        self.valid_points = []
        self.game_over = False
        self.win_text = ""
        self.current_log = []
        self.history_stack = []
        self.in_game = True
        self.ai_wait = False
        self.ai_result = {"done":False, "move":None}
        self.draw_board()

    def undo_move(self):
        if self.is_challenge_mode:
            return
        is_ai_game = (red_player == "电脑") or (black_player == "电脑")
        if is_ai_game:
            if len(self.history_stack) >= 2:
                self.history_stack.pop()
                state = self.history_stack.pop()
                self.current_log.pop()
                self.current_log.pop()
            else:
                return
        else:
            if len(self.history_stack) >= 1:
                state = self.history_stack.pop()
                self.current_log.pop()
            else:
                return
        self.board = deepcopy(state["board"])
        self.turn_red = state["turn_red"]
        self.game_over = state["game_over"]
        self.win_text = state["win_text"]
        self.select_pos = None
        self.valid_points = []
        self.draw_board()

    def run_ai(self):
        self.ai_result = {"done":False, "move":None}
        t = threading.Thread(target=ai_calc_thread, args=(deepcopy(self.board), self.turn_red, ai_level, self.ai_result), daemon=True)
        t.start()
        Clock.schedule_interval(self.check_ai, 0.2)

    @mainthread
    def check_ai(self, dt):
        if self.ai_result["done"]:
            Clock.unschedule(self.check_ai)
            mv = self.ai_result["move"]
            if mv is not None:
                self.auto_execute_move(mv)
            self.ai_wait = False

    def auto_execute_move(self, mv):
        (fr,fc), (tr,tc) = mv
        self.history_stack.append({"board":deepcopy(self.board), "turn_red":self.turn_red, "game_over":self.game_over, "win_text":self.win_text})
        nb = deepcopy(self.board)
        captured = nb[tr][tc] != 0
        nb[tr][tc] = nb[fr][fc]
        nb[fr][fc] = 0
        new_turn = not self.turn_red
        new_state = board_to_tuple(nb)
        step_data = {"state": new_state, "from": (fr, fc), "to": (tr, tc), "capture": captured, "next_turn_red": new_turn}
        self.current_log.append(step_data)
        if sound_effect_on and luozi_sound:
            luozi_sound.play()
        count = 0
        for st in self.current_log:
            if st["state"] == new_state and st["next_turn_red"] == new_turn:
                count += 1
        REPEAT_LIMIT = 26
        if count >= REPEAT_LIMIT:
            self.game_over = True
            self.win_text = "游戏结束"
        else:
            self.board = nb
            self.turn_red = new_turn
            if self.is_challenge_mode and not self.turn_red:
                self.player_step_count += 1
                if self.player_step_count > self.level_target_steps:
                    self.game_over = True
                    self.win_text = "游戏结束"
                    if sound_effect_on and jiangjun_sound:
                        jiangjun_sound.play()
            if not self.game_over:
                if is_checkmate(self.board, self.turn_red):
                    self.game_over = True
                    self.win_text = "游戏结束"
                elif is_stalemate(self.board, self.turn_red):
                    self.game_over = True
                    self.win_text = "游戏结束"
                elif is_checked(self.board, self.turn_red):
                    if sound_effect_on and jiangjun_sound:
                        jiangjun_sound.play()
        self.select_pos = None
        self.valid_points = []
        if not self.game_over:
            current_player = red_player if self.turn_red else black_player
            if self.is_challenge_mode:
                current_player = "电脑" if not self.turn_red else "棋手"
            if current_player == "电脑":
                self.ai_wait = True
                self.run_ai()
        self.draw_board()

    def on_touch_down(self, touch):
        if not self.in_game or self.game_over:
            return super().on_touch_down(touch)
        pos = self.pos_from_touch(touch.x, touch.y)
        if pos is None:
            self.select_pos = None
            self.valid_points = []
            self.draw_board()
            return super().on_touch_down(touch)
        cr, cc = pos
        if self.select_pos is None:
            p = self.board[cr][cc]
            if p == 0:
                return True
            is_p_red = p.isupper()
            if (is_p_red and not self.turn_red) or (not is_p_red and self.turn_red):
                return True
            if self.is_challenge_mode:
                if not is_p_red:
                    return True
            else:
                current_player = red_player if self.turn_red else black_player
                if current_player == "电脑":
                    return True
            self.select_pos = (cr, cc)
            self.valid_points = get_valid_moves(self.board, cr, cc)
        else:
            sr, sc = self.select_pos
            if (cr, cc) in self.valid_points:
                self.auto_execute_move(((sr, sc), (cr, cc)))
            self.select_pos = None
            self.valid_points = []
        self.draw_board()
        return True

    def pos_from_touch(self, mx, my):
        for r in range(10):
            for c in range(9):
                dr, dc = (9 - r, 8 - c) if self.flip_board else (r, c)
                x = self.OFFSET_X + dc * self.BLOCK
                y = self.OFFSET_Y + dr * self.BLOCK
                if (mx - x)**2 + (my - y)**2 < 24**2:
                    return (r,c)
        return None

    def draw_board(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.94, 0.83, 0.63, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.27,0.14,0.0,1)
            # 横线
            for i in range(10):
                y = self.OFFSET_Y + i * self.BLOCK
                Line(points=[self.OFFSET_X, y, self.OFFSET_X + 8 * self.BLOCK, y], width=2)
            bottom_y = self.OFFSET_Y + 9 * self.BLOCK
            # 竖线，河界断开
            for j in range(9):
                x = self.OFFSET_X + j * self.BLOCK
                if j ==0 or j ==8:
                    Line(points=[x, self.OFFSET_Y, x, bottom_y], width=2)
                else:
                    Line(points=[x, self.OFFSET_Y, x, self.OFFSET_Y + 4 * self.BLOCK], width=2)
                    Line(points=[x, self.OFFSET_Y + 5 * self.BLOCK, x, bottom_y], width=2)
            # 九宫斜线
            Line(points=[self.OFFSET_X+3*self.BLOCK, self.OFFSET_Y, self.OFFSET_X+5*self.BLOCK, self.OFFSET_Y+2*self.BLOCK], width=2)
            Line(points=[self.OFFSET_X+5*self.BLOCK, self.OFFSET_Y, self.OFFSET_X+3*self.BLOCK, self.OFFSET_Y+2*self.BLOCK], width=2)
            Line(points=[self.OFFSET_X+3*self.BLOCK, self.OFFSET_Y+7*self.BLOCK, self.OFFSET_X+5*self.BLOCK, self.OFFSET_Y+9*self.BLOCK], width=2)
            Line(points=[self.OFFSET_X+5*self.BLOCK, self.OFFSET_Y+7*self.BLOCK, self.OFFSET_X+3*self.BLOCK, self.OFFSET_Y+9*self.BLOCK], width=2)
            # 楚河汉界文字
            Color(0.27,0.14,0.0,1)
            from kivy.uix.label import Label
            river_y = self.OFFSET_Y + 4.5 * self.BLOCK
            # 可行点绿色小圆点
            Color(0,0.8,0,1)
            for (r,c) in self.valid_points:
                dr, dc = (9 - r, 8 - c) if self.flip_board else (r,c)
                x = self.OFFSET_X + dc * self.BLOCK
                y = self.OFFSET_Y + dr * self.BLOCK
                Ellipse(pos=(x-8, y-8), size=(16,16))
            # 棋子
            for r in range(10):
                for c in range(9):
                    piece = self.board[r][c]
                    if piece == 0: continue
                    dr, dc = (9 - r, 8 - c) if self.flip_board else (r,c)
                    x = self.OFFSET_X + dc * self.BLOCK
                    y = self.OFFSET_Y + dr * self.BLOCK
                    Color(1,1,1,1)
                    Ellipse(pos=(x-24, y-24), size=(48,48))
                    Color(0.27,0.14,0.0,1)
                    Ellipse(pos=(x-24, y-24), size=(48,48), width=2)
                    # 棋子文字
                    lbl = Label(text=name_map[piece], font_size=32, color=(1,0,0,1) if piece.isupper() else (0,0,0,1))
                    lbl.texture_update()
                    self.canvas.before.add(Rectangle(texture=lbl.texture, pos=(x - lbl.texture_size[0]/2, y - lbl.texture_size[1]/2), size=lbl.texture_size))
            # 选中圈绿色外环
            if self.select_pos is not None:
                sr, sc = self.select_pos
                dr, dc = (9 - sr, 8 - sc) if self.flip_board else (sr, sc)
                x = self.OFFSET_X + dc * self.BLOCK
                y = self.OFFSET_Y + dr * self.BLOCK
                Color(0,0.8,0,1)
                Line(circle=(x,y,28), width=3)

# ===================== 主界面布局 =====================
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.chess = ChessBoardWidget(size_hint_y=0.85)
        self.add_widget(self.chess)
        btn_box = BoxLayout(size_hint_y=0.15, spacing=5, padding=5)
        btn_names = ["新局","设置","悔棋","菜单","提示","主页"]
        for bn in btn_names:
            btn = Button(text=bn, font_size=18)
            btn.bind(on_press=self.on_btn_press)
            btn_box.add_widget(btn)
        self.add_widget(btn_box)

    def on_btn_press(self, btn):
        txt = btn.text
        if txt == "新局":
            self.chess.reset_game()
        elif txt == "悔棋":
            self.chess.undo_move()
        elif txt == "设置":
            popup = SettingPopup(self.chess)
            popup.open()
        elif txt == "主页":
            self.chess.in_game = False

class SettingPopup(Popup):
    def __init__(self, chess_widget, **kwargs):
        super().__init__(title="对局设置", size_hint=(0.85,0.75), **kwargs)
        self.chess = chess_widget
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.red_btn = Button(text=red_player)
        self.black_btn = Button(text=black_player)
        self.ai_btn = Button(text=ai_level)
        self.hint_btn = Button(text=hint_level)
        ok_btn = Button(text="确定")
        cancel_btn = Button(text="取消")
        self.red_btn.bind(on_press=lambda x: self.toggle_player(self.red_btn))
        self.black_btn.bind(on_press=lambda x: self.toggle_player(self.black_btn))
        self.ai_btn.bind(on_press=lambda x: self.toggle_level(self.ai_btn))
        self.hint_btn.bind(on_press=lambda x: self.toggle_level(self.hint_btn))
        ok_btn.bind(on_press=self.save_setting)
        cancel_btn.bind(on_press=self.dismiss)
        box.add_widget(Label(text="红方"))
        box.add_widget(self.red_btn)
        box.add_widget(Label(text="黑方"))
        box.add_widget(self.black_btn)
        box.add_widget(Label(text="AI等级"))
        box.add_widget(self.ai_btn)
        box.add_widget(Label(text="提示等级"))
        box.add_widget(self.hint_btn)
        box.add_widget(BoxLayout(size_hint_y=0.15, spacing=10, children=[ok_btn, cancel_btn]))
        self.content = box

    def toggle_player(self, btn):
        if btn.text == "棋手":
            btn.text = "电脑"
        else:
            btn.text = "棋手"

    def toggle_level(self, btn):
        if btn.text == "初级":
            btn.text = "中级"
        elif btn.text == "中级":
            btn.text = "高级"
        else:
            btn.text = "初级"

    def save_setting(self, *args):
        global red_player, black_player, ai_level, hint_level
        red_player = self.red_btn.text
        black_player = self.black_btn.text
        ai_level = self.ai_btn.text
        hint_level = self.hint_btn.text
        save_config()
        self.dismiss()

# ===================== APP入口 =====================
class XiangqiApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    XiangqiApp().run()
