import json
import os
import sys
from typing import Dict, Any

def load_ui_settings(filepath: str) -> Dict[str, Any]:
    """UI 設定をファイルから読み込む"""
    # まず、指定されたパスで試す
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            print(f"Info: Loading UI settings from {filepath}")
            return json.load(f)
    except FileNotFoundError:
        print(f"Info: UI settings not found at {filepath}")
        pass
    
    # 次に、実行ファイルと同じディレクトリにある設定ファイルを探す
    try:
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
        exe_config_path = os.path.join(exe_dir, os.path.basename(filepath))
        if os.path.exists(exe_config_path):
            with open(exe_config_path, 'r', encoding='utf-8') as f:
                print(f"Info: Loading UI settings from {exe_config_path}")
                return json.load(f)
        else:
            print(f"Info: UI settings not found at {exe_config_path}")
    except Exception as e:
        print(f"Warning: Error loading UI settings from {exe_config_path}: {e}")
        pass
    
    # 最後に、ソースディレクトリ内の設定ファイルを探す
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        src_config_path = os.path.join(base_path, 'src', os.path.basename(filepath))
        if os.path.exists(src_config_path):
            with open(src_config_path, 'r', encoding='utf-8') as f:
                print(f"Info: Loading UI settings from {src_config_path}")
                return json.load(f)
        else:
            print(f"Info: UI settings not found at {src_config_path}")
    except Exception as e:
        print(f"Warning: Error loading UI settings from {src_config_path}: {e}")
        pass
    
    print(f"Error: Could not find UI settings file.")
    return None
