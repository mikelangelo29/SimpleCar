from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import json
import os

BLU_NOTTE = get_color_from_hex("0D1B2A")  # colore uniforme di EasyAuto


class AddAutoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ROOT
        root = MDAnchorLayout(anchor_x="center", anchor_y="center")

        # ---------- CARD ----------
        card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(18),
            size_hint=(0.88, None),
            height=dp(540),
            elevation=6,
            md_bg_color=(1, 1, 1, 1)
        )

        # ---------- TITOLO + BACK ----------
        header = MDBoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(40), spacing=dp(10))
        back_btn = MDIconButton(
            icon="arrow-left",
            icon_size=dp(28),
            on_release=lambda x: setattr(self.manager, "current", "home")
        )
        title = MDLabel(
            text="Aggiungi Auto",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )

        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(MDLabel(size_hint=(0.3, 1)))  # per bilanciare lo spazio a destra
        card.add_widget(header)

        # ---------- CAMPI CON ICONE ----------
        self.marca = MDTextField(
            hint_text="Marca (opzionale)",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55),
            icon_left="car",
        )
        card.add_widget(self.marca)

        self.modello = MDTextField(
            hint_text="Modello *",
            helper_text="obbligatorio",
            helper_text_mode="on_focus",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55),
            icon_left="form-textbox",
        )
        self.modello.bind(text=self.check_required_fields)
        card.add_widget(self.modello)

        self.targa = MDTextField(
            hint_text="Targa (opzionale)",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55),
            icon_left="tag",
        )
        card.add_widget(self.targa)

        self.km = MDTextField(
        hint_text="Chilometraggio *",
        helper_text="obbligatorio",
        helper_text_mode="on_focus",
        mode="rectangle",
        size_hint=(1, None),
        height=dp(55),
        input_filter="int",
        icon_left="speedometer",
    )
        self.km.bind(text=self.check_required_fields)

        card.add_widget(self.km)

        self.anno = MDTextField(
            hint_text="Anno immatricolazione (opzionale)",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55),
            input_filter="int",
            icon_left="calendar",
        )
        card.add_widget(self.anno)

        # ---------- SALVA (disabled all’inizio) ----------
        self.btn_save = MDRaisedButton(
            text="Salva",
            md_bg_color=BLU_NOTTE,
            text_color=(1, 1, 1, 1),
            size_hint=(0.5, None),
            height=dp(50),
            disabled=True,
            on_release=self.save_auto  
        )
        save_box = MDAnchorLayout(anchor_x="center", anchor_y="center")
        save_box.add_widget(self.btn_save)

        card.add_widget(save_box)

        root.add_widget(card)
        self.add_widget(root)

    # ------------ LOGICA DEI CAMPI OBBLIGATORI -------------
    def check_required_fields(self, *args):
        modello_ok = bool(self.modello.text.strip())
        km_ok = bool(self.km.text.strip())

        self.btn_save.disabled = not (modello_ok and km_ok)


    def save_auto(self, *args):
        data_path = "app/data/autos.json"

        # Se il file non esiste → crealo
        if not os.path.exists(data_path):
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump({"autos": []}, f, indent=4)

        # Carica autos.json
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])

        # Versione FREE → massimo 1 auto
        if len(autos) >= 1:
            return  # NON SALVIAMO NULLA

        # Crea nuovo dizionario auto
        new_auto = {
            "marca": self.marca.text.strip(),
            "modello": self.modello.text.strip(),
            "targa": self.targa.text.strip(),
            "km": int(self.km.text.strip()),
            "anno": self.anno.text.strip(),
            "scadenze": {}
        }

        autos.append(new_auto)

        # Salva su file
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump({"autos": autos}, f, indent=4)

        # Torna allo screen “mycars”
        self.manager.current = "mycars"


