import random

VO_LIST = ['o', 'n', 'm', 'u', 'a', 'r', 'y']
CHA_LIST = ['k', 'b', 'ay', 'or', 'nr', 'o', 'n', 'am', 'amu', 'ny', 'mru', 'ru', 'aoy', 'any', 'amou', 'mruy', 'ory', 'nor', 'mny', 'mnuy', 'nou', 'mnou', 'amr', 'amru', 'amno', 'anou', 'amnou', 'amnru', 'aouy', 'amouy', 'anry', 'mnouy', 'anor', 'aory', 'mnry', 'nruy', 'mnruy']
ELEMENTS = {'反': ['k', []], '+': ['b', []], '始': ['ay', []], '中': ['or', []], '時': ['nr', []], '→': [1, []], '←': [1, []], '善悪': [3, []], '何': [3, []], '相環': [2, []], '赤色': ['', []], '青色': ['', []], '緑色': ['', []], '三態': [2, []], '我為': ['', []], '他為': ['', []], '神為': ['', []], '形': ['', []], '大きさ': ['', []], '固さ': ['', []], '距離': ['', []], '数': ['', []], '&': [2, []]}
CODE_TO_LINE = {"a": (0, 1), "o": (3, 4), "m": (1, 2), "u": (2, 4), "n": (0, 3), "r": (0, 4), "y": (1, 3), "k": (0, 2), "b": (0, 0), "t": (2, 3)}
ATTR_DIC = {'+': ['助詞'], '-': ['助詞'], '中': ['助詞'], '⇔': ['方向', '両', []], '→': ['方向', '右', []], '←': ['方向', '左', []], '&': ['加詞'], '相環': ['状態詞', '色', []], '赤色': ['形容詞', '色'], '青色': ['形容詞', '色'], '緑色': ['形容詞', '色'], '白色': ['形容詞', '色'], '黒色': ['形容詞', '色'], '水色': ['形容詞', '色'], '黄色': ['形容詞', '色'], '紫色': ['形容詞', '色'], '数': ['状態詞', '数', []], '1': ['形容詞', '数'], '2': ['形容詞', '数'], '3': ['形容詞', '数'], '4': ['形容詞', '数'], '5': ['形容詞', '数'], '6': ['形容詞', '数'], '7': ['形容詞', '数'], '我為': ['名詞', '三態', [], []], '他為': ['名詞', '三態', [], []], '神為': ['名詞', '三態', [], []], '三態': ['状態詞', '三態', []], '形': ['状態詞', '形', []], '大きさ': ['状態詞', '形容', []], '固さ': ['状態詞', '形容', []], '距離': ['状態詞', '形容', []], '時': ['状態詞', '形容', []], '善悪': ['状態詞', '善悪', []], '得る': ['動詞', '一般', []], '失う': ['動詞', '一般', []], '創る': ['動詞', '一般', []], '壊す': ['動詞', '一般', []], '組む': ['動詞', '一般', []], 'ほどく': ['動詞', '一般', []], '近づく': ['動詞', '一般', []], '近づける': ['動詞', '一般', []], '遠ざかる': ['動詞', '一般', []], '遠ざける': ['動詞', '一般', []], '生': ['動詞', '一般', []], '死': ['動詞', '一般', []], '何': ['疑問詞', '何'], '始': ['形容詞', '時'], '終': ['形容詞', '時']}

