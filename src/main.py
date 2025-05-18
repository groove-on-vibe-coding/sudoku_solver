"""
数独ソルバーアプリケーションのメインモジュール
"""
import argparse
import sys
import os
from game import SudokuGame
from ui import SudokuUI
from console import run_console
from config import load_ui_settings
from lang_manager import get_text, get_language_manager

# Windows 環境での日本語表示対応
if os.name == 'nt':
    os.environ['SDL_VIDEODRIVER'] = 'windib'


def main():
    # コマンドライン引数を解析
    parser = argparse.ArgumentParser(description='数独パズルを解くプログラム')
    parser.add_argument('file', nargs='?', help='数独パズルのファイルパス')
    parser.add_argument('-c', '--console', action='store_true', help='コンソールモードで実行')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細出力モード')
    parser.add_argument('-g', '--generate', type=int, help='問題を自動生成して保存（指定した数）')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard', 'random'], default='medium',
                        help='生成時の難易度（default: medium、random 指定可）')
    parser.add_argument('--output_dir', type=str, default='generated',
                        help='出力先フォルダ（default: ./generated）')
    parser.add_argument('--language', type=str, choices=['ja', 'en'], help='言語設定（ja: 日本語, en: 英語）')
    args = parser.parse_args()

    # UI設定を読み込む
    ui_settings_path = os.path.join(os.path.dirname(__file__), 'ui_setting.json')
    ui_settings = load_ui_settings(ui_settings_path)
    if ui_settings is None:
        # 言語マネージャーを初期化（コマンドライン引数の言語設定を優先）
        get_language_manager(args.language or "ja")
        print(get_text("main.errors", "ui_load_error"))
        sys.exit(1)
    
    # 言語設定を初期化（コマンドライン引数の言語設定を優先）
    language = args.language or ui_settings.get("language", "ja")
    get_language_manager(language)
    
    # コマンドライン引数の言語設定を優先するため、UI設定を更新
    if args.language:
        ui_settings["language"] = args.language
    
    if args.console:
        run_console(args.file, args.verbose, language)
    elif args.generate:
        from console import generate_problems
        generate_problems(args.generate, args.difficulty, args.output_dir, language)
        sys.exit(0)
    else:
        # ゲームインスタンスを作成し、UI設定を渡す
        game = SudokuGame(args.file, ui_settings)
        # UI インスタンスを作成し、ゲームをセット
        ui = SudokuUI(game)
        # UI をゲームにセット
        game.set_ui(ui)
        # ゲームを実行
        game.run()

if __name__ == "__main__":
    main()
