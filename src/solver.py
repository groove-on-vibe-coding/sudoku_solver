import pygame
import sys
from board import SudokuBoard
from typing import Callable, Optional


class SudokuSolver:
    """数独を解くためのクラス"""
    
    def __init__(self, board: SudokuBoard):
        self.board = board
    
    def solve(self, animate: bool, callback: Optional[Callable] = None, delay: int = 0, game=None) -> bool:
        """数独を解く
        
        Args:
            animate: アニメーション表示を行うかどうか
            callback: 盤面更新時のコールバック関数
            delay: アニメーションの遅延時間（ミリ秒）
            game: ゲームインスタンス（中断チェック用）
            
        Returns:
            bool: 解けたかどうか
        """
        # メインイベントループを維持するために定期的にイベントを処理
        if animate and callback:
            pygame.event.pump()
            
            # 中断チェック
            if game and not game.solving:
                return False
            
            # UIの更新
            callback()
            
            # 遅延処理（短い間隔で複数回に分けることでUIの応答性を維持）
            if delay > 0:
                steps = 10
                step_delay = max(1, delay // steps)
                for _ in range(steps):
                    pygame.time.delay(step_delay)
                    pygame.event.pump()
                    if game and not game.solving:
                        return False
        
        # 解法処理
        for i in range(9):
            for j in range(9):
                if self.board.get_value(i, j) == 0:
                    for num in range(1, 10):
                        if self.board.is_valid(i, j, num):
                            self.board.set_value(i, j, num)
                            
                            if self.solve(animate, callback, delay, game):
                                return True
                                
                            self.board.set_value(i, j, 0)
                    return False
        return True
