from typing import NamedTuple, Tuple

Color = Tuple[int, int, int]


GREEN: Color = (29, 185, 84)  # 1DB954
GREEN_HOVER: Color = (30, 215, 96)  # 1ED760
RED: Color = (233, 20, 41)  # E91429

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)

TEXT_PRIMARY: Color = WHITE
TEXT_SECONDARY: Color = (179, 179, 179)  # B3B3B3

BACKGROUND_BASE: Color = (18, 18, 18)  # 121212
SURFACE_ELEVATED: Color = (40, 40, 40)  # 282828
SURFACE_ELEVATED_HOVER: Color = (62, 62, 62)  # 3E3E3E

GRADIENT_START: Color = (66, 56, 140)
GRADIENT_EDIT: Color = (28, 100, 62)
GRADIENT_PLAY: Color = (122, 40, 58)
GRADIENT_HEIGHT_RATIO = 0.6  # fração da altura da janela ocupada pelo degradê


PILL_RADIUS_RATIO = 0.5  # raio = metade da altura
TEXTBOX_BORDER_RADIUS = 8
TEXTBOX_BORDER_WIDTH = 2

CURSOR_WIDTH = 2
CURSOR_BLINK_PERIOD_MS = 1000  # tempo de um ciclo completo (aceso + apagado)
CURSOR_VISIBLE_MS = 500  # tempo aceso dentro de cada ciclo

SLIDER_TRACK_HEIGHT = 6
SLIDER_KNOB_RADIUS = 10
SLIDER_LABEL_SPACE = 30  # espaço entre o rótulo e a barra


FONT_NAME = None  # fonte padrão do pygame
FONT_SIZE_TITLE = 60
FONT_SIZE_BUTTON = 36
FONT_SIZE_BUTTON_SMALL = 18
FONT_SIZE_TEXTBOX = 24
FONT_SIZE_STATUS = 32
FONT_SIZE_PLAYER = 25


class ButtonStyle(NamedTuple):
    background: Color
    background_hover: Color
    text_color: Color


PRIMARY_BUTTON = ButtonStyle(GREEN, GREEN_HOVER, BLACK)

SECONDARY_BUTTON = ButtonStyle(SURFACE_ELEVATED, SURFACE_ELEVATED_HOVER, WHITE)
