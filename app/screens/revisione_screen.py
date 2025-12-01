from datetime import datetime

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.pickers import MDDatePicker
from kivy.metrics import dp


class RevisioneScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # qui ci mettiamo il dizionario auto passato da DetailAuto
        self.current_auto = None

    # quando entriamo nello screen, costruiamo la UI
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        from kivy.uix.image import Image

        self.clear_widgets()

        # ROOT → verticale classico
        root = MDBoxLayout(
            orientation="vertical",
            padding=(dp(10), dp(10), dp(10), dp(10)),
            spacing=dp(10)
        )

        # -----------------------
        # SPAZIO SUPERIORE
        # -----------------------
        root.add_widget(MDBoxLayout(size_hint_y=None, height=dp(20)))

        # -----------------------
        # TITOLO
        # -----------------------
        title = MDLabel(
            text="Revisione",
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=(0.05, 0.1, 0.2, 1),
            size_hint_y=None,
            height=dp(50),
        )
        root.add_widget(title)

        # -----------------------
        # IMMAGINE
        # -----------------------
        img_box = MDBoxLayout(
            size_hint_y=None,
            height=dp(160),
        )

        try:
            img = Image(
                source="app/assets/icons/revisione.png",
                size_hint=(None, None),
                width=dp(140),
                height=dp(140),
                allow_stretch=True,
                keep_ratio=True
            )
            img_box.add_widget(MDBoxLayout())
            img_box.add_widget(img)
            img_box.add_widget(MDBoxLayout())
        except:
            img_box.add_widget(MDLabel(
                text="🚗",
                halign="center",
                font_style="H1"
            ))

        root.add_widget(img_box)

        # -----------------------
        # CARD CAMPi
        # -----------------------
        card = MDBoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=dp(16),
            md_bg_color=(1, 1, 1, 1),
            radius=[20, 20, 20, 20],
            size_hint_y=None
        )
        card.bind(minimum_height=card.setter("height"))

        # valori iniziali
        anno_imm_str = ""
        ultima_rev_str = ""
        prossima_str = "—"

        if self.current_auto:
            anno_imm = self.current_auto.get("anno_imm")
            if anno_imm:
                anno_imm_str = str(anno_imm)

            rev = self.current_auto.get("revisione", {})
            ultima_rev_str = rev.get("ultima", "")
            prossima_str = rev.get("prossima", "—")

        self.field_anno = MDTextField(
            hint_text="Anno immatricolazione",
            text=anno_imm_str,
            input_filter="int",
            mode="rectangle",
        )

        self.field_ultima = MDTextField(
            hint_text="Eventuale Ultima Revisione (gg/mm/aaaa) ",
            text=ultima_rev_str,
            mode="rectangle",
            on_focus=self.on_ultima_focus,
        )

        self.label_prossima = MDLabel(
            text=f"Prossima revisione: {prossima_str}",
            halign="left",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(28),
        )

        card.add_widget(self.field_anno)
        card.add_widget(self.field_ultima)
        card.add_widget(self.label_prossima)
        root.add_widget(card)

        # -----------------------
        # BOTTONI IN FONDO
        # -----------------------
        root.add_widget(MDBoxLayout(size_hint_y=1))  # SPINGE GIÙ I BOTTONI

        buttons_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60),
            padding=(0, dp(10)),
        )

        btn_annulla = MDFlatButton(
            text="ANNULLA",
            on_release=lambda x: self.go_back(),
            font_size=dp(16),
        )
        btn_salva = MDRaisedButton(
            text="SALVA",
            on_release=lambda x: self.salva(),
            font_size=dp(16),
        )

        buttons_box.add_widget(btn_annulla)
        buttons_box.add_widget(btn_salva)

        root.add_widget(buttons_box)

        self.add_widget(root)
        self.update_prossima()



    # ---------------------------------------------------------
    # DATEPICKER PER ULTIMA REVISIONE
    # ---------------------------------------------------------
    def on_ultima_focus(self, instance, value):
        if value:  # quando entra nel campo
            picker = MDDatePicker()
            picker.bind(on_save=self.set_ultima_date)
            picker.open()

    def set_ultima_date(self, instance, date_value, date_range):
        if date_value:
            self.field_ultima.text = date_value.strftime("%d/%m/%Y")
            # aggiorno subito la preview
            self.update_prossima()

    # ---------------------------------------------------------
    # LOGICA CALCOLO PROSSIMA REVISIONE
    # ---------------------------------------------------------
    def update_prossima(self, *args):

        # Se manca anno immatricolazione → non si può calcolare
        if not self.field_anno.text.strip().isdigit():
            self.label_prossima.text = "Prossima revisione: —"
            return

        anno_imm = int(self.field_anno.text.strip())
        today = datetime.now()

        # Calcolo età auto
        anni_auto = today.year - anno_imm

        # ----- CASO 1: nessuna revisione fatta -----
        # Auto ha meno di 4 anni e non esiste una revisione
        if anni_auto < 4 and not self.field_ultima.text.strip():
            prima_rev = datetime(anno_imm + 4, today.month, today.day)
            self.label_prossima.text = f"Prossima revisione: {prima_rev.strftime('%d/%m/%Y')}"
            return

        # ----- CASO 2: ultima revisione esiste -----
        if self.field_ultima.text.strip():
            try:
                ultima = datetime.strptime(self.field_ultima.text.strip(), "%d/%m/%Y")
                prossima = ultima.replace(year=ultima.year + 2)
                self.label_prossima.text = f"Prossima revisione: {prossima.strftime('%d/%m/%Y')}"
                return
            except:
                self.label_prossima.text = "Prossima revisione: —"
                return

        # ----- CASO 3: auto vecchia ma nessuna data inserita -----
        # (ad esempio, utente non la ricorda → non la calcoliamo)
        self.label_prossima.text = "Prossima revisione: —"


    # ---------------------------------------------------------
    # SALVATAGGIO
    # ---------------------------------------------------------
    def salva(self):
        if not self.current_auto:
            self.go_back()
            return

        anno_txt = self.field_anno.text.strip()
        if not anno_txt:
            # anno obbligatorio
            return

        try:
            anno_imm = int(anno_txt)
        except ValueError:
            return

        ultima_txt = self.field_ultima.text.strip()
        # ricalcolo la prossima in base ai campi
        self.update_prossima()
        prossima_txt = self.label_prossima.text.replace("Prossima revisione: ", "").strip()

        # salviamo nel dizionario auto
        self.current_auto["anno_imm"] = anno_imm
        if "revisione" not in self.current_auto:
            self.current_auto["revisione"] = {}

        self.current_auto["revisione"]["ultima"] = ultima_txt or None
        self.current_auto["revisione"]["prossima"] = prossima_txt if prossima_txt != "—" else None

        # TODO: qui dopo collegheremo salvataggio su JSON, refresh ecc.
        self.go_back()

    # ---------------------------------------------------------
    def go_back(self):
        # torna alla schermata dettaglio
        self.manager.current = "detail_auto"
