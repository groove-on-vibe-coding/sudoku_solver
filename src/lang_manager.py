import json
import os
import sys
from typing import Dict, Any, Optional

class LanguageManager:
    """言語ファイルを管理するクラス"""
    
    def __init__(self, lang_code: str = "ja"):
        """
        言語マネージャーを初期化
        
        Args:
            lang_code: 言語コード（デフォルト: "ja"）
        """
        self.lang_code = lang_code
        self.translations: Dict[str, Any] = {}
        self.load_language(lang_code)
    
    def load_language(self, lang_code: str) -> bool:
        """
        指定された言語コードの言語ファイルを読み込む
        
        Args:
            lang_code: 言語コード
            
        Returns:
            bool: 読み込みに成功したかどうか
        """
        self.lang_code = lang_code
        
        # 言語ファイルを探す場所のリスト
        search_paths = []
        
        # 1. exeと同じディレクトリの lang フォルダ (PyInstallerでビルドされた場合)
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            search_paths.append(os.path.join(exe_dir, "lang", f"{lang_code}.json"))
        
        # 2. カレントディレクトリの lang フォルダ
        search_paths.append(os.path.join(os.getcwd(), "lang", f"{lang_code}.json"))
        
        # 3. ソースディレクトリの lang フォルダ
        src_dir = os.path.dirname(__file__)
        search_paths.append(os.path.join(src_dir, "lang", f"{lang_code}.json"))
        
        # 4. PyInstallerでビルドされた場合の一時ディレクトリ
        if getattr(sys, 'frozen', False):
            search_paths.append(os.path.join(sys._MEIPASS, "lang", f"{lang_code}.json"))
        
        # 各パスを順番に試す
        for lang_file in search_paths:
            if os.path.exists(lang_file):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        print(f"Info: Loading language file from {lang_file}")
                        self.translations = json.load(f)
                    return True
                except Exception as e:
                    print(f"Error loading language file {lang_file}: {e}")
                    continue
            else:
                print(f"Info: Language file not found at {lang_file}")
        
        # 言語ファイルが見つからない場合、デフォルト言語（日本語）を試す
        if lang_code != "ja":
            print(f"Warning: Language file for '{lang_code}' not found. Using default language.")
            return self.load_language("ja")
        else:
            print("Error: Default language file not found.")
            return False
    
    def get_text(self, section: str, key: str, default: Optional[str] = None, *args) -> str:
        """
        指定されたセクションとキーに対応するテキストを取得
        
        Args:
            section: セクション名（例: "ui.messages"）
            key: キー名
            default: デフォルト値（テキストが見つからない場合）
            *args: フォーマット引数
            
        Returns:
            str: 翻訳されたテキスト
        """
        # セクションをドットで分割して階層的にアクセス
        parts = section.split('.')
        current = self.translations
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return default if default is not None else key
        
        if key in current:
            text = current[key]
            
            # 引数がある場合はフォーマット
            if args:
                try:
                    return text.format(*args)
                except Exception:
                    return text
            return text
        
        return default if default is not None else key


# シングルトンインスタンス
_instance = None

def get_language_manager(lang_code: Optional[str] = None) -> LanguageManager:
    """
    言語マネージャーのシングルトンインスタンスを取得
    
    Args:
        lang_code: 言語コード（指定された場合は言語を再ロード）
        
    Returns:
        LanguageManager: 言語マネージャーのインスタンス
    """
    global _instance
    if _instance is None:
        _instance = LanguageManager(lang_code or "ja")
    elif lang_code is not None and lang_code != _instance.lang_code:
        _instance.load_language(lang_code)
    return _instance


def get_text(section: str, key: str, default: Optional[str] = None, *args) -> str:
    """
    指定されたセクションとキーに対応するテキストを取得（ショートカット関数）
    
    Args:
        section: セクション名（例: "ui.messages"）
        key: キー名
        default: デフォルト値（テキストが見つからない場合）
        *args: フォーマット引数
        
    Returns:
        str: 翻訳されたテキスト
    """
    return get_language_manager().get_text(section, key, default, *args) 