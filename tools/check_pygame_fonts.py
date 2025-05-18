import pygame

pygame.init()

# フォント名リストを取得して並び替え
available_fonts = sorted(pygame.font.get_fonts())

# 出力
for font in available_fonts:
    print(font)

pygame.quit()