def generate_initial_dictionary():
    """初期辞書データを生成して辞書形式で返す"""
    word_list = []
    generated_ele = {}

    for key, val in ELEMENTS.items():
        constraint, extra = val
        while True:
            word = ''.join(sorted(random.sample(VO_LIST, constraint))) if isinstance(constraint, int) else (constraint if constraint != '' else ''.join(sorted(random.sample(VO_LIST, random.randint(3, 5)))))
            if word not in word_list and word in CHA_LIST:
                if "為" in key and not all(e in word for e in generated_ele["三態"][0]): continue
                if "色" in key and not all(e in word for e in generated_ele["相環"][0]): continue
                word_list.append(word)
                generated_ele[key] = [word, extra]
                break

    d = generated_ele
    def word_merge(a, b): return [a[0] + b[0], a[1] + b[1]]
    
    dic_main = {'終': word_merge(d['始'], d['反']), '⇔': word_merge(d['→'], d['←']), '遠ざける': word_merge(d['距離'], d['+']), '-': d['反'], '近づく': word_merge(d['距離'], d['反']), '得る': word_merge(d['形'], d['+']), '死': word_merge(d['時'], d['+']), '創る': word_merge(d['大きさ'], d['+']), '組む': word_merge(d['固さ'], d['+'])}
    dic_main.update(d)
    dic_main.update({'失う': word_merge(dic_main['得る'], dic_main['反']), '生': word_merge(dic_main['死'], dic_main['反']), '壊す': word_merge(dic_main['創る'], dic_main['反']), 'ほどく': word_merge(dic_main['組む'], dic_main['反']), '近づける': word_merge(dic_main['近づく'], dic_main['反']), '遠ざかる': word_merge(dic_main['遠ざける'], dic_main['反'])})
    dic_main.update({'1': dic_main['始'], '2': word_merge(dic_main['始'], dic_main['+']), '3': word_merge(dic_main['中'], dic_main['-']), '4': dic_main['中'], '5': word_merge(dic_main['中'], dic_main['+']), '6': dic_main['終'], '7': word_merge(dic_main['終'], dic_main['+']), '白色': dic_main['始'], '黒色': dic_main['終'], '水色': word_merge(dic_main['赤色'], dic_main['反']), '黄色': word_merge(dic_main['青色'], dic_main['反']), '紫色': word_merge(dic_main['緑色'], dic_main['反'])})

    original_dic = {k: v + [dic_main[k]] for k, v in ATTR_DIC.items()}
    translation_map = {
        '始': 'Begin', '中': 'Middle', '終': 'End', '反': 'Reverse', '時': 'Time',
        '距離': 'Range', '大きさ': 'Size', '固さ': 'Hard', '形': 'Shape',
        '得る': 'Gain', '失う': 'Lose', '創る': 'Build', '壊す': 'Break',
        '組む': 'Join', 'ほどく': 'Split', '近づく': 'Near',
        '近づける': 'Pull', '遠ざかる': 'Away', '遠ざける': 'Push',
        '何': 'What', '相環': 'Cycle', '三態': 'Agents', '我為': "Self-by",
        '他為': "Other-by", '神為': "God-by", '数': 'Number',
        '赤色': 'Red', '青色': 'Blue', '緑色': 'Green', '白色': 'White',
        '黒色': 'Black', '水色': 'Cyan', '黄色': 'Yellow', '紫色': 'Purple',
        '善悪': 'Ethic'
    }

    master_dic = {}
    for key, value in original_dic.items():
        if key in ["生", "死"]: continue
        word_str = value[-1][0]
        route_coords = tuple(sorted(list({CODE_TO_LINE[char] for char in word_str})))
        if route_coords in master_dic:
            master_dic[route_coords][0] += "\n" + key
        else:
            master_dic[route_coords] = [key, True]
        if value[0] == "状態詞" and key not in ["相環", "三態", "数"]:
            for suffix, sym in [("+", "+"), ("-", "-")]:
                w = word_str + original_dic[sym][-1][0]
                suffix_coords = tuple(sorted(list({CODE_TO_LINE[c] for c in w})))
                if suffix_coords in master_dic:
                    master_dic[suffix_coords][0] += "\n" + key + suffix
                else:
                    master_dic[suffix_coords] = [key + suffix, True]
    
    # --- ここから英訳版作成ロジック ---
    master_en_dic = {}
    for coords, val in master_dic.items():
        content = val[0]
        en_lines = []
        for line in content.split("\n"):
            translated = line
            for jp, en in translation_map.items():
                if jp in line:
                    translated = line.replace(jp, en)
                    break
            en_lines.append(translated)
        
        master_en_dic[coords] = ["\n".join(en_lines), val[1]]
    return {'original': original_dic, 'master': master_dic, 'master_en': master_en_dic,'user': {}, 'save': {}}