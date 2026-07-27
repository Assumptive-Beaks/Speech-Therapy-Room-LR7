import event_data_source

class EventManager:
    """
    events.pickle からデータを読み込み、
    ゲーム内イベント（テキスト、パターンなど）を管理・実行するクラス。
    """
    def __init__(self, game_controller, ui_manager, word_manager, language="JP"):
        self.controller = game_controller
        self.ui_manager = ui_manager
        self.word_manager = word_manager
        
        self.event_queue = []            
        self.is_event_active = False     
        self.is_waiting_for_choice = False
        self.current_choices = []
        
        if language == "JP":
            self.event_database = event_data_source.event_data
        else:
            self.event_database = event_data_source.event_en_data

    def trigger_event(self, event_id):
        if event_id not in self.event_database:
            return

        events = self.event_database[event_id]
        for ev in events:
            new_ev = ev.copy()
            if new_ev["type"] == "text":
                new_ev["page_index"] = 0
                
            self.event_queue.append(new_ev)
        if not self.ui_manager.showing_text and self.event_queue:
            self.process_next_event()

    def update(self, dt):
        if self.ui_manager.showing_text:
            self.is_event_active = True
        else:
            if self.event_queue:
                self.process_next_event()
            else:
                self.is_event_active = False
            
    def process_next_event(self):
        if not self.event_queue:
            return

        event = self.event_queue[0] 

        if event["type"] == "text":
            self.ui_manager.set_message(event["content"][0])
            self.is_event_active = True

        elif event["type"] == "pattern":
            self._handle_pattern_event(event)
            self.event_queue.pop(0)
            if self.event_queue:
                self.process_next_event()

    def _handle_text_event(self, event):
        current_text = event["content"][event["page_index"]]
        self.ui_manager.set_message(current_text)
        self.is_event_active = True
            
    def next_text_page(self):
        if not self.event_queue or self.event_queue[0]["type"] != "text":
            return False

        event = self.event_queue[0]
        event["page_index"] += 1

        if event["page_index"] < len(event["content"]):
            next_text = event["content"][event["page_index"]]
            self.ui_manager.set_message(next_text)
            return True
        else:
            self.ui_manager.clear_message()
            self.event_queue.pop(0)
            self.is_event_active = False
            return False

    def _handle_pattern_event(self, event):
        sentence = event["content"]
        random_patterns = self.word_manager.generate_random_pattern(sentence)
        
        if self.controller.difficulty == "Master":
            dic_updated = False
            for pdata in random_patterns:
                lines = pdata.get('used_lines', [])
                normalized_edges = set()
                for u, v in lines:
                    normalized_edges.add(tuple(sorted((u, v))))
                key_tuple = tuple(sorted(list(normalized_edges)))
                if key_tuple not in self.word_manager.user_dictionary:
                    self.word_manager.user_dictionary[key_tuple] = ["?", False]
                    dic_updated = True
            
            if dic_updated:
                self.word_manager.save_user_dic()

        self.ui_manager.set_random_patterns(random_patterns)
        self.controller.next_voice = True
        
    def open_question(self, choices):
        """選択肢モードを開始"""
        self.is_waiting_for_choice = True
        self.current_choices = choices

    def close_question(self):
        """選択肢モードを終了"""
        self.is_waiting_for_choice = False
        self.current_choices = []