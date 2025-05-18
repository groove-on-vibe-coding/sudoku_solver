from typing import List, Optional, Tuple
from file_io import load_board_from_file
from lang_manager import get_text


class SudokuBoard:
    def __init__(self, board: List[List[int]] = None):
        if board is None:
            self.board = [[0 for _ in range(9)] for _ in range(9)]
        else:
            self.validate_board_format(board)
            self.board = [row[:] for row in board]
        
        self.original_board = [row[:] for row in self.board]
    
    def validate_board_format(self, board: List[List[int]]) -> None:
        if len(board) != 9:
            raise ValueError(get_text("board.errors", "invalid_rows"))
        for row in board:
            if len(row) != 9:
                raise ValueError(get_text("board.errors", "invalid_columns"))
            for cell in row:
                if not isinstance(cell, int) or not (0 <= cell <= 9):
                    raise ValueError(get_text("board.errors", "invalid_cell"))
    
    def validate_full_board(self) -> bool:
        """盤面全体が現在の状態で妥当（重複がない）かどうかをチェック"""
        for i in range(9):
            for j in range(9):
                num = self.board[i][j]
                if num != 0:
                    self.board[i][j] = 0
                    if not self.is_valid(i, j, num):
                        self.board[i][j] = num  # 復元
                        return False
                    self.board[i][j] = num  # 復元
        return True
    
    @classmethod
    def from_file(cls, filepath: str) -> 'SudokuBoard':
        board_data = load_board_from_file(filepath)
        return cls(board_data)
    
    def is_valid(self, row: int, col: int, num: int) -> bool:
        for x in range(9):
            if self.board[row][x] == num or self.board[x][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[start_row + i][start_col + j] == num:
                    return False
        return True
    
    def find_empty(self) -> Optional[Tuple[int, int]]:
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None
    
    def set_value(self, row: int, col: int, value: int) -> None:
        self.board[row][col] = value
    
    def get_value(self, row: int, col: int) -> int:
        return self.board[row][col]
    
    def is_original_cell(self, row: int, col: int) -> bool:
        return self.original_board[row][col] != 0
    
    def reset(self) -> None:
        self.board = [row[:] for row in self.original_board]
    
    def copy(self) -> 'SudokuBoard':
        """現在の盤面のコピーを作成"""
        return SudokuBoard([row[:] for row in self.board])
