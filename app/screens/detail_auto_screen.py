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




# ------------------------- PALETTE -------------------------
BLU_NOTTE = get_color_from_hex("0D1B2A")
GRIGIO_SFONDO = (0.94, 0.95, 0.96, 1)
GRIGIO_HEADER = (0.90, 0.91, 0.93, 1)
GRIGIO_CARD = (0.965, 0.965, 0.97, 1)

# ------------------------- PATHS ---------------------------
DATA_PATH = "app/data/autos.json"
IMG_TYRE = str(Path(__file__).parent.parent / "assets" / "tyre.png")


class DetailAutoScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0  # <<< fondamentale per multi-auto

    def on_pre_enter(self):
        self.clear_widgets()
        self.load_auto()
        self.build_ui()

    # ---------------------------------------------------------
    # LOAD AUTO — ORA CARICA QUELLA GIUSTA IN BASE A selected_index
    # ---------------------------------------------------------
    def load_auto(self):
        if not os.path.exists(DATA_PATH):
            self.auto = None
            return

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])

        # fallback di sicurezza
        if not autos:
            self.auto = None
            return

        index = self.selected_index
        if index >= len(autos):
            index = 0

        self.auto = autos[index]

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

        # ======================================================
        # HEADER AUTO (con tachimetro)
        # ======================================================
        tacho_color = self.auto.get("tacho_color", "purple")
        tacho_src = f"app/assets/icons/tacho_{tacho_color}.png"

        header = MDCard(
            orientation="horizontal",
            padding=dp(20),
            size_hint=(1, None),
            height=dp(160),
            radius=[22, 22, 22, 22],
            elevation=4,
            md_bg_color=GRIGIO_HEADER
        )

        # --- COLONNA SINISTRA ---
        left_col = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_x=0.65
        )

        left_col.add_widget(
            MDLabel(
                text=nome_auto,
                font_style="H5",
                halign="left",
                theme_text_color="Custom",
                text_color=BLU_NOTTE
            )
        )

        left_col.add_widget(
            MDLabel(
                text=f"Km attuali: {km}",
                theme_text_color="Secondary",
                halign="left"
            )
        )

        # --- COLONNA DESTRA (TACHIMETRO) ---
        tacho_img = Image(
            source=tacho_src,
            size_hint=(None, None),
            size=(dp(110), dp(110)),
            pos_hint={"center_y": 0.5}
        )

        header.add_widget(left_col)
        header.add_widget(tacho_img)
        root.add_widget(header)


        # ======================================================
        # SCADENZE TECNICHE
        # ======================================================
        root.add_widget(self.section_title("📘  SCADENZE TECNICHE"))

        tecnici = [
            ("Tagliando",            "tagliando",        "tune"),
            ("Revisione",            "revisione",         "clipboard-check"),
            ("Gomme",                "gomme",             "tyre"),
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
        # SPAZIO PER EVITARE SOVRAPPOSIZIONI
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
        box = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(45)
        )
        lbl = MDLabel(
            text=text,
            font_style="H6",
            theme_text_color="Secondary"
        )
        sep = MDBoxLayout(
            size_hint=(1, None),
            height=dp(1),
            md_bg_color=(0.75, 0.75, 0.78, 1)
        )
        box.add_widget(lbl)
        box.add_widget(sep)
        return box

    # ---------------------------------------------------------
    # PARAMETER CARD
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

        # Icona speciale per gomme (usa PNG)
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
    # OPENERS (GOMME ecc.)
    # ---------------------------------------------------------
    def open_item(self, key):
        if key == "gomme":
            self.manager.get_screen("gomme").current_auto = self.auto
            self.manager.current = "gomme"
        elif key == "revisione":
            rev_screen = self.manager.get_screen("revisione")
            rev_screen.current_auto = self.auto
            self.manager.current = "revisione"

    
    def update_view(self):
        self.refresh_from_data()


    # ---------------------------------------------------------
    # AGGIORNAMENTO KM (dialog)
    # ---------------------------------------------------------
    def open_update_km_dialog(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField

        self.km_field = MDTextField(
            hint_text="Nuovo chilometraggio",
            text=str(self.auto["km"]),
            input_filter="int",
            mode="rectangle"
        )

        self.dialog_km = MDDialog(
            title="Aggiorna chilometraggio",
            type="custom",
            content_cls=self.km_field,
            buttons=[
                MDIconButton(icon="close", on_release=lambda x: self.dialog_km.dismiss()),
                MDIconButton(icon="check",
                             text_color=BLU_NOTTE,
                             on_release=lambda x: self.save_km())
            ],
        )

        self.dialog_km.open()

    def save_km(self):
        val = self.km_field.text.strip()

        if not val.isdigit():
            self.km_field.error = True
            return

        new_km = int(val)

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["autos"][self.selected_index]["km"] = new_km

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.dialog_km.dismiss()
        self.on_pre_enter()
