import pygame
import threading
import os
import sys
from solver import SudokuSolver
from board import SudokuBoard
from generator import SudokuGenerator
from file_io import save_board_to_file
from config import load_ui_settings
from event_manager import EventManager
from lang_manager import get_text

class GameInitializationError(Exception):
    """ゲームの初期化時に発生するエラー"""
    pass

class SudokuGame:
    def __init__(self, input_file=None, ui_settings=None):
        pygame.init()
        pygame.font.init()
        
        # イベントマネージャーを最初に初期化
        self.event_manager = EventManager()
        
        # UI設定をロード
        try:
            if ui_settings is None:
                self.ui_config = load_ui_settings("ui_setting.json")
                if self.ui_config is None:
                    raise GameInitializationError(get_text("game.messages", "ui_load_error"))
            else:
                self.ui_config = ui_settings
        except Exception as e:
            raise GameInitializationError(get_text("game.messages", "ui_init_error", str(e)))
        
        # 盤面の初期化
        try:
            if input_file:
                if not os.path.exists(input_file):
                    self.event_manager.notify('error', get_text("game.messages", "file_not_found", input_file))
                    self.board = SudokuBoard()
                else:
                    try:
                        self.board = SudokuBoard.from_file(input_file)
                        self.event_manager.notify('info', get_text("game.messages", "board_loaded"))
                    except ValueError as e:
                        self.event_manager.notify('error', get_text("game.messages", "invalid_file_format", str(e)))
                        self.board = SudokuBoard()
                    except Exception as e:
                        self.event_manager.notify('error', get_text("game.messages", "load_error", str(e)))
                        self.board = SudokuBoard()
            else:
                self.board = SudokuBoard()
        except Exception as e:
            self.event_manager.notify('error', get_text("game.messages", "board_init_error", str(e)))
            self.board = SudokuBoard()
        
        self.solver = SudokuSolver(self.board)
        self.solving = False
        self.solving_speed = 2550
        self.last_generated_difficulty = "medium"
        self.generator = SudokuGenerator()
        
        # UIは外部から設定する
        self.ui = None
    
    def set_ui(self, ui):
        """UI を設定するメソッド"""
        self.ui = ui
        # 初期化時のエラーメッセージがあれば表示
        if hasattr(self, '_init_error'):
            self.ui.show_temporary_message(self._init_error, self.ui_config["colors"]["invalid"])
    
    def reset(self):
        self.board.reset()
        self.solving = False
        # イベント発火
        self.event_manager.notify('board_reset')
    
    def solve(self):
        """数独を解く処理"""
        if self.solving:
            # 既に解答中の場合は中断
            self.solving = False
            self.event_manager.notify('solve_interrupted')
            return
            
        # 盤面の妥当性チェック
        if not self.board.validate_full_board():
            self.event_manager.notify('error', get_text("game.messages", "invalid_board"))
            return
            
        self.solving = True
        board_copy = self.board.copy()
        solver = SudokuSolver(board_copy)
        
        # UI に盤面更新を通知するためのコールバック
        def update_ui_callback():
            # 現在の解答状態を反映
            self.board.board = [row[:] for row in board_copy.board]
            self.event_manager.notify('board_updated', self.board)
            
            # イベントを処理してUI操作を可能にする
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.solving = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # クリック位置を取得
                    pos = event.pos
                    # 「解く」ボタンと「終了」ボタンのクリックを処理
                    if self.ui:
                        for label, rect in self.ui.buttons.items():
                            if rect.collidepoint(pos):
                                if label == get_text("ui.buttons", "solve"):
                                    self.solving = False
                                    # 中断時は現在の状態を保持
                                    self.board.board = [row[:] for row in board_copy.board]
                                    return
                                elif label == get_text("ui.buttons", "exit"):
                                    self.solving = False
                                    pygame.quit()
                                    sys.exit()
            
            # 描画を更新
            if self.ui:
                self.ui.renderer.draw_board()
                self.ui.draw_buttons()
                self.ui.renderer.draw_speed_slider(
                    self.ui.slider_rect,
                    self.ui.slider_button_rect,
                    self.solving_speed
                )
                pygame.display.update()
        
        # 解法実行
        solved = solver.solve(True, update_ui_callback, self.solving_speed // 100, self)
        
        if solved and self.solving:  # 解答が完了し、かつ中断されていない場合のみ結果を反映
            self.board.board = [row[:] for row in board_copy.board]
            self.event_manager.notify('solve_completed', True)
        elif not self.solving:
            # 中断時は現在の状態を保持（既に update_ui_callback で反映済み）
            self.event_manager.notify('solve_interrupted')
        else:
            self.event_manager.notify('solve_completed', False)
        
        self.solving = False
    
    def generate_problem(self, difficulty: str):
        """問題を生成"""
        self.event_manager.notify('generation_started')
        
        # 進捗通知用のコールバック関数
        def progress_callback(message):
            self.event_manager.notify('generation_progress', message)
        
        # 問題を生成（プログレスコールバックを渡す）
        problem = self.generator.generate(difficulty, progress_callback)
        self.board = SudokuBoard(problem.board)  # board プロパティにアクセス
        
        # 生成完了イベントを通知
        self.event_manager.notify('generation_completed', self.board)
    
    def save_current_board(self, filepath: str):
        """盤面をファイルに保存"""
        save_board_to_file(self.board.board, filepath)
        return True
    
    def load_board(self, board_data):
        """盤面をロード"""
        self.board = SudokuBoard(board_data)
        self.event_manager.notify('board_loaded', self.board)
    
    def update_solving_speed(self, speed):
        """解答速度を更新"""
        self.solving_speed = speed
        
    def run(self):
        """ゲームのメインループを実行（UI 側で実行される）"""
        if self.ui:
            self.ui.run()
        else:
            raise ValueError("UI が設定されていません。先にset_ui()メソッドを呼び出してください。")
