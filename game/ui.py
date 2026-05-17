import pygame
import sys
import os
from typing import Optional

from game.card import Card, draw_unique_cards
from game.check import validate_expression
from game.count import Timer

pygame.init()

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
FPS = 60

BACKGROUND_COLOR = (26, 77, 46)
BUTTON_COLOR = (200, 50, 50)
BUTTON_HOVER_COLOR = (220, 70, 70)
BUTTON_TEXT_COLOR = (255, 255, 255)
INPUT_BG_COLOR = (255, 255, 255)
INPUT_TEXT_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
ERROR_COLOR = (255, 100, 100)
SUCCESS_COLOR = (100, 255, 100)
CARD_BG = (255, 255, 255)
CARD_RED = (200, 0, 0)
CARD_BLACK = (0, 0, 0)

STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_RESULT = 'result'


def get_font(size: int) -> pygame.font.Font:
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simhei.ttf',
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.SysFont('arial', size)


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font_size: int = 28):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = get_font(font_size)
        self.hover = False

    def draw(self, screen: pygame.Surface):
        color = BUTTON_HOVER_COLOR if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (150, 30, 30), self.rect, 3, border_radius=12)
        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class InputBox:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.font = get_font(32)
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                char = event.unicode
                if char:
                    self.text += char

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, INPUT_BG_COLOR, self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 3, border_radius=8)

        text_surf = self.font.render(self.text, True, INPUT_TEXT_COLOR)
        screen.blit(text_surf, (self.rect.x + 15, self.rect.y + 10))

        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 15 + text_surf.get_width() + 3
            pygame.draw.line(screen, (0, 0, 0),
                             (cursor_x, self.rect.y + 10),
                             (cursor_x, self.rect.y + self.rect.height - 10), 2)

    def get_text(self) -> str:
        return self.text

    def clear(self):
        self.text = ''


def draw_card(screen: pygame.Surface, card: Card, x: int, y: int, width: int = 100, height: int = 150):
    pygame.draw.rect(screen, CARD_BG, (x, y, width, height), border_radius=10)
    pygame.draw.rect(screen, (150, 150, 150), (x, y, width, height), 3, border_radius=10)

    is_red = card.suit in ['♥', '♦']
    color = CARD_RED if is_red else CARD_BLACK

    font_lg = get_font(42)
    font_sm = get_font(22)

    display_val = card.display_value()

    top_text = font_sm.render(display_val, True, color)
    screen.blit(top_text, (x + 10, y + 8))

    top_suit = font_sm.render(card.suit, True, color)
    screen.blit(top_suit, (x + 10, y + 30))

    center_suit = font_lg.render(card.suit, True, color)
    center_rect = center_suit.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(center_suit, center_rect)

    bottom_text = font_sm.render(display_val, True, color)
    bottom_text = pygame.transform.rotate(bottom_text, 180)
    screen.blit(bottom_text, (x + width - 10 - bottom_text.get_width(), y + height - 8 - bottom_text.get_height()))

    bottom_suit = font_sm.render(card.suit, True, color)
    bottom_suit = pygame.transform.rotate(bottom_suit, 180)
    screen.blit(bottom_suit, (x + width - 10 - bottom_suit.get_width(), y + height - 30 - bottom_suit.get_height()))


class GameUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('24点游戏')
        self.clock = pygame.time.Clock()
        self.state = STATE_MENU

        self.cards: list[Card] = []
        self.timer = Timer()
        self.input_box = InputBox(200, 420, 500, 55)
        self.error_message: Optional[str] = None
        self.success_expression: str = ''
        self.final_time: float = 0.0

        self.start_button = Button(WINDOW_WIDTH // 2 - 100, 480, 200, 60, '开始游戏', 32)
        self.submit_button = Button(WINDOW_WIDTH // 2 - 80, 500, 160, 55, '提交答案', 26)
        self.back_button = Button(WINDOW_WIDTH // 2 - 80, 500, 160, 55, '返回首页', 26)

        self._current_time = 0.0

    def _timer_callback(self, elapsed: float):
        self._current_time = elapsed

    def start_game(self):
        self.cards = draw_unique_cards(4)
        self.timer = Timer(self._timer_callback)
        self.timer.start()
        self.input_box.clear()
        self.error_message = None
        self.state = STATE_PLAYING
        self._current_time = 0.0

    def submit_answer(self):
        expression = self.input_box.get_text().strip()
        if not expression:
            self.error_message = '请输入算式'
            return

        card_values = [card.value for card in self.cards]
        is_valid, message = validate_expression(expression, card_values)

        if is_valid:
            self.timer.pause()
            self.final_time = self.timer.get_elapsed()
            self.timer.stop()
            self.success_expression = expression
            self.state = STATE_RESULT
        else:
            self.error_message = message

    def go_to_menu(self):
        self.timer.stop()
        self.state = STATE_MENU

    def draw_menu(self):
        title_font = get_font(72)
        desc_font = get_font(28)
        info_font = get_font(22)

        title = title_font.render('24点游戏', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        descriptions = [
            '游戏规则：',
            '使用4张扑克牌的数字，通过加减乘除和括号组成算式',
            '每张牌的数字只能使用一次，最终结果必须等于24',
            'A=1, J=11, Q=12, K=13',
            '',
            '输入示例：(3 + 5) * (8 - 5) = 24'
        ]

        y = 200
        for desc in descriptions:
            text = desc_font.render(desc, True, TEXT_COLOR)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 42

        self.start_button.draw(self.screen)

        hint = info_font.render('按 ESC 键退出游戏', True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(hint, hint_rect)

    def draw_playing(self):
        title_font = get_font(36)
        timer_font = get_font(32)
        hint_font = get_font(20)

        title = title_font.render('请组成等于24的算式', True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        time_str = Timer.format_time(self._current_time)
        timer_text = timer_font.render(f'用时: {time_str}', True, TEXT_COLOR)
        timer_rect = timer_text.get_rect(center=(WINDOW_WIDTH // 2, 110))
        self.screen.blit(timer_text, timer_rect)

        card_width = 110
        card_height = 165
        spacing = 30
        total_width = card_width * 4 + spacing * 3
        start_x = (WINDOW_WIDTH - total_width) // 2
        card_y = 170

        for i, card in enumerate(self.cards):
            x = start_x + i * (card_width + spacing)
            draw_card(self.screen, card, x, card_y, card_width, card_height)

        values_str = ', '.join([str(c.value) for c in self.cards])
        values_text = hint_font.render(f'可用数字: {values_str}', True, (220, 220, 220))
        values_rect = values_text.get_rect(center=(WINDOW_WIDTH // 2, 370))
        self.screen.blit(values_text, values_rect)

        hint_text = hint_font.render('输入算式（仅支持 数字 + - * / ( ) 空格）', True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, 400))
        self.screen.blit(hint_text, hint_rect)

        self.input_box.draw(self.screen)

        if self.error_message:
            error_font = get_font(24)
            error_text = error_font.render(self.error_message, True, ERROR_COLOR)
            error_rect = error_text.get_rect(center=(WINDOW_WIDTH // 2, 575))
            self.screen.blit(error_text, error_rect)

        self.submit_button.draw(self.screen)

    def draw_result(self):
        title_font = get_font(56)
        content_font = get_font(28)
        small_font = get_font(24)

        title = title_font.render('🎉 恭喜通关！', True, SUCCESS_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        card_width = 90
        card_height = 135
        spacing = 25
        total_width = card_width * 4 + spacing * 3
        start_x = (WINDOW_WIDTH - total_width) // 2
        card_y = 160

        for i, card in enumerate(self.cards):
            x = start_x + i * (card_width + spacing)
            draw_card(self.screen, card, x, card_y, card_width, card_height)

        expr_label = content_font.render('你的算式:', True, TEXT_COLOR)
        expr_label_rect = expr_label.get_rect(center=(WINDOW_WIDTH // 2, 335))
        self.screen.blit(expr_label, expr_label_rect)

        expr_text = content_font.render(f'{self.success_expression} = 24', True, (255, 255, 150))
        expr_rect = expr_text.get_rect(center=(WINDOW_WIDTH // 2, 375))
        self.screen.blit(expr_text, expr_rect)

        time_label = content_font.render('用时:', True, TEXT_COLOR)
        time_label_rect = time_label.get_rect(center=(WINDOW_WIDTH // 2, 430))
        self.screen.blit(time_label, time_label_rect)

        time_text = content_font.render(Timer.format_time(self.final_time), True, SUCCESS_COLOR)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH // 2, 470))
        self.screen.blit(time_text, time_rect)

        self.back_button.draw(self.screen)

        hint = small_font.render('按 ESC 退出 | 按返回首页可重新开始游戏', True, (180, 180, 180))
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(hint, hint_rect)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING:
            self.draw_playing()
        elif self.state == STATE_RESULT:
            self.draw_result()
        pygame.display.flip()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.timer.stop()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.timer.stop()
            pygame.quit()
            sys.exit()

        if self.state == STATE_MENU:
            if self.start_button.handle_event(event):
                self.start_game()
        elif self.state == STATE_PLAYING:
            self.input_box.handle_event(event)
            if self.submit_button.handle_event(event):
                self.submit_answer()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.submit_answer()
        elif self.state == STATE_RESULT:
            if self.back_button.handle_event(event):
                self.go_to_menu()

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            self.clock.tick(FPS)
