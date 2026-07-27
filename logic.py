import os
import pickle
import numpy as np
import random
from itertools import combinations
from collections import defaultdict

# 設定クラスへのアクセスを仮定
from config import Config 

# -----------------------------
# アイテム特定アルゴリズム
# -----------------------------
def is_specific_condition(condition_set, P, N):
    if not condition_set:
        return False

    # 1. Positive Check (P内のすべてのアイテムがこの条件を満たすか)
    for status_p in P:
        if not all(status_p.get(s) == v for s, v in condition_set.items()):
            return False 

    # 2. Negative Check (N内のどのアイテムもこの条件を満たさないか)
    for status_n in N:
        if all(status_n.get(s) == v for s, v in condition_set.items()):
            return False 

    return True

def find_all_non_redundant_specific_conditions(item_list):
    if not item_list:
        return {}

    grouped_items = defaultdict(list)
    for item in item_list:
        grouped_items[item['name']].append(item['status'])
    
    unique_names = list(grouped_items.keys())
    
    all_statuses_keys = set()
    for item in item_list:
        all_statuses_keys.update(k for k, v in item['status'].items() if v is not None)
    all_statuses_keys = sorted(list(all_statuses_keys))

    final_results = {}

    for target_name in unique_names:
        P = grouped_items[target_name]
        N = [status for name, statuses in grouped_items.items() 
             for status in statuses if name != target_name]

        all_specific_sets = []
        max_k = len(all_statuses_keys)
        
        for k in range(1, max_k + 1):
            for status_combination in combinations(all_statuses_keys, k):
                representative_conditions = set()
                for status_p in P:
                    current_dict = {s: status_p.get(s) for s in status_combination 
                                    if status_p.get(s) is not None}
                    
                    if len(current_dict) == k:
                        representative_conditions.add(frozenset(current_dict.items()))
                
                for condition_frozenset in representative_conditions:
                    condition_set = dict(condition_frozenset)

                    if is_specific_condition(condition_set, P, N):
                        all_specific_sets.append(condition_set)

        non_redundant_sets = []
        
        for i, current_set in enumerate(all_specific_sets):
            is_redundant = False
            current_keys = list(current_set.keys())
            
            for sub_k in range(1, len(current_set)):
                for sub_keys in combinations(current_keys, sub_k):
                    subset_condition = {k: current_set[k] for k in sub_keys}
                    
                    if is_specific_condition(subset_condition, P, N):
                        is_redundant = True
                        break
                if is_redundant:
                    break
            
            if not is_redundant:
                non_redundant_sets.append(current_set)

        final_results[target_name] = non_redundant_sets

    return final_results

