from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRoundFlatIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.widget import MDWidget
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Sfondo elegante grigio chiaro
        with self.canvas.before:
            Color(0.949, 0.957, 0.969, 1)  # #F2F4F7
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(30)
        )

        # --- LOGO ---
        logo_wrap = MDAnchorLayout(anchor_x="center", anchor_y="top")
        logo = Image(
            source="app/assets/logo.png",
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            allow_stretch=True,
            keep_ratio=True
        )
        logo_wrap.add_widget(logo)
        layout.add_widget(logo_wrap)

        # --- SPAZIO MAGGIORE (EasyAuto scende di ~2mm) ---
        layout.add_widget(MDWidget(size_hint_y=None, height=dp(55)))

        # --- Blu notte ---
        blu_notte = (13/255, 71/255, 161/255, 1)

        # --- TITOLO APP ---
        layout.add_widget(
            MDLabel(
                text="EasyAuto",
                halign="center",
                font_style="H4",
                theme_text_color="Custom",
                text_color=blu_notte
            )
        )

        # --- SOTTOTITOLO ---
        layout.add_widget(
            MDLabel(
                text="Scadenze Macchina",
                halign="center",
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=(0.2, 0.2, 0.2, 1)
            )
        )

        layout.add_widget(MDWidget(size_hint_y=None, height=dp(25)))

        # --- VERDE PETROLIO ---
        teal = (0/255, 124/255, 145/255, 1)

        # --- PULSANTE: Aggiungi Auto ---
        btn_add = MDRaisedButton(
            text="Aggiungi Auto",
            size_hint=(0.6, None),
            height=dp(50),
            pos_hint={"center_x": 0.5},
            md_bg_color=teal,
            text_color=(1, 1, 1, 1),
            elevation=3
        )
        btn_add.bind(on_release=lambda x: self._go("add_auto"))
        layout.add_widget(btn_add)

        # --- PULSANTE: Le mie Auto ---
        btn_mie = MDRaisedButton(
            text="Le mie Auto",
            size_hint=(0.6, None),
            height=dp(50),
            pos_hint={"center_x": 0.5},
            md_bg_color=teal,
            text_color=(1, 1, 1, 1),
            elevation=3
        )
        btn_mie.bind(on_release=lambda x: self._go("mie_auto"))
        layout.add_widget(btn_mie)

        layout.add_widget(MDWidget())

        # --- INFO ---
        info_wrap = MDAnchorLayout(anchor_x="center", anchor_y="bottom")
        info_btn = MDRoundFlatIconButton(
            icon="information-outline",
            text="Info",
            size_hint=(None, None),
            width=dp(140),
            height=dp(45),
            text_color=(0, 0, 0, 1)
        )
        info_wrap.add_widget(info_btn)
        layout.add_widget(info_wrap)

        self.add_widget(layout)

    def _go(self, screen_name):
        if self.manager:
            self.manager.current = screen_name

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
