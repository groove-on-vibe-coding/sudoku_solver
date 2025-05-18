import random
import pygame
import sys
import time
from typing import List, Tuple, Callable, Optional
from board import SudokuBoard
from solver import SudokuSolver


class SudokuGenerator:
    """問題生成器（難易度付き）"""
    
    def __init__(self):
        self.board = SudokuBoard()
    
    def generate(self, difficulty: str, progress_callback: Optional[Callable] = None) -> SudokuBoard:
        """
        問題を生成
        
        Args:
            difficulty: 難易度 ("easy", "medium", "hard", "random")
            progress_callback: 進捗通知用のコールバック関数（オプション）
        
        Returns:
            SudokuBoard: 生成された問題
        """
        if difficulty == "random":
            difficulty = random.choice(["easy", "medium", "hard"])  # ランダムに難易度を選択
        
        # 進捗通知（コールバックがあれば）
        if progress_callback:
            progress_callback("問題を生成中です...")
        
        # 少し待機して進捗表示を確実に表示させる
        self._process_events()
        time.sleep(0.1)  # UIが更新される時間を確保
        
        attempt_count = 0
        while True:
            attempt_count += 1
            
            # 定期的に進捗を通知
            if progress_callback and attempt_count % 2 == 0:
                progress_callback(f"問題を生成中です... (試行: {attempt_count})")
            
            # イベント処理でUIの応答性を確保
            self._process_events()
            
            # 問題生成ロジック
            board = self._generate_board(difficulty, progress_callback)
            
            # 解答可能性を確認
            if progress_callback:
                progress_callback("一意解を確認中...")
            self._process_events()
            
            if self._is_solvable(board):
                # 完了メッセージ（コールバックがあれば）
                if progress_callback:
                    progress_callback("問題の生成が完了しました")
                return board
            
            # 再試行メッセージ（コールバックがあれば）
            if progress_callback:
                progress_callback("一意解にならないため再生成しています...")
            
            # イベント処理
            self._process_events()
    
    def _process_events(self):
        """pygame イベントを処理して UI の応答性を確保"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    def _generate_board(self, difficulty: str, progress_callback: Optional[Callable] = None) -> SudokuBoard:
        """問題を生成する（難易度付き）"""
        # 空の盤面を作成
        self.board = SudokuBoard()
        
        # 進捗通知
        if progress_callback:
            progress_callback("完成盤面を作成中...")
        self._process_events()
        
        # 完成された盤面を作成
        self._fill_board()
        
        # 進捗通知
        if progress_callback:
            progress_callback(f"難易度 '{difficulty}' に調整中...")
        self._process_events()
        
        # 難易度に応じてセルを削除
        self._remove_cells(difficulty, progress_callback)
        
        return self.board
    
    def _fill_board(self) -> bool:
        """完成された盤面を作成（バックトラッキング）"""
        empty = self.board.find_empty()
        if not empty:
            return True
        
        row, col = empty
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for num in numbers:
            if self.board.is_valid(row, col, num):
                self.board.set_value(row, col, num)
                
                # 定期的にイベント処理
                if (row * 9 + col) % 20 == 0:
                    self._process_events()
                    
                if self._fill_board():
                    return True
                self.board.set_value(row, col, 0)
        return False
    
    def _remove_cells(self, difficulty: str, progress_callback: Optional[Callable] = None):
        """難易度に応じてセルを消す（ランダム）"""
        if difficulty == "easy":
            to_remove = 35
        elif difficulty == "hard":
            to_remove = 55
        else:  # default = medium
            to_remove = 45
        
        count = 0
        attempts = 0
        max_attempts = 1000
        last_progress_update = 0
        
        # 一意解になるまでセルを消す
        while count < to_remove and attempts < max_attempts:
            attempts += 1
            
            # 定期的に進捗を更新
            if progress_callback and attempts - last_progress_update >= 50:
                progress_callback(f"難易度調整中... ({count}/{to_remove})")
                last_progress_update = attempts
                self._process_events()
            
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            
            if self.board.get_value(row, col) != 0:
                backup = self.board.get_value(row, col)
                self.board.set_value(row, col, 0)
                
                # 一意解チェック（最低限の確認）
                board_copy = SudokuBoard([row[:] for row in self.board.board])
                solver = SudokuSolver(board_copy)
                solutions = []
                self._count_solutions(board_copy, solver, solutions, max_solutions=2)
                
                if len(solutions) != 1:
                    self.board.set_value(row, col, backup)  # 戻す
                else:
                    count += 1
            
            # 定期的にイベント処理
            if attempts % 10 == 0:
                self._process_events()
        
        # 最終進捗更新
        if progress_callback:
            progress_callback(f"難易度調整完了 ({count}/{to_remove})")
    
    def _count_solutions(self, board: SudokuBoard, solver: SudokuSolver, solutions: List[List[List[int]]], max_solutions: int):
        """再帰的に解を数える（複数解検出用）"""
        empty = board.find_empty()
        if not empty:
            solutions.append([row[:] for row in board.board])
            return
        
        # 空のセルを見つける
        row, col = empty
        for num in range(1, 10):
            if board.is_valid(row, col, num):
                board.set_value(row, col, num)
                self._count_solutions(board, solver, solutions, max_solutions)
                if len(solutions) >= max_solutions:
                    board.set_value(row, col, 0)  # 元に戻す前に早期リターン
                    return
                board.set_value(row, col, 0)
    
    def _is_solvable(self, board: SudokuBoard) -> bool:
        """盤面が解答可能かどうかを確認"""
        if not isinstance(board, SudokuBoard):
            board = SudokuBoard(board)  # リストの場合は SudokuBoard に変換
        board_copy = SudokuBoard([row[:] for row in board.board])
        solver = SudokuSolver(board_copy)
        return solver.solve(animate=False)  # 解答可能なら True を返す
