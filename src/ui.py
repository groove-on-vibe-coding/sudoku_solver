import pygame
import sys
import math
import time
from renderer import SudokuRenderer
from tkinter import Tk, filedialog
from datetime import datetime
from file_io import load_board_from_file
import os
from lang_manager import get_text, get_language_manager


class SudokuUI:
    def __init__(self, game):
        self.game = game
        self.ui_config = game.ui_config
        
        # 言語設定を取得
        self.language = self.ui_config.get("language", "ja")
        # 言語マネージャーは既に初期化されているため、再初期化は不要
        # get_language_manager(self.language)
        
        # ゲームのイベントリスナーを設定
        self._setup_event_listeners()
        
        # ウィンドウ設定
        self.window = pygame.display.set_mode((
            self.ui_config['window']['width'],
            self.ui_config['window']['height']
        ))
        pygame.display.set_caption(get_text("ui", "window_title"))
        self.clock = pygame.time.Clock()
        
        # レンダラー
        self.renderer = SudokuRenderer(self.window, game.board, self.ui_config)
        
        # ボタン
        self.buttons = {}
        self.add_buttons()
        self.hovered_button = None  # ホバー中のボタン
        
        # スライダー
        self.slider_rect = pygame.Rect(*self.ui_config['slider_position'], 200, 15)
        self.slider_button_rect = None
        self.slider_active = False
        self.update_slider_position()
        
        # メッセージ表示用の状態
        self.message = None
        self.message_color = None
        self.message_time = 0
        self.last_message_time = 0  # 最後にメッセージを表示した時間を記録
        
        # スピナー用の状態
        self.loading = False
        self.loading_start_time = 0
        self.loading_message = ""
    
    def _setup_event_listeners(self):
        """ゲームからのイベント通知を処理するリスナーを設定"""
        em = self.game.event_manager
        
        # 盤面更新イベント
        em.subscribe('board_updated', self._on_board_updated)
        # 解答完了イベント
        em.subscribe('solve_completed', self._on_solve_completed)
        # 解答中断イベント
        em.subscribe('solve_interrupted', self._on_solve_interrupted)
        # 問題生成開始イベント
        em.subscribe('generation_started', self._on_generation_started)
        # 問題生成の進捗イベント
        em.subscribe('generation_progress', self._on_generation_progress) 
        # 問題生成完了イベント
        em.subscribe('generation_completed', self._on_generation_completed)
        # 盤面ロードイベント
        em.subscribe('board_loaded', self._on_board_loaded)
        # 盤面リセットイベント
        em.subscribe('board_reset', self._on_board_reset)
        # エラーイベント
        em.subscribe('error', self._on_error)
        # 情報通知イベント
        em.subscribe('info', self._on_info)
    
    def _on_board_updated(self, board):
        """盤面更新イベントのハンドラ"""
        self.renderer.board = board
        self.renderer.draw_board()
        self.draw_buttons()
        self.renderer.draw_speed_slider(self.slider_rect, self.slider_button_rect, self.game.solving_speed)
        pygame.display.update()
    
    def _on_solve_completed(self, success):
        """解答完了イベントのハンドラ"""
        if success:
            self.show_temporary_message(get_text("ui.messages", "solved"), self.ui_config["colors"]["valid"])
        else:
            self.show_temporary_message(get_text("ui.messages", "unsolved"), self.ui_config["colors"]["invalid"])
    
    def _on_solve_interrupted(self):
        """解答中断イベントのハンドラ"""
        self.show_temporary_message(get_text("ui.messages", "interrupted"), self.ui_config["colors"]["text_default"])
        pygame.display.update()
    
    def _on_generation_started(self):
        """問題生成開始イベントのハンドラ"""
        self.loading = True
        self.loading_start_time = time.time()
        self.loading_message = get_text("ui.messages", "generating")
        self.show_loading_message_with_spinner(self.loading_message)
        
    def _on_generation_progress(self, message):
        """問題生成進捗イベントのハンドラ"""
        self.loading_message = message
        self.show_loading_message_with_spinner(message)
    
    def _on_generation_completed(self, board):
        """問題生成完了イベントのハンドラ"""
        self.loading = False
        self.renderer.board = board
        self.renderer.draw_board()
        self.show_temporary_message(get_text("ui.messages", "generation_completed"), self.ui_config["colors"]["valid"])
        pygame.display.update()
    
    def _on_board_loaded(self, board):
        """盤面ロードイベントのハンドラ"""
        self.renderer.board = board
        self.renderer.draw_board()
        pygame.display.update()
    
    def _on_board_reset(self):
        """盤面リセットイベントのハンドラ"""
        self.renderer.board = self.game.board
        self.renderer.draw_board()
        self.show_temporary_message(get_text("ui.messages", "reset_completed"), self.ui_config["colors"]["text_default"])
        pygame.display.update()
    
    def _on_error(self, message):
        """エラーメッセージを表示"""
        self.show_temporary_message(message, self.ui_config["colors"]["invalid"])
    
    def _on_info(self, message):
        """情報メッセージを表示"""
        self.show_temporary_message(message, self.ui_config["colors"]["valid"])
    
    def add_buttons(self):
        """すべてのボタンを追加"""
        button_config = self.ui_config["button"]
        button_keys = ["load", "generate", "solve", "reset", "save", "exit"]
        button_labels = [get_text("ui.buttons", key) for key in button_keys]
        
        for i, label in enumerate(button_labels):
            x = button_config["start_x"] + i * button_config["margin_x"]
            y = button_config["start_y"]
            width = button_config["width"]
            height = button_config["height"]
            self.buttons[label] = pygame.Rect(x, y, width, height)
    
    def update_slider_position(self):
        """スライダーの UI 上の位置を視覚的に更新する"""
        # 解答速度の調整：値が大きいほど遅く (5000 が最も遅く、100 が最も速い)
        # スライダーのUIでは左が遅く(5000)、右が速い(100)となるように表示
        normalized_pos = 1.0 - (self.game.solving_speed - 100) / 4900.0  # 位置を反転
        button_x = self.slider_rect.left + normalized_pos * self.slider_rect.width
        self.slider_button_rect = pygame.Rect(button_x - 7, self.slider_rect.y - 5, 14, 25)
    
    def handle_event(self, event):
        """イベントを処理"""
        # メッセージがあり、かつ新しいユーザー操作があった場合のみメッセージをクリア
        # 直前のメッセージ表示から少し時間が経過している場合のみクリア（即時消去を防止）
        current_time = pygame.time.get_ticks()
        if self.message and event.type != pygame.QUIT and (current_time - self.last_message_time) > 300:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.message = None
                # 画面の更新が必要
                self.renderer.draw_board()
                self.draw_buttons()
                self.renderer.draw_speed_slider(self.slider_rect, self.slider_button_rect, self.game.solving_speed)
                pygame.display.update()
            
        if event.type == pygame.QUIT:
            self.quit_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_mouse_button_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.slider_active = False
        elif event.type == pygame.MOUSEMOTION:
            if self.slider_active:
                self.update_slider(event.pos)
            else:
                # ホバー状態の更新
                self.update_button_hover(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
        
        return True
    
    def quit_game(self):
        """ゲームを終了する処理"""
        self.game.solving = False
        pygame.quit()
        sys.exit()
    
    def handle_mouse_button_down(self, pos):
        """マウスボタンが押されたときの処理"""
        if self.slider_button_rect.collidepoint(pos):
            self.slider_active = True
            return
        
        for label, rect in self.buttons.items():
            if rect.collidepoint(pos):
                self._handle_button_click(label)
                return
        
        self.handle_cell_selection(pos)
    
    def handle_cell_selection(self, pos):
        """セルの選択処理"""
        cell_size = self.ui_config["cell_size"]
        origin_x, origin_y = self.ui_config["board_origin"]
        
        x, y = pos
        if (origin_x <= x < origin_x + 9 * cell_size and 
            origin_y <= y < origin_y + 9 * cell_size):
            col = (x - origin_x) // cell_size
            row = (y - origin_y) // cell_size
            
            if not self.game.board.is_original_cell(row, col):
                self.renderer.set_selected_cell(row, col)
                # handle_eventで処理するのでここでのメッセージクリアは不要
            else:
                self.show_temporary_message(get_text("ui.messages", "cell_unchangeable"), self.ui_config["colors"]["invalid"])
    
    def update_slider(self, pos):
        """スライダーの位置をマウスの動きに基づいて更新し、解答速度を計算してゲームの状態を更新する"""
        # メッセージをクリアする必要はない（handle_eventで処理済み）
        
        x = max(self.slider_rect.left, min(pos[0], self.slider_rect.right))
        normalized_pos = (x - self.slider_rect.left) / self.slider_rect.width
        speed = int(5000 - normalized_pos * 4900)
        self.game.update_solving_speed(speed)
        self.update_slider_position()
    
    def handle_keydown(self, event):
        """キーボードの入力処理"""
        # メッセージをクリアする必要はない（handle_eventで処理済み）
        
        selected_cell = self.renderer.selected_cell
        if selected_cell and not self.game.solving:
            row, col = selected_cell
            
            if not self.game.board.is_original_cell(row, col):
                self.handle_number_input(event, row, col)
        
        self.handle_arrow_keys(event)
    
    def handle_number_input(self, event, row, col):
        """数字キーの入力処理"""
        # メッセージをクリアする必要はない（handle_eventで処理済み）
        
        if pygame.K_1 <= event.key <= pygame.K_9:
            num = event.key - pygame.K_0
            self.game.board.set_value(row, col, num)
        elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
            num = event.key - pygame.K_KP1 + 1
            self.game.board.set_value(row, col, num)
        elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_SPACE, pygame.K_0, pygame.K_KP0):
            self.game.board.set_value(row, col, 0)
    
    def handle_arrow_keys(self, event):
        """矢印キーの入力処理"""
        if self.renderer.selected_cell:
            row, col = self.renderer.selected_cell
            if event.key == pygame.K_UP:
                self.move_selection(row - 1, col)
            elif event.key == pygame.K_DOWN:
                self.move_selection(row + 1, col)
            elif event.key == pygame.K_LEFT:
                self.move_selection(row, col - 1)
            elif event.key == pygame.K_RIGHT:
                self.move_selection(row, col + 1)
    
    def move_selection(self, row, col):
        """セルの選択を移動する処理"""
        if 0 <= row < 9 and 0 <= col < 9:
            while 0 <= row < 9 and 0 <= col < 9:
                if not self.game.board.is_original_cell(row, col):
                    self.renderer.set_selected_cell(row, col)
                    # handle_eventで処理するのでここでのメッセージクリアは不要
                    break
                # 方向に応じて行または列を進める
                if row < self.renderer.selected_cell[0]:
                    row -= 1
                elif row > self.renderer.selected_cell[0]:
                    row += 1
                if col < self.renderer.selected_cell[1]:
                    col -= 1
                elif col > self.renderer.selected_cell[1]:
                    col += 1
    
    def _handle_button_click(self, button_name):
        """ボタンのクリックイベントを処理"""
        # メッセージをクリアする必要はない（handle_eventで処理済み）
        
        if self.game.solving:
            # 解答中は「中断」と「終了」ボタンのみ有効
            if button_name == get_text("ui.buttons", "solve"):  # 解答中は「中断」ボタンとして機能
                self.game.solving = False
                self.game.event_manager.notify('solve_interrupted')
            elif button_name == get_text("ui.buttons", "exit"):
                self.game.solving = False
                pygame.quit()
                sys.exit()
            else:
                # 他のボタンは無効化状態を示すメッセージを表示
                self.show_temporary_message(get_text("ui.messages", "solving_disabled"), self.ui_config["colors"]["invalid"])
            return
            
        # 解答中でない場合の通常の処理
        if button_name == get_text("ui.buttons", "load"):
            self.load_file()
        elif button_name == get_text("ui.buttons", "save"):
            self.save_file()
        elif button_name == get_text("ui.buttons", "solve"):
            self._handle_solve_button()
        elif button_name == get_text("ui.buttons", "reset"):
            self.game.reset()
            self.renderer.selected_cell = None
        elif button_name == get_text("ui.buttons", "generate"):
            difficulty = self.show_difficulty_modal()
            if difficulty:  # 難易度が選択された場合のみ
                self.game.generate_problem(difficulty)
        elif button_name == get_text("ui.buttons", "exit"):
            self.game.solving = False
            pygame.quit()
            sys.exit()
    
    def _handle_solve_button(self):
        """解くボタンの処理"""
        if not self.game.solving:
            # 直接ゲームのメソッドを呼び出す
            self.game.solve()
    
    def load_file(self):
        """ファイルを読み込み、ゲームに反映する"""
        # 現在のウィンドウを記憶
        current_window = pygame.display.get_surface()
        
        # tkinterダイアログを表示
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)  # ダイアログを最前面に
        file_path = filedialog.askopenfilename(
            title="数独ファイルを選択",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir="."  # カレントディレクトリをデフォルトに設定
        )
        root.destroy()  # Tkインスタンスを破棄
        
        # Pygameウィンドウを再アクティブ化
        pygame.display.update()
        
        # イベントキューをクリア
        pygame.event.clear()
        
        # 少し待機して、OSがウィンドウフォーカスを処理する時間を与える
        pygame.time.delay(100)
        
        if file_path:
            try:
                board_data = load_board_from_file(file_path)
                self.game.load_board(board_data)
            except Exception as e:
                error_msg = str(e)
                self.show_temporary_message(get_text("ui.messages", "load_failed", "読み込み失敗: {0}", error_msg), self.ui_config["colors"]["invalid"])
    
    def save_file(self):
        """現在の盤面をファイルに保存"""
        # 現在のウィンドウを記憶
        current_window = pygame.display.get_surface()
        
        # tkinterダイアログを表示
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)  # ダイアログを最前面に
        default_name = f"sudoku_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = filedialog.asksaveasfilename(
            title="数独ファイルを保存",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialdir="."  # カレントディレクトリをデフォルトに設定
        )
        root.destroy()  # Tkインスタンスを破棄
        
        # Pygameウィンドウを再アクティブ化
        pygame.display.update()
        
        # イベントキューをクリア
        pygame.event.clear()
        
        # 少し待機して、OSがウィンドウフォーカスを処理する時間を与える
        pygame.time.delay(100)
        
        if file_path:
            try:
                success = self.game.save_current_board(file_path)
                if success:
                    self.show_temporary_message(get_text("ui.messages", "file_saved"), self.ui_config["colors"]["valid"])
            except Exception as e:
                error_msg = str(e)
                self.show_temporary_message(get_text("ui.messages", "save_failed", "保存失敗: {0}", error_msg), self.ui_config["colors"]["invalid"])
    
    def show_difficulty_modal(self) -> str:
        """難易度選択モーダルを表示（pygame ベース）"""
        font = pygame.font.SysFont(self.ui_config["font"]["default"], 24)
        difficulty_keys = ["easy", "medium", "hard", "random"]
        difficulties = [(get_text("ui.difficulties", key), key) for key in difficulty_keys]
        selected_difficulty = None
        hovered_button = None
        
        # モーダルウィンドウの背景
        modal_rect = pygame.Rect(100, 100, 400, 300)
        pygame.draw.rect(self.window, self.ui_config["colors"]["background"], modal_rect)
        pygame.draw.rect(self.window, self.ui_config["colors"]["grid"], modal_rect, 2)
        
        # ラベルを描画
        label = font.render(get_text("ui.messages", "select_difficulty"), True, self.ui_config["colors"]["text_default"])
        self.window.blit(label, (modal_rect.x + 20, modal_rect.y + 20))
        
        # ボタンを描画する関数
        def draw_buttons():
            buttons = []
            for i, (text, value) in enumerate(difficulties):
                button_rect = pygame.Rect(modal_rect.x + 50, modal_rect.y + 60 + i * 50, 300, 40)
                
                # ホバー状態に応じて色を変える
                if value == hovered_button:
                    color = self.ui_config["colors"]["button_hover"]
                else:
                    color = self.ui_config["colors"]["button"]
                
                pygame.draw.rect(self.window, color, button_rect)
                pygame.draw.rect(self.window, self.ui_config["colors"]["grid"], button_rect, 2)
                
                # テキストを描画（中央揃え）
                button_text = font.render(text, True, self.ui_config["colors"]["text_default"])
                text_rect = button_text.get_rect(center=button_rect.center)
                self.window.blit(button_text, text_rect)
                
                buttons.append((button_rect, value))
            return buttons
        
        # 初期描画
        buttons = draw_buttons()
        pygame.display.update()
        
        # イベントループで選択を待つ
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    # ホバー状態の更新
                    old_hovered = hovered_button
                    hovered_button = None
                    for button_rect, value in buttons:
                        if button_rect.collidepoint(event.pos):
                            hovered_button = value
                            break
                    
                    # ホバー状態が変わった場合のみ再描画
                    if old_hovered != hovered_button:
                        buttons = draw_buttons()
                        pygame.display.update()
                        
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button_rect, value in buttons:
                        if button_rect.collidepoint(event.pos):
                            selected_difficulty = value
                            waiting = False
        
        return selected_difficulty
    
    def show_message(self, message: str, color):
        """ユーザーの操作を待つメッセージを表示"""
        rect = pygame.Rect(0, self.ui_config["window"]["height"] - self.ui_config["message_area_height"], 
                          self.ui_config["window"]["width"], self.ui_config["message_area_height"])
        pygame.draw.rect(self.window, self.ui_config["colors"]["message_background"], rect)
        
        font = pygame.font.SysFont(self.ui_config["font"]["default"], self.ui_config["font"]["button_size"])
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(self.ui_config["window"]["width"] // 2, 
                                        self.ui_config["window"]["height"] - self.ui_config["message_area_height"] // 2))
        self.window.blit(text, text_rect)
        
        pygame.display.update()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False
    
    def show_temporary_message(self, message: str, color):
        """一時的なメッセージを表示（自動的に消えない）"""
        self.message = message
        self.message_color = color
        self.message_time = pygame.time.get_ticks()
        self.last_message_time = self.message_time  # メッセージを表示した時間を記録
        
        # メッセージを描画
        font = pygame.font.SysFont(self.ui_config["font"]["default"], self.ui_config["font"]["message_size"])
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(self.window.get_width() // 2, self.window.get_height() - 40))
        self.window.blit(text, text_rect)
        pygame.display.update()
    
    def draw_spinner(self, center_x, center_y, radius=20):
        """スピナーを描画"""
        # 経過時間に基づいて回転角度を計算
        angle = (time.time() - self.loading_start_time) * 360 % 360
        
        # 12個の点を描画して「読み込み中」を表現
        for i in range(12):
            # 点の角度を計算
            dot_angle = (i * 30 + angle) % 360
            rad = math.radians(dot_angle)
            
            # 点の位置を計算
            x = center_x + int(radius * math.cos(rad))
            y = center_y + int(radius * math.sin(rad))
            
            # 点の大きさと色の計算（時計回りで徐々に薄くなる）
            size = max(3, 8 - (i % 12) // 2)
            alpha = 255 - (i * 20) % 256
            color = (100, 100, 100, alpha)
            
            # 点を描画
            pygame.draw.circle(self.window, color, (x, y), size)
    
    def show_loading_message_with_spinner(self, message: str):
        """スピナー付きの読み込みメッセージを表示"""
        # 背景をクリア
        self.window.fill(self.ui_config["colors"]["background"])
        
        # メッセージを描画
        font = pygame.font.SysFont(self.ui_config["font"]["default"], 36)
        text = font.render(message, True, self.ui_config["colors"]["text_default"])
        text_rect = text.get_rect(center=(self.window.get_width() // 2, self.window.get_height() - 30))
        self.window.blit(text, text_rect)
        
        # スピナーを描画
        center_x = self.window.get_width() // 2
        center_y = self.window.get_height() // 2 + 40
        self.draw_spinner(center_x, center_y)
        
        # 画面を更新
        pygame.display.update()
    
    def show_loading_message(self, message: str):
        """画面中央にメッセージを表示（スピナーなし - 後方互換性のため残す）"""
        self.show_loading_message_with_spinner(message)
    
    def draw_buttons(self):
        """ボタンを描画"""
        button_config = self.ui_config["button"]
        font = pygame.font.SysFont(self.ui_config["font"]["default"], self.ui_config["font"]["button_size"])
        
        for label, rect in self.buttons.items():
            # 解答中の場合の特別な処理
            if self.game.solving:
                if label == get_text("ui.buttons", "solve"):
                    # 「解く」ボタンを「中断」として表示
                    text = get_text("ui.buttons", "interrupt")
                    color = self.ui_config["colors"]["button"]
                elif label == get_text("ui.buttons", "exit"):
                    # 「終了」ボタンは通常通り表示
                    text = label
                    color = self.ui_config["colors"]["button"]
                else:
                    # その他のボタンはグレーアウト
                    text = label
                    color = [150, 150, 150]  # グレー色
            else:
                text = label
                color = self.ui_config["colors"]["button"]
                
                # ホバー状態の場合は色を変える
                if label == self.hovered_button:
                    color = self.ui_config["colors"]["button_hover"]
            
            # ボタンの背景を描画
            pygame.draw.rect(self.window, color, rect)
            pygame.draw.rect(self.window, self.ui_config["colors"]["grid"], rect, 2)
            
            # ボタンのテキストを描画
            text_surface = font.render(text, True, self.ui_config["colors"]["text_default"])
            text_rect = text_surface.get_rect(center=rect.center)
            self.window.blit(text_surface, text_rect)
            
    def update_button_hover(self, pos):
        """マウス位置に基づいてボタンのホバー状態を更新"""
        previous_hovered = self.hovered_button
        self.hovered_button = None
        
        for label, rect in self.buttons.items():
            if rect.collidepoint(pos):
                self.hovered_button = label
                break
        
        # ホバー状態が変わった場合のみ再描画
        if previous_hovered != self.hovered_button:
            self.draw_buttons()
            pygame.display.update()
    
    def run(self):
        """メインの GUI ゲームループ"""
        running = True
        while running:
            self.clock.tick(30)
            
            # ローディング中はスピナーを表示
            if self.loading:
                self.show_loading_message_with_spinner(self.loading_message)
            else:
                # 通常の盤面描画
                self.renderer.draw_board()
                self.draw_buttons()
                self.renderer.draw_speed_slider(self.slider_rect, self.slider_button_rect, self.game.solving_speed)
                
                # メッセージがあれば表示
                if self.message:
                    font = pygame.font.SysFont(self.ui_config["font"]["default"], 24)
                    text = font.render(self.message, True, self.message_color)
                    text_rect = text.get_rect(center=(self.window.get_width() // 2, self.window.get_height() - 30))
                    self.window.blit(text, text_rect)
                
                pygame.display.update()
            
            # イベント処理
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
        
        # ゲーム終了時の処理
        pygame.quit()
        sys.exit()
