from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.app import MDApp
from kivymd.toast import toast


from app.storage.data_store import ensure_live_file, load_data, save_data
from app.storage.license import max_cars


import json
import os

BLU_NOTTE = get_color_from_hex("0D1B2A")  # colore uniforme di EasyAuto
BORDER_BLU = (0.12, 0.25, 0.45, 1)

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
            elevation=0,                 # ✅ niente ombra
            style="outlined",            # ✅ bordo
            line_color=BORDER_BLU,
            line_width=1.4,

            md_bg_color=(1, 1, 1, 1)

        )

                # ---------- IMMAGINE TACHIMETRO ----------
      

        # ---------- TITOLO + BACK ----------
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(40),
            spacing=dp(10)
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            icon_size=dp(28),
            on_release=lambda x: self.go_back()

        )

        title = MDLabel(
            text="Aggiungi Auto",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )

        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(MDLabel(size_hint=(0.3, 1)))  # bilanciamento

        card.add_widget(header)




        # ---------- CAMPI ----------
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

        # ---------- SALVA ----------
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

    # ------------ LOGICA CAMPI OBBLIGATORI -------------
    def check_required_fields(self, *args):
        modello_ok = bool(self.modello.text.strip())
        km_ok = bool(self.km.text.strip())
        self.btn_save.disabled = not (modello_ok and km_ok)

    def reset_fields(self):
        self.marca.text = ""
        self.modello.text = ""
        self.targa.text = ""
        self.km.text = ""
        self.anno.text = ""
        self.btn_save.disabled = True

    def go_back(self):
        self.reset_fields()
        self.manager.current = "mycars"



    # ------------ SALVATAGGIO AUTO (VERSIONE PRO + COLORI) ------------

    def save_auto(self, *args):
        ensure_live_file()
        data = load_data()
        autos = data.get("autos", [])

        limit = max_cars()
        if len(autos) >= limit:
            toast("FREE: 1 auto. Sblocca PRO per arrivare a 10.")
            return

        # --- Assegna colore tachimetro automaticamente ---
        app = MDApp.get_running_app()
        auto_color = app.genera_colore_tachimetro(len(autos))

        new_auto = {
            "marca": self.marca.text.strip(),
            "modello": self.modello.text.strip(),
            "targa": self.targa.text.strip(),
            "km": int(self.km.text.strip()),
            "anno": self.anno.text.strip(),
            "scadenze": {},
            "tacho_color": auto_color
        }

        autos.append(new_auto)
        data["autos"] = autos
        save_data(data)

        self.reset_fields()
        self.manager.current = "mycars"
