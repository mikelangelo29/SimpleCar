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

# ✅ NUOVO: usa il data_store (file VIVO)
from app.storage.data_store import load_data, save_data


# ------------------------- PALETTE -------------------------
BLU_NOTTE = get_color_from_hex("0D1B2A")
GRIGIO_SFONDO = (0.94, 0.95, 0.96, 1)
GRIGIO_HEADER = (0.90, 0.91, 0.93, 1)
GRIGIO_CARD = (0.965, 0.965, 0.97, 1)
VERDE_OK = (0.1, 0.6, 0.3, 1)
# ------------------------- PATHS ---------------------------
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
    # LOAD AUTO — ORA CARICA DAL FILE VIVO
    # ---------------------------------------------------------
    def load_auto(self):
        data = load_data()  # ✅ legge dal file VIVO
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
                text=nome_auto.upper(),
                font_style="H5",
                bold=True,
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
            ("Dischi freno",         "dischi_freno",            "disc"),
            ("Pastiglie freno",      "pastiglie_freno",         "car-brake-alert"),
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

    def get_label_ultimo(self, key):
        return {
            "tagliando": "Ultimo intervento",
            "dischi_freno": "Ultima sostituzione",
            "pastiglie_freno": "Ultima sostituzione",
            "ammortizzatori": "Ultima sostituzione",
            "cinghia": "Ultima sostituzione",
            "batteria": "Ultima sostituzione",
            "revisione": "Ultima revisione",
            "bollo": "Ultimo pagamento",
            "assicurazione": "Ultimo rinnovo",
        }.get(key, "Ultimo")

    def get_label_prossimo(self, key):
        return {
            "tagliando": "Prossimo tagliando",
            "revisione": "Prossima revisione",
            "dischi_freno": "Prossima sostituzione",
            "pastiglie_freno": "Prossima sostituzione",
            "ammortizzatori": "Prossima sostituzione",
            "cinghia": "Prossima sostituzione",
            "batteria": "Prossima sostituzione",
            "assicurazione": "Scadenza",
            "bollo": "Scadenza",
        }.get(key, "Prossimo intervento")

    # ---------------------------------------------------------
    # PARAMETER CARD
    # ---------------------------------------------------------
    def param_card(self, title, key, icon):

        sc = self.auto["scadenze"].get(key, {})
        ultimo = sc.get("ultimo", "—")
        prossimo = sc.get("prossimo", "—")
        stato = sc.get("stato", "⚪")

        # --- CARD ---
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

        # --- CONTENUTO ---
        col = MDBoxLayout(orientation="vertical", spacing=dp(3))

        # Titolo card
        col.add_widget(MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Custom",
            text_color=BLU_NOTTE
        ))

        # --- CONTENUTO SPECIFICO PER GOMME O ALTRO ---
        if key == "gomme":
            treno = sc.get("treno", "—")
            km_percorsi = sc.get("km_percorsi", "—")
            km_residui = sc.get("km_residui", "—")

            # traduzione UI: T1/T2 → SET 1/SET 2
            if treno == "T1":
                set_label = "SET 1"
            elif treno == "T2":
                set_label = "SET 2"
            else:
                set_label = "—"

            col.add_widget(MDLabel(
                text=f"Set montato: {set_label}",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                font_style="Subtitle2"
            ))
            col.add_widget(MDLabel(
                text=f"Km percorsi: {km_percorsi}",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                font_style="Subtitle2"
            ))
            col.add_widget(MDLabel(
                text=f"Km residui: {km_residui}",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                font_style="Subtitle2"
            ))

        else:
            label_ultimo = self.get_label_ultimo(key)

            col.add_widget(MDLabel(
                text=f"{label_ultimo}: {ultimo}",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                font_style="Subtitle2"
            ))

            label_prossimo = self.get_label_prossimo(key)

            col.add_widget(MDLabel(
                text=f"{label_prossimo}: {prossimo}",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                font_style="Subtitle2"
            ))

        col.add_widget(MDBoxLayout(size_hint_y=None, height=dp(4)))

        # --- Stato testuale leggibile ---
        if stato == "🔴":
            stato_txt = "Scaduto"
            stato_color = (1, 0, 0, 1)  # rosso forte
        elif stato == "🟡":
            stato_txt = "In scadenza"
            stato_color = (0.8, 0.55, 0, 1)  # giallo/ocra deciso
        else:
            stato_txt = "Regolare"
            stato_color = VERDE_OK  # colore standard

        col.add_widget(MDLabel(
            text=f"Stato: {stato_txt}",
            theme_text_color="Custom",
            text_color=stato_color,
            font_style="Subtitle2"
        ))

        card.add_widget(icona)
        card.add_widget(col)

        # --- Colore card in base allo stato ---
        if stato == "🔴":
            card.md_bg_color = (1, 0.85, 0.85, 1)   # rosino allerta
        elif stato == "🟡":
            card.md_bg_color = (1, 1, 0.85, 1)      # giallo chiaro
        else:
            card.md_bg_color = GRIGIO_CARD          # colore standard

        return card

    # ---------------------------------------------------------
    # OPENERS (GOMME ecc.)
    # ---------------------------------------------------------
    def open_item(self, key):
        print("OPEN_ITEM:", key)
        if key == "gomme":
            gs = self.manager.get_screen("gomme")
            gs.current_auto = self.auto
            gs.current_auto_index = self.selected_index
            self.manager.current = "gomme"

        elif key == "revisione":
            rev_screen = self.manager.get_screen("revisione")
            rev_screen.current_auto = self.auto
            rev_screen.current_auto_index = self.selected_index
            self.manager.current = "revisione"

        elif key == "tagliando":
            ts = self.manager.get_screen("tagliando")
            ts.current_auto = self.auto
            ts.current_auto_index = self.selected_index
            self.manager.current = "tagliando"

        elif key == "dischi_freno":
            df = self.manager.get_screen("dischi_freno")
            df.current_auto = self.auto
            df.current_auto_index = self.selected_index
            self.manager.current = "dischi_freno"

        elif key == "pastiglie_freno":
            ps = self.manager.get_screen("pastiglie_freno")
            ps.current_auto = self.auto
            ps.current_auto_index = self.selected_index
            self.manager.current = "pastiglie_freno"

        elif key == "ammortizzatori":
            am = self.manager.get_screen("ammortizzatori")
            am.current_auto = self.auto
            am.current_auto_index = self.selected_index
            self.manager.current = "ammortizzatori"

        elif key == "cinghia":
            cs = self.manager.get_screen("cinghia")
            cs.current_auto = self.auto
            cs.current_auto_index = self.selected_index
            self.manager.current = "cinghia"

        elif key == "batteria":
            bs = self.manager.get_screen("batteria")
            bs.current_auto = self.auto
            bs.current_auto_index = self.selected_index
            self.manager.current = "batteria"

        elif key == "assicurazione":
            a = self.manager.get_screen("assicurazione")
            a.current_auto = self.auto
            a.current_auto_index = self.selected_index
            self.manager.current = "assicurazione"

        elif key == "bollo":
            b = self.manager.get_screen("bollo")
            b.current_auto = self.auto
            b.current_auto_index = self.selected_index
            self.manager.current = "bollo"

    def update_view(self):
        self.on_pre_enter()

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

    # ✅ MODIFICATO: salva su file VIVO
    def save_km(self):
        val = self.km_field.text.strip()

        if not val.isdigit():
            self.km_field.error = True
            return

        new_km = int(val)

        data = load_data()  # ✅ legge dal file VIVO

        autos = data.get("autos", [])
        if not autos:
            self.dialog_km.dismiss()
            return

        idx = self.selected_index
        if idx >= len(autos):
            idx = 0

        autos[idx]["km"] = new_km
        data["autos"] = autos

        save_data(data)  # ✅ scrive sul file VIVO

        self.dialog_km.dismiss()
        self.on_pre_enter()

    # ✅ MODIFICATO: salva su file VIVO
    def save_auto_data(self):
        """
        Salva TUTTE le modifiche fatte a self.auto
        dentro il file dati VIVO per l'auto selezionata.
        """
        data = load_data()  # ✅ legge dal file VIVO

        autos = data.get("autos", [])
        if not autos:
            return

        idx = self.selected_index
        if idx >= len(autos):
            idx = 0

        autos[idx] = self.auto
        data["autos"] = autos

        save_data(data)  # ✅ scrive sul file VIVO

        # Aggiorna UI
        self.on_pre_enter()
