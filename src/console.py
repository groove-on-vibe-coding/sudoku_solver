import os
import time
import random
import argparse
from datetime import datetime
from board import SudokuBoard
from solver import SudokuSolver
from generator import SudokuGenerator
from file_io import save_board_to_file, load_board_from_file
from lang_manager import get_text, get_language_manager


def print_board(board: SudokuBoard):
    print("-" * 25)
    for i, row in enumerate(board.board):
        print("| ", end="")
        for j, cell in enumerate(row):
            print(cell if cell != 0 else ".", end=" ")
            if (j + 1) % 3 == 0:
                print("| ", end="")
        print()
        if (i + 1) % 3 == 0:
            print("-" * 25)


def run_console(input_file: str, verbose: bool = False, language: str = None):
    # 言語設定を初期化（引数で指定された場合のみ）
    if language:
        get_language_manager(language)
        
    try:
        print(get_text("console.messages", "loading_puzzle"))
        board_data = load_board_from_file(input_file)  # 直接file_io.pyを使用
        board = SudokuBoard(board_data)
        solver = SudokuSolver(board)
        
        print(get_text("console.messages", "puzzle_loaded"))
        print("\n" + get_text("console.messages", "original_puzzle") + ":")
        print_board(board)
        
        print(get_text("console.messages", "solving_puzzle"))
        start_time = time.time()
        if solver.solve(animate=False):  # コールバックなしでsolveを呼び出す
            end_time = time.time()
            print("\n" + get_text("console.messages", "solution"))
            print_board(board)
            if verbose:
                elapsed_time = end_time - start_time
                print(get_text("console.messages", "solving_time", elapsed_time))
        else:
            print(get_text("console.messages", "no_solution"))
    except Exception as e:
        print(f"{get_text('console.messages', 'error')}: {e}")


def generate_problems(count: int, difficulty: str, output_dir: str, language: str = None):
    # 言語設定を初期化（引数で指定された場合のみ）
    if language:
        get_language_manager(language)
        
    os.makedirs(output_dir, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    difficulties = ["easy", "medium", "hard"]
    
    print(get_text("console.messages", "generating_puzzle"))
    
    for i in range(1, count + 1):
        d = random.choice(difficulties) if difficulty == "random" else difficulty
        generator = SudokuGenerator()
        problem = generator.generate(d)
        board = SudokuBoard(problem)
        
        filename = f"{d}_{now}_{i}.txt"
        filepath = os.path.join(output_dir, filename)
        save_board_to_file(board.board, filepath)
        
        print(get_text("console.messages", "puzzle_saved", filepath))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='数独パズルを解くプログラム')
    parser.add_argument('file', nargs='?', help='数独パズルのファイルパス')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細出力モード')
    parser.add_argument('-g', '--generate', type=int, help='問題を自動生成して保存（指定した数）')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard', 'random'], default='medium',
                        help='生成時の難易度（default: medium、random指定可）')
    parser.add_argument('--output_dir', type=str, default='generated',
                        help='出力先フォルダ（default: ./generated）')
    parser.add_argument('--language', type=str, choices=['ja', 'en'], help='言語設定（ja: 日本語, en: 英語）')
    args = parser.parse_args()
    
    # 言語設定を初期化
    language = args.language or "ja"
    get_language_manager(language)
    
    if args.generate:
        generate_problems(args.generate, args.difficulty, args.output_dir, language)
    elif args.file:
        run_console(args.file, args.verbose, language)
