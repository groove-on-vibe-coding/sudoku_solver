class EventManager:
    """
    イベント駆動型アーキテクチャのためのイベント管理クラス
    モジュール間の直接的な依存関係を減らすために使用
    """
    
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event_type, listener):
        """
        特定のイベントタイプに対してリスナー（コールバック関数）を登録
        
        Args:
            event_type (str): イベントの種類を示す文字列
            listener (callable): イベント発生時に呼び出される関数
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        if listener not in self.listeners[event_type]:
            self.listeners[event_type].append(listener)
    
    def unsubscribe(self, event_type, listener):
        """
        登録済みのリスナーを削除
        
        Args:
            event_type (str): イベントの種類
            listener (callable): 削除するリスナー関数
        """
        if event_type in self.listeners and listener in self.listeners[event_type]:
            self.listeners[event_type].remove(listener)
    
    def notify(self, event_type, *args, **kwargs):
        """
        登録されたすべてのリスナーに通知（イベント発火）
        
        Args:
            event_type (str): 発火するイベントの種類
            *args, **kwargs: リスナー関数に渡される引数
        """
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener(*args, **kwargs)
