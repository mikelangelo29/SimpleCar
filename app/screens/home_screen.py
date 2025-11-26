from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.widget import MDWidget
from kivy.uix.image import Image
from kivy.metrics import dp

# IMPORTANTI — DEVONO STARE QUI
from kivy.uix.widget import Widget
from kivy.graphics import Color as KColor, Rectangle


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        blu_notte = (13/255, 27/255, 42/255, 1)

        # ------------------- SFONDO -------------------
        with self.canvas.before:
            KColor(0.949, 0.957, 0.969, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # ------------------- LAYOUT -------------------
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(20), dp(10), dp(20), dp(10))
        )

        # ------------------- LOGO -------------------
        logo = Image(
            source="app/assets/logo_home.png",
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            keep_ratio=True
        )

        logo_anchor = MDAnchorLayout(
            anchor_x="center",
            anchor_y="top",
            size_hint=(1, None),
            height=dp(160),
        )
        logo_anchor.add_widget(logo)
        layout.add_widget(logo_anchor)

        # ------------------- PAYOFF -------------------
        payoff = MDLabel(
            text="[i]Le scadenze della tua macchina[/i]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=blu_notte,
            font_size="18sp",
            size_hint=(1, None),
            height=dp(40),
        )
        layout.add_widget(payoff)

        layout.add_widget(MDWidget(size_hint_y=None, height=dp(35)))

        # ------------------- BOTTONE AUTO -------------------
        btn_mie = MDRaisedButton(
            text="Le mie Auto",
            size_hint=(0.6, None),
            height=dp(50),
            pos_hint={"center_x": 0.5},
            md_bg_color=blu_notte,
            text_color=(1, 1, 1, 1),
            elevation=3,
        )
        btn_mie.bind(on_release=lambda x: setattr(self.manager, "current", "mycars"))
        layout.add_widget(btn_mie)

        # ------------------- IMMAGINE STRADA -------------------
        # ------------------- SPAZIO ELASTICO SOPRA LA STRADA -------------------
        layout.add_widget(MDWidget(size_hint_y=1))

        # ------------------- IMMAGINE STRADA -------------------
        strada_box = MDAnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(1, None),
            height=dp(120)  # ← più elegante, non schiaccia il layout
        )

        strada_img = Image(
            source="app/assets/strada_s.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            height=dp(130)
        )

        strada_box.add_widget(strada_img)
        layout.add_widget(strada_box)



        # ------------------- BOTTONE INFO -------------------
        info_row = MDAnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(1, None),
            height=dp(80)
        )

        info_btn = MDRoundFlatIconButton(
            icon="information-outline",
            text="Info",
            size_hint=(None, None),
            width=dp(140),
            height=dp(45),
            text_color=(0, 0, 0, 1),
        )

        info_row.add_widget(info_btn)
        layout.add_widget(info_row)

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
