from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivy.uix.image import Image
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from datetime import datetime


class RevisioneScreen(Screen):

    def on_pre_enter(self, *args):
        detail = self.manager.get_screen("detail_auto")
        self.current_auto = detail.auto
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        # ---------- ROOT ----------
        root = AnchorLayout(anchor_y="top")

        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))
        root.add_widget(content)

        # ---------- TITOLO ----------
        title_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
        )

        title = MDLabel(
            text="Revisione",
            halign="center",
            valign="middle",
            font_style="H4",
            theme_text_color="Custom",
            text_color=(0.05, 0.1, 0.2, 1),
        )

        info_icon = MDIconButton(
            icon="information-outline",
            theme_text_color="Custom",
            text_color=(0.05, 0.1, 0.2, 1),
            icon_size=dp(22),
            on_release=lambda x: self.show_info()
        )

        title_row.add_widget(title)
        title_row.add_widget(info_icon)
        content.add_widget(title_row)

        # ---------- IMMAGINE ----------
        image_box = MDBoxLayout(size_hint_y=None, height=dp(140))
        try:
            img = Image(
                source="app/assets/icons/revisione.png",
                size_hint=(None, None),
                width=dp(120),
                height=dp(120),
                allow_stretch=True,
                keep_ratio=True,
            )
            image_box.add_widget(MDBoxLayout())
            image_box.add_widget(img)
            image_box.add_widget(MDBoxLayout())
        except:
            image_box.add_widget(MDLabel(text="🔧", halign="center", font_style="H1"))

        content.add_widget(image_box)

        # ---------- DATI AUTO ----------
        anno_imm_str = ""
        ultima_rev_str = ""
        prossima_str = "—"

        if self.current_auto:
            anno = self.current_auto.get("anno_imm")
            if anno:
                anno_imm_str = str(anno)

            rev = self.current_auto.get("revisione", {})
            ultima_rev_str = rev.get("ultima", "") or ""
            prossima_str = rev.get("prossima", "—")

        # ---------- CARD ----------
        card = MDBoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=dp(16),
            md_bg_color=(1, 1, 1, 1),
            radius=[20, 20, 20, 20],
            size_hint_y=None
        )
        card.bind(minimum_height=card.setter("height"))

        # --- Campo data immatricolazione ---
        self.field_anno = MDTextField(
            hint_text="Data immatricolazione (gg/mm/aaaa)",
            text=anno_imm_str,
            mode="rectangle",
            line_color_normal=(0.05, 0.1, 0.2, 1),
            line_color_focus=(0.05, 0.1, 0.2, 1),
        )
        card.add_widget(self.field_anno)

        # --- OPPURE ---
        oppure = MDLabel(
            text="oppure",
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(20),
        )
        card.add_widget(oppure)

        # --- Campo ultima revisione ---
        self.field_ultima = MDTextField(
            hint_text="Eventuale ultima revisione (gg/mm/aaaa)",
            text=ultima_rev_str,
            mode="rectangle",
            line_color_normal=(0.05, 0.1, 0.2, 1),
            line_color_focus=(0.05, 0.1, 0.2, 1),
        )
        card.add_widget(self.field_ultima)

        # --- TESTO DINAMICO REGOLA APPLICATA ---
        self.label_regola = MDLabel(
            text="Calcolo: —",
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(22),
        )
        card.add_widget(self.label_regola)

        # --- Risultato calcolato ---
        self.label_prossima = MDLabel(
            text=f"[b][size=16]Prossima revisione:[/size][/b]  [size=18]{prossima_str}[/size]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=(0.10, 0.10, 0.20, 1),
            size_hint_y=None,
            height=dp(32),
        )
        card.add_widget(self.label_prossima)

        # Bind aggiornamenti
        self.field_anno.bind(text=self.on_imm_changed)
        self.field_ultima.bind(text=self.on_ultima_changed)


        content.add_widget(card)

        # ---------- BOTTONI ----------
        buttons = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60),
        )

        buttons.add_widget(
            MDFlatButton(text="ANNULLA", on_release=lambda x: self.go_back())
        )
        buttons.add_widget(
            MDRaisedButton(text="SALVA", on_release=lambda x: self.salva())
        )

        content.add_widget(buttons)

        self.add_widget(root)
        self.update_prossima()

    # ---------- LOGICA ----------
    def update_prossima(self, *args):
        imm = self.field_anno.text.strip()
        ultima = self.field_ultima.text.strip()

        # --- Date incomplete ---
        if imm and len(imm) < 10:
            self.label_prossima.text = "[b][size=16]Prossima revisione:[/size][/b]  [size=18]—[/size]"
            self.label_regola.text = "Calcolo: —"
            return

        if ultima and len(ultima) < 10:
            self.label_prossima.text = "[b][size=16]Prossima revisione:[/size][/b]  [size=18]—[/size]"
            self.label_regola.text = "Calcolo: —"
            return

        # --- Se esiste ultima revisione → regola dei 2 anni ---
        if ultima:
            try:
                dt = datetime.strptime(ultima, "%d/%m/%Y")
                prox = dt.replace(year=dt.year + 2).strftime("%d/%m/%Y")
                self.label_prossima.text = f"[b][size=16]Prossima revisione:[/size][/b]  [size=18]{prox}[/size]"
                self.label_regola.text = "Calcolo: revisione successiva (2 anni)"
                return
            except:
                pass

        # --- Prima revisione: 4 anni dall’immatricolazione ---
        if imm:
            try:
                dt = datetime.strptime(imm, "%d/%m/%Y")
                prox = dt.replace(year=dt.year + 4).strftime("%d/%m/%Y")
                self.label_prossima.text = f"[b][size=16]Prossima revisione:[/size][/b]  [size=18]{prox}[/size]"
                self.label_regola.text = "Calcolo: prima revisione (4 anni)"
                return
            except:
                pass

        # --- Nessun dato valido ---
        self.label_prossima.text = "[b][size=16]Prossima revisione:[/size][/b]  [size=18]—[/size]"
        self.label_regola.text = "Calcolo: —"

    def on_imm_changed(self, instance, value):
    # Se l’utente scrive l’immatricolazione → svuota l'ultima revisione
        if value.strip():
            self.field_ultima.text = ""
        self.update_prossima()


    def on_ultima_changed(self, instance, value):
        # Se l’utente scrive l’ultima revisione → svuota l'immatricolazione
        if value.strip():
            self.field_anno.text = ""
        self.update_prossima()


    # ---------- SALVA ----------
    def salva(self):
        imm = self.field_anno.text.strip()
        ultima = self.field_ultima.text.strip() or None

        # --- VALIDAZIONE DATA IMMATRICOLAZIONE ---
        if imm:
            if not self.is_valid_date(imm):
                self.show_error("La data di immatricolazione non è valida.\nFormato richiesto: gg/mm/aaaa")
                return
        else:
            self.show_error("Inserisci una data di immatricolazione.")
            return

        # --- VALIDAZIONE ULTIMA REVISIONE ---
        if ultima:
            if not self.is_valid_date(ultima):
                self.show_error("La data dell'ultima revisione non è valida.\nFormato richiesto: gg/mm/aaaa")
                return

        # --- PROSSIMA REVISIONE ---
        prossima = self.label_prossima.text.split("] ")[1].strip()

        # --- SALVATAGGIO ---
        self.current_auto["anno_imm"] = imm
        self.current_auto.setdefault("revisione", {})
        self.current_auto["revisione"]["ultima"] = ultima
        self.current_auto["revisione"]["prossima"] = prossima

        detail = self.manager.get_screen("detail_auto")
        detail.save_auto_data()
        self.go_back()
    
    def is_valid_date(self, text):
        try:
            datetime.strptime(text, "%d/%m/%Y")
            return True
        except:
            return False
    
    def show_error(self, msg):
        dialog = MDDialog(
            title="Errore",
            text=msg,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def go_back(self):
        self.manager.current = "detail_auto"

    # ---------- INFO POPUP ----------
    def show_info(self):
        dialog = MDDialog(
            title="Come funziona la revisione?",
            text=(
                "• Prima revisione: 4 anni\n"
                "• Revisioni successive: ogni 2 anni\n\n"
                "Compila solo ciò che conosci:\n"
                "• Se l’auto è nuova → solo immatricolazione\n"
                "• Se ha già fatto una revisione → solo ultima revisione\n"
            ),
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
