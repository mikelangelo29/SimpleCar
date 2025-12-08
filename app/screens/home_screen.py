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
            height=dp(220),
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
        root.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(10)))

        # --------------------------
        # BOTTONE
        # --------------------------
        btn_mie = MDRaisedButton(
            text="Le mie Auto",
            md_bg_color=blu_notte,
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            height=dp(60),            # un po' più alto
            padding=(dp(75), dp(18)), # <-- qui si allarga davvero
            font_size="18sp",         # leggermente più grande
            elevation=3,
            pos_hint={"center_x": 0.5}
        )
        btn_mie.bind(on_release=lambda x: setattr(self.manager, "current", "mycars"))

        btn_anchor = MDAnchorLayout(anchor_x="center")
        btn_anchor.add_widget(btn_mie)
        root.add_widget(btn_anchor)


        # SPAZIO FISSO 70dp
        root.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(30)))

        # --------------------------
        # STRADA
        # --------------------------
        strada = Image(
            source="app/assets/strada_s.png",
            size_hint=(1, None),
            height=dp(260),
            keep_ratio=True,
            allow_stretch=True
        )
        strada_anchor = MDAnchorLayout(anchor_y="bottom")
        strada_anchor.add_widget(strada)
        root.add_widget(strada_anchor)
                # -----
       # ---------- FRAME CON BORDO ----------
        frame = MDBoxLayout(
            orientation="vertical",
            padding=dp(12),      # distanza bordo-contenuto
        )

        # Disegno del bordo blu notte
        with frame.canvas.before:
            from kivy.graphics import Color, Line
            Color(13/255, 27/255, 42/255, 1)  # BLU NOTTE
            self.frame_border = Line(rounded_rectangle=(0, 0, 0, 0, 20), width=1.4)

        # aggiorna la cornice ogni volta che cambia la finestra
        frame.bind(pos=self._update_border, size=self._update_border)

        # Inseriamo root dentro frame
        frame.add_widget(root)

        # Aggiungiamo frame alla Home
        self.add_widget(frame)


    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _update_border(self, *args):
        # margine dal bordo finestra
        offset = 10

        x = self.x + offset
        y = self.y + offset
        w = self.width - offset * 2
        h = self.height - offset * 2

        # radius 20 = bordi arrotondati più eleganti
        self.frame_border.rounded_rectangle = (x, y, w, h, 20)

