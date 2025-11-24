from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from pathlib import Path
import json
import os
from app.screens.gomme_screen import GommeScreen




# ------------------------- PALETTE -------------------------
BLU_NOTTE = get_color_from_hex("0D1B2A")
GRIGIO_SFONDO = (0.94, 0.95, 0.96, 1)
GRIGIO_HEADER = (0.90, 0.91, 0.93, 1)
GRIGIO_CARD = (0.965, 0.965, 0.97, 1)

# ------------------------- PATHS ---------------------------
DATA_PATH = "app/data/autos.json"
IMG_TYRE = str(Path(__file__).parent.parent / "assets" / "tyre.png")


class DetailAutoScreen(MDScreen):

    def on_pre_enter(self):
        self.clear_widgets()
        self.load_auto()
        self.build_ui()

    # ---------------------------------------------------------
    # LOAD AUTO
    # ---------------------------------------------------------
    def load_auto(self):
        if not os.path.exists(DATA_PATH):
            self.auto = None
            return

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])
        self.auto = autos[0] if autos else None

        if "scadenze" not in self.auto:
            self.auto["scadenze"] = {}

    # ---------------------------------------------------------
    # BUILD UI
    # ---------------------------------------------------------
    def build_ui(self):

        self.md_bg_color = GRIGIO_SFONDO

        scroll = MDScrollView()
        root = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(15),
            size_hint_y=None
        )
        root.bind(minimum_height=root.setter("height"))
        scroll.add_widget(root)
        self.add_widget(scroll)

        # ======================================================
        # HEADER AUTO
        # ======================================================
        nome_auto = (self.auto.get("marca", "") + " " + self.auto.get("modello", "")).strip()
        km = self.auto.get("km", 0)

        header = MDCard(
            orientation="vertical",
            padding=dp(20),
            size_hint=(1, None),
            height=dp(160),
            radius=[22, 22, 22, 22],
            elevation=4,
            md_bg_color=GRIGIO_HEADER
        )

        lab_nome = MDLabel(
            text=nome_auto,
            font_style="H5",
            halign="left",
            theme_text_color="Custom",
            text_color=BLU_NOTTE
        )
        lab_km = MDLabel(text=f"Km attuali: {km}", theme_text_color="Secondary", halign="left")

        # tappabile per aggiornamento km
        lab_km.bind(on_touch_down=lambda w, t: self.open_update_km_dialog()
                    if lab_km.collide_point(t.x, t.y) else False)

        header.add_widget(lab_nome)
        header.add_widget(lab_km)
        root.add_widget(header)

        # ======================================================
        # SCADENZE TECNICHE
        # ======================================================
        root.add_widget(self.section_title("📘  SCADENZE TECNICHE"))

        tecnici = [
            ("Tagliando",            "tagliando",        "tune"),
            ("Revisione",            "revisione",         "clipboard-check"),
            ("Gomme",                "gomme",             "tyre"),  # ICONA PNEUMATICO
            ("Dischi freno",         "dischi",            "disc"),
            ("Pastiglie freno",      "pastiglie",         "car-brake-alert"),
            ("Ammortizzatori",       "ammortizzatori",    "car-defrost-rear"),
            ("Cinghia distribuzione","cinghia",           "cog-transfer"),
            ("Batteria",             "batteria",          "car-battery"),
        ]

        for nome, key, icon in tecnici:
            root.add_widget(self.param_card(nome, key, icon))

        # ======================================================
        # SCADENZE AMMINISTRATIVE
        # ======================================================
        root.add_widget(self.section_title("🧾  SCADENZE AMMINISTRATIVE"))

        amministrative = [
            ("Assicurazione", "assicurazione", "shield-car"),
            ("Bollo",         "bollo",         "cash"),
            ("Multe",         "multe",         "police-badge-outline")
        ]

        for nome, key, icon in amministrative:
            root.add_widget(self.param_card(nome, key, icon))

        # ======================================================
        # SPAZIO PER EVITARE CHE IL FOOTER COPRA LE CARD
        # ======================================================
        root.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(80)))

        # ======================================================
        # FOOTER BLU NOTTE
        # ======================================================
        footer = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            md_bg_color=BLU_NOTTE,
            padding=(dp(15), dp(10))
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            icon_size=dp(32),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=lambda x: setattr(self.manager, "current", "mycars")
        )

        footer.add_widget(back_btn)
        self.add_widget(footer)

    # ---------------------------------------------------------
    # SECTION TITLE
    # ---------------------------------------------------------
    def section_title(self, text):
        box = MDBoxLayout(orientation="vertical", size_hint=(1, None), height=dp(45))
        lbl = MDLabel(text=text, font_style="H6", theme_text_color="Secondary")
        sep = MDBoxLayout(size_hint=(1, None), height=dp(1), md_bg_color=(0.75, 0.75, 0.78, 1))
        box.add_widget(lbl)
        box.add_widget(sep)
        return box

    # ---------------------------------------------------------
    # PARAMETER CARD (uguale per tutto, comprese gomme)
    # ---------------------------------------------------------
    def param_card(self, title, key, icon):

        sc = self.auto["scadenze"].get(key, {})
        ultimo = sc.get("ultimo", "—")
        prossimo = sc.get("prossimo", "—")
        stato = sc.get("stato", "⚪")

        card = MDCard(
            orientation="horizontal",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(120),
            radius=[18, 18, 18, 18],
            elevation=3,
            ripple_behavior=True,
            md_bg_color=GRIGIO_CARD,
            on_release=lambda x: self.open_item(key)
        )

        # ICONA → Se “gomme”, usare PNG
        if key == "gomme":
            icona = Image(
                source=IMG_TYRE,
                size_hint=(None, None),
                size=(dp(50), dp(50)),
                pos_hint={"center_y": 0.5}
            )
        else:
            icona = MDIconButton(
                icon=icon,
                icon_size=dp(30),
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                pos_hint={"center_y": 0.5}
            )

        col = MDBoxLayout(orientation="vertical", spacing=dp(3))
        col.add_widget(MDLabel(text=title, font_style="H6"))
        col.add_widget(MDLabel(text=f"Ultimo: {ultimo}", theme_text_color="Secondary"))
        col.add_widget(MDLabel(text=f"Prossimo: {prossimo}", theme_text_color="Secondary"))
        col.add_widget(MDLabel(text=f"Stato: {stato}", theme_text_color="Secondary"))

        card.add_widget(icona)
        card.add_widget(col)

        return card

    # ---------------------------------------------------------
    # OPENERS
    # ---------------------------------------------------------
    def open_item(self, key):
        if key == "gomme":
            self.manager.current = "gomme"
        else:
            print(f"APRI POPUP → {key}")


    def open_update_km_dialog(self):
        print("Popup aggiornamento km (da fare)")
