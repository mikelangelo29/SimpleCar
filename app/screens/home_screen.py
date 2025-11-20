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

        # ---------- SFONDO HOME ----------
        with self.canvas.before:
            Color(0.949, 0.957, 0.969, 1)  # #F2F4F7
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            padding=dp(30)
        )

        # ---------- LOGO CENTRATO, SENZA SFONDO ----------
        logo_container = MDAnchorLayout(
            anchor_x="center",
            anchor_y="top",
            size_hint=(1, None),
            height=dp(150),
            md_bg_color=(0, 0, 0, 0)  # completamente trasparente
        )

        logo = Image(
            source="app/assets/logo_home.png",
            size_hint=(None, None),
            size=(dp(230), dp(230)),
            allow_stretch=False,   # niente stiramenti
            keep_ratio=True,
            mipmap=True
        )

        logo_container.add_widget(logo)
        layout.add_widget(logo_container)

        # ---------- SOTTOTITOLO ----------
        layout.add_widget(
            MDLabel(
                text="[i]Scadenze Macchina[/i]",
                markup=True,
                halign="center",
                theme_text_color="Custom",
                text_color=(0.1, 0.15, 0.25, 1),
                font_size="25sp" 
            )
        )


        # ---------- COLORI ----------
        blu_notte = (13/255, 27/255, 42/255, 1)

        # ---------- PULSANTE: Aggiungi Auto ----------
        btn_add = MDRaisedButton(
            text="Aggiungi Auto",
            size_hint=(0.6, None),
            height=dp(50),
            pos_hint={"center_x": 0.5},
            md_bg_color=blu_notte,
            text_color=(1, 1, 1, 1),
            radius=[12, 12, 12, 12],
            elevation=3
        )
       
        # CLICK TEST
        print("Bind attivo su Aggiungi Auto")

        btn_add.bind(
            on_release=lambda x: setattr(self.manager, "current", "add_auto")
        )

        layout.add_widget(btn_add)
        

        # ---------- PULSANTE: Le mie Auto ----------
        btn_mie = MDRaisedButton(
            text="Le mie Auto",
            size_hint=(0.6, None),
            height=dp(50),
            pos_hint={"center_x": 0.5},
            md_bg_color=blu_notte,
            text_color=(1, 1, 1, 1),
            radius=[12, 12, 12, 12],
            elevation=3
        )
        layout.add_widget(btn_mie)

        # ---------- SPAZIO FINALE ----------
        layout.add_widget(MDWidget())

        # ---------- BOTTONE INFO ----------
        info_box = MDAnchorLayout(anchor_x="center", anchor_y="bottom")
        info_btn = MDRoundFlatIconButton(
            icon="information-outline",
            text="Info",
            size_hint=(None, None),
            width=dp(140),
            height=dp(45),
            text_color=(0, 0, 0, 1)
        )
        info_box.add_widget(info_btn)
        layout.add_widget(info_box)

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
