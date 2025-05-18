import pygame
from typing import List, Dict, Any
from board import SudokuBoard
from solver import SudokuSolver
from lang_manager import get_text


class SudokuRenderer:
    """数独を描画するためのクラス"""
    
    def __init__(self, window, board: SudokuBoard, ui_config: Dict[str, Any]):
        self.window = window
        self.board = board
        self.selected_cell = None
        
        self.ui_config = ui_config
        self.colors = ui_config["colors"]
        self.fonts = ui_config["font"]
        self.cell_size = ui_config["cell_size"]
        self.width = ui_config["window"]["width"]
        self.height = ui_config["window"]["height"]
        self.message_area_height = ui_config.get("message_area_height", 50)
        self.origin_x, self.origin_y = ui_config.get("board_origin", [0, 0])
    
    def draw_board(self):
        """盤面を描画"""
        # 背景を塗りつぶす
        self.window.fill(self.colors["background"])
        
        # 各セルを描画
        for i in range(9):
            for j in range(9):
                value = self.board.get_value(i, j)
                cell_color = self.colors["cell_background"] if value != 0 else self.colors["background"]
                x = self.origin_x + j * self.cell_size
                y = self.origin_y + i * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.window, cell_color, rect)
        
        # 選択されたセルを強調表示
        if self.selected_cell:
            row, col = self.selected_cell
            x = self.origin_x + col * self.cell_size
            y = self.origin_y + row * self.cell_size
            rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            pygame.draw.rect(self.window, self.colors["selected_grid"], rect, 3)
        
        # グリッド線を描画
        self._draw_grid_lines()
        
        # 数字を描画
        self._draw_numbers()
    
    def draw_speed_slider(self, slider_rect: pygame.Rect, slider_button_rect: pygame.Rect, solving_speed: int):
        """スライダーを描画"""
        # スライダーの背景とボタンを描画
        pygame.draw.rect(self.window, self.colors["grid"], slider_rect, 1)
        pygame.draw.rect(self.window, self.colors["button"], slider_button_rect)
        pygame.draw.rect(self.window, self.colors["grid"], slider_button_rect, 1)
        
        # スライダーの上に解答速度を表示（1-100 のレンジ）
        # 表示値が1のとき実際の速度が最遅(内部値5000)、表示値が100のとき最速(内部値100)
        display_speed = int(99 - (solving_speed - 100) / 4900 * 99) + 1  # 内部値を1-100に変換
        font = pygame.font.SysFont(self.fonts["default"], self.fonts["speed_size"])
        text = font.render(f"{get_text('renderer', 'solving_speed')}: {display_speed}", True, self.colors["text_default"])
        text_rect = text.get_rect(center=(slider_rect.centerx, slider_rect.top - 20))
        self.window.blit(text, text_rect)
        
        # 「遅い」「速い」のラベルを表示
        slow_text = font.render(get_text("renderer", "slow"), True, self.colors["text_default"])
        fast_text = font.render(get_text("renderer", "fast"), True, self.colors["text_default"])
        
        # 左側に「遅い」、右側に「速い」を配置
        slow_rect = slow_text.get_rect(midright=(slider_rect.left - 10, slider_rect.centery))
        fast_rect = fast_text.get_rect(midleft=(slider_rect.right + 10, slider_rect.centery))
        
        self.window.blit(slow_text, slow_rect)
        self.window.blit(fast_text, fast_rect)
    
    def _draw_grid_lines(self):
        """盤面のグリッド線を描画"""
        for i in range(10):
            width = 2 if i % 3 == 0 else 1
            pygame.draw.line(self.window, self.colors["grid"],
                             (self.origin_x + i * self.cell_size, self.origin_y),
                             (self.origin_x + i * self.cell_size, self.origin_y + 9 * self.cell_size), width)
            pygame.draw.line(self.window, self.colors["grid"],
                             (self.origin_x, self.origin_y + i * self.cell_size),
                             (self.origin_x + 9 * self.cell_size, self.origin_y + i * self.cell_size), width)
    
    def _draw_numbers(self):
        """盤面の数字を描画"""
        font = pygame.font.SysFont(self.fonts["default"], self.fonts["num_size"])
        for i in range(9):
            for j in range(9):
                value = self.board.get_value(i, j)
                if value != 0:
                    color = self.colors["text_default"] if self.board.is_original_cell(i, j) else self.colors["text_added"]
                    text = font.render(str(value), True, color)
                    x = self.origin_x + j * self.cell_size + self.cell_size // 4
                    y = self.origin_y + i * self.cell_size + self.cell_size // 6
                    self.window.blit(text, (x, y))
    
    def show_message(self, message: str, color):
        """メッセージを表示"""
        rect = pygame.Rect(0, self.height - self.message_area_height, self.width, self.message_area_height)
        pygame.draw.rect(self.window, self.colors["message_background"], rect)
        
        font = pygame.font.SysFont(self.fonts["default"], self.fonts["button_size"])
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(self.width // 2, self.height - self.message_area_height // 2))
        self.window.blit(text, text_rect)
        
        pygame.display.update()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False
    
    def set_selected_cell(self, row: int, col: int):
        self.selected_cell = (row, col)
