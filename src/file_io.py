from typing import List
from lang_manager import get_text


def load_board_from_file(filepath: str) -> List[List[int]]:
    """テキストファイルから盤面を読み込む（9x9の2次元リスト）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    board = []
    for line in lines:
        line = line.strip()
        if len(line) == 9 and all(c.isdigit() for c in line):
            board.append([int(c) for c in line])
    if len(board) != 9:
        raise ValueError(get_text("file_io.errors", "invalid_format"))
    return board


def save_board_to_file(board: List[List[int]], filepath: str):
    """2次元リストの盤面をテキストファイルに保存"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for row in board:
            line = ''.join(str(num) for num in row)
            f.write(line + '\n')
