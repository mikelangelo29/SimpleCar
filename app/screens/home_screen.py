from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.graphics import Color as KColor, Rectangle


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        blu_notte = (13/255, 27/255, 42/255, 1)

        # SFONDO
        with self.canvas.before:
            KColor(0.949, 0.957, 0.969, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # ROOT
        root = MDBoxLayout(
            orientation="vertical",
            padding=(0, dp(25), 0, dp(25)),
            spacing=dp(0)
        )

        # --------------------------
        # LOGO
        # --------------------------
        logo = Image(
            source="app/assets/logo_home.png",
            size_hint=(1, None),
            height=dp(150),
            keep_ratio=True,
            allow_stretch=True
        )
        root.add_widget(logo)

        # SPAZIO FISSO 20dp
        root.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(5)))

        # --------------------------
        # PAYOFF
        # --------------------------
        payoff = MDLabel(
            text="[i]Le scadenze della tua macchina[/i]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=blu_notte,
            font_size="17sp",
            size_hint=(1, None),
            height=dp(30)
        )
        root.add_widget(payoff)

        # SPAZIO FISSO 50dp
        root.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(20)))

        # --------------------------
        # BOTTONE
        # --------------------------
        btn_mie = MDRaisedButton(
            text="Le mie Auto",
            md_bg_color=blu_notte,
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            height=dp(60),            # un po' più alto
            padding=(dp(55), dp(14)), # <-- qui si allarga davvero
            font_size="17sp",         # leggermente più grande
            elevation=3,
            pos_hint={"center_x": 0.5}
        )
        btn_mie.bind(on_release=lambda x: setattr(self.manager, "current", "mycars"))

        btn_anchor = MDAnchorLayout(anchor_x="center")
        btn_anchor.add_widget(btn_mie)
        root.add_widget(btn_anchor)


        # SPAZIO FISSO 70dp
        root.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(70)))

        # --------------------------
        # STRADA
        # --------------------------
        strada = Image(
            source="app/assets/strada_s.png",
            size_hint=(1, None),
            height=dp(230),
            keep_ratio=True,
            allow_stretch=True
        )
        root.add_widget(strada)

        # -----
        self.add_widget(root)


    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
