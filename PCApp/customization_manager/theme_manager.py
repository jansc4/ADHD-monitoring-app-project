import json
from pathlib import Path
import re
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt, QByteArray

from customization_manager.settings_manager import SettingsManager
from customization_manager.strings_manager import StringsManager


class ThemeManager:
    """
    Klasa zarządzająca motywami kolorystycznymi w aplikacji PyQt6.
    Obsługuje kolory w formacie HEX (z opcjonalnym kanałem alpha) oraz konwertuje je do RGBA.
    """

    def __init__(self, settings_manager: SettingsManager, strings: StringsManager):
        """
        Inicjalizuje ThemeManager, wczytując plik JSON z motywem kolorów.

        :param theme_name: Nazwa motywu (plik {theme_name}.json w katalogu themes).
        """
        self.settings = settings_manager
        self.strings = strings
        self.load_theme()

    def load_theme(self):
        self.theme_name = self.settings.get("theme")
        base_dir = Path(__file__).resolve().parent.parent
        theme_path = base_dir / 'themes' / f'{self.theme_name}.json'
        with open(theme_path, 'r') as f:
            self.colors = json.load(f)


    def apply_theme(self, app):
        self.load_theme()
        self.strings.load_language()
        base_dir = Path(__file__).resolve().parent.parent
        style_path = base_dir / 'themes' / 'stylesheet.qss'
        with open(style_path, "r", encoding="utf-8") as f:
            raw_css = f.read()
        styled_css = self.apply_to_stylesheet(raw_css)
        app.setStyleSheet(styled_css)

    def _get_color(self, key, fallback='#FFFFFF'):
        """
        Zwraca kolor z motywu, przetwarzając HEX z alpha na rgba.
        Obsługuje wartości 'none', 'transparent' i brakujące klucze.
        """
        value = self.colors.get(key, fallback)

        if value is None:
            return fallback

        if isinstance(value, str):
            if value.lower() in {"none", "transparent"}:
                return value
            if value.startswith('#') and len(value) == 9:
                return self._hex_to_rgba(value)
            return value

        return fallback


    def apply_to_stylesheet(self, stylesheet: str) -> str:
        """
        Wstawia kolory do stylu QSS, konwertując HEX z alpha na rgba().
        """
        formatted_colors = {}

        for key, value in self.colors.items():
            if value is None:
                continue
            if isinstance(value, str) and value.startswith('#') and len(value) == 9:
                formatted_colors[key] = self._hex_to_rgba(value)
            else:
                formatted_colors[key] = value
        font_size = self.settings.get("font_size")
        if isinstance(font_size, int):
            font_size = f"{font_size}px"
        formatted_colors["font_family"] = self.settings.get("font_family")
        formatted_colors["font_size"] = font_size

        try:
            return stylesheet.format(**formatted_colors)
        except KeyError as e:
            print(f"[ThemeManager] Brak klucza w stylach: {e}")
            return stylesheet


    def colored_svg_icon(self, path, color_key='text', size=24, customColor=False):
        """
        Wczytuje plik SVG i zamienia kolor fill na wskazany z motywu.

        :param path: Ścieżka do pliku SVG.
        :param color_key: Klucz koloru z motywu.
        :param size: Rozmiar ikony.
        :param customColor: Jeśli True, traktuje `color_key` jako wartość koloru.
        :return: QIcon z pokolorowaną ikoną.
        """
        color = color_key if customColor else self._get_color(color_key)

        if color.startswith("rgba"):
            hex_color, alpha = self._rgba_to_svg_components(color)
        else:
            hex_color = color
            alpha = "1.0"

        with open(path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        svg_colored = svg_content.replace('fill="#000000"', f'fill="{hex_color}" fill-opacity="{alpha}"')

        renderer = QSvgRenderer(QByteArray(svg_colored.encode("utf-8")))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _hex_to_rgba(self, hex_color_with_alpha_channel):
        """
        Konwertuje HEX z kanałem alpha (#RRGGBBAA) na rgba().

        :param hex_color_with_alpha_channel: Kolor HEX z kanałem alpha.
        :return: Tekst rgba(R, G, B, A).
        """
        hex_color = hex_color_with_alpha_channel.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)
        return f"rgba({r}, {g}, {b}, {a})"

    def _rgba_to_hex(self, rgba_string):
        """
        Konwertuje rgba(R, G, B, A) na HEX bez alpha (#RRGGBB).

        :param rgba_string: Tekst rgba().
        :return: HEX bez kanału alpha.
        """
        match = re.match(r'rgba?\(\s*(\d+),\s*(\d+),\s*(\d+)(?:,\s*\d+)?\s*\)', rgba_string)
        if not match:
            raise ValueError("Nieprawidłowy format RGBA")
        r, g, b = map(int, match.groups()[:3])
        return f'#{r:02x}{g:02x}{b:02x}'

    def _rgba_to_svg_components(self, rgba_string):
        """
        Rozdziela rgba() na HEX oraz przezroczystość SVG (fill-opacity).

        :param rgba_string: Tekst rgba(R, G, B, A).
        :return: (HEX, fill-opacity).
        """
        match = re.match(r'rgba?\(\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\)', rgba_string)
        if not match:
            raise ValueError("Nieprawidłowy format RGBA")
        r, g, b, a = map(int, match.groups())
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        fill_opacity = f'{a / 255:.2f}'
        return hex_color, fill_opacity