# -----------------------------
# 言語・パターン管理クラス
# -----------------------------
class WordManager:
    def __init__(self, dots, difficulty, language):
        self.dots = dots
        self.code_to_line = {
            "a": [(0, 1)], "o": [(3, 4)], "m": [(1, 2)],
            "u": [(2, 4)], "n": [(0, 3)], "r": [(0, 4)],
            "y": [(1, 3)], "k": [(0, 2)], "b": [(0, 0)],
            "t": [(2, 3)]
        }
        all_data = self._load_pickle(Config.DIC_PATH, default={})
        self.dictionary = all_data.get('original', {})
        self.user_dic_path = Config.DIC_PATH
        if difficulty in ["Bachelor", "Master"]:
            raw_user_dic = all_data.get('user', {})
            self.save_key = 'user'
        elif language == "JP":
            raw_user_dic = all_data.get('master', {})
            self.save_key = 'master'
        else:
            raw_user_dic = all_data.get('master_en', {})
            self.save_key = 'master_en'
        self.user_dictionary = {}
        for key, value in raw_user_dic.items():
            if isinstance(value, str):
                self.user_dictionary[key] = [value, False]
            else:
                self.user_dictionary[key] = value

    def _initial_load(self, path):
        if not os.path.exists(path):
            return {'original': {}, 'master': None, 'master_en': None, 'user': None}
        with open(path, "rb") as f:
            return pickle.load(f)

    def _load_pickle(self, path, default, is_user_dic=False):
        if not os.path.exists(path):
            if path == getattr(self, 'user_dic_path', None):
                with open(path, "wb") as f:
                    pickle.dump(default, f)
            return default
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                
                if is_user_dic:
                    new_data = {}
                    for key, value in data.items():
                        if isinstance(value, str):
                            new_data[key] = [value, False]
                        else:
                            new_data[key] = value
                    return new_data

                return data
        except:
            return default

    def save_user_dic(self):
        current_data = self._load_pickle(self.user_dic_path, default={})
        current_data[self.save_key] = self.user_dictionary
        with open(self.user_dic_path, "wb") as f:
            pickle.dump(current_data, f)

    def judge_sentence(self, words_list):
        parts = []
        for w in words_list:
            if w in self.dictionary:
                parts.append([w] + self.dictionary[w])
            else:
                parts.append([w, '不明'])
        
        changed = True
        while changed:
            changed = False
            i = 0
            while i < len(parts) - 1:
                if parts[i][1] == '形容詞' and parts[i+1][1] == '名詞':
                    if parts[i][2] not in parts[i+1][4]:
                        parts[i+1][4].append(parts[i][2])
                        parts[i+1][3].append(parts[i][0])
                    parts.pop(i)
                    changed = True
                    break
                elif parts[i][1] == '名詞' and parts[i+1][1] == '程度詞':
                    if parts[i+1][2] not in parts[i][4]:
                        parts[i][4].append(parts[i+1][2])
                        parts[i][3].append(parts[i+1][0])
                    parts.pop(i+1)
                    changed = True
                    break
                elif parts[i][1] == '状態詞' and parts[i+1][1] == '助詞':
                    new = [parts[i+1][0], '程度詞', parts[i][0]]
                    parts = parts[:i] + [new] + parts[i+2:]
                    changed = True
                    break
                i += 1

        i = 0
        while i < len(parts) - 2:
            if parts[i][1] == '名詞' and parts[i+1][1] == '加詞' and parts[i+2][1] == '名詞':
                new = [
                    [parts[i][0], parts[i+2][0]],
                    '名詞',
                    [parts[i][2], parts[i+2][2]],
                    [parts[i][3], parts[i+2][3]]
                ]
                parts = parts[:i] + [new] + parts[i+3:]
            else:
                i += 1

        pattern = [x[1] for x in parts]
        if pattern == ['疑問詞', '状態詞', '名詞']:
            return '疑問文1'
        elif len(pattern) == 3 and pattern[:2] == ['疑問詞', '方向'] and pattern[2] in ['名詞', '形容詞', '状態詞']:
            return '疑問文2'
        elif pattern == ['名詞', '動詞', '名詞']:
            return '通常文'
        else:
            return '不明'

    def find_eulerian_path(self, edges):
        """
        与えられた辺リストからオイラー路を計算する。
        一筆書きが不可能な場合は False を返す。
        """
        if not edges:
            return []

        adj = defaultdict(list)
        degree = defaultdict(int)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
            degree[u] += 1
            degree[v] += 1

        odd_nodes = [node for node, deg in degree.items() if deg % 2 != 0]
        
        if len(odd_nodes) not in (0, 2):
            return []

        start_node = odd_nodes[0] if odd_nodes else edges[0][0]

        curr_adj = {u: list(v) for u, v in adj.items()}
        temp_stack = [start_node]
        res_path = []

        while temp_stack:
            u = temp_stack[-1]
            if curr_adj.get(u):
                v = curr_adj[u].pop()
                if u in curr_adj[v]:
                    curr_adj[v].remove(u)
                temp_stack.append(v)
            else:
                res_path.append(temp_stack.pop())

        if len(res_path) != len(edges) + 1:
            return []

        return res_path[::-1]
    def random_point_in_dot(self, dot_rect):
        cx, cy = dot_rect.center
        r = random.uniform(0, Config.RADIUS)
        theta = random.uniform(0, 2 * np.pi)
        return cx + r * np.cos(theta), cy + r * np.sin(theta)

    def generate_random_pattern(self, sentence):
        words = []
        reserve = False
        reserve_word = ""
        reserve_code = ""

        for word in sentence[::-1]:
            entry = self.dictionary[word]
            code = entry[-1][0] if entry[-1] else ""
            if entry[0] == "助詞":
                reserve_word = word
                reserve_code = code
                reserve = True
                continue
            if reserve:
                code += reserve_code
                word += reserve_word
                reserve = False
            
            edge_set = set()
            for c in code:
                if c in self.code_to_line:
                    for e in self.code_to_line[c]:
                        edge_set.add(tuple(sorted(e)))

            if not edge_set:
                continue

            unique_edges = list(edge_set)
            path_vertices = self.find_eulerian_path(unique_edges)
            
            is_incomplete = (len(unique_edges) > 0 and not path_vertices)
            
            path = []
            if path_vertices:
                curr_pt = self.random_point_in_dot(self.dots[path_vertices[0]])
                path.append(curr_pt)
                
                last_vx, last_vy = 0, -1

                for i in range(1, len(path_vertices)):
                    prev_v = path_vertices[i-1]
                    curr_v = path_vertices[i]
                    
                    start_pt = path[-1]
                    end_pt = self.random_point_in_dot(self.dots[curr_v])

                    if prev_v == 0 and curr_v == 0:
                        x, y = start_pt
                        mag = 50
                        vx, vy = last_vx * mag, last_vy * mag
                        
                        path.append((x + vx, y + vy))
                        if abs(vx) > abs(vy):
                            path.append((x + vx + vy, y - vx + vy))
                            path.append((x + vy, y - vx))
                        else:
                            path.append((x + vx - vy, y + vx + vy))
                            path.append((x - vy, y + vx))
                        
                        path.append(end_pt)
                    else:
                        path.append(end_pt)
                    
                    dx = end_pt[0] - start_pt[0]
                    dy = end_pt[1] - start_pt[1]
                    dist = (dx**2 + dy**2)**0.5
                    if dist > 0:
                        last_vx, last_vy = dx/dist, dy/dist

            words.append({
                "word": word, 
                "path": path, 
                "used_lines": edge_set, 
                "is_incomplete": is_incomplete
            })
            
        return words[::-1]