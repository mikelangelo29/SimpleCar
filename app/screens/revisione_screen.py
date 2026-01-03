from kivy.uix.screenmanager import Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivy.uix.image import Image
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from datetime import datetime, timedelta
from kivymd.uix.card import MDCard

# ✅ NUOVO: runtime storage (file VIVO)
from app.storage.data_store import load_data, save_data, ensure_live_file


class RevisioneScreen(Screen):

    def on_pre_enter(self, *args):
        detail = self.manager.get_screen("detail_auto")
        self.current_auto = detail.auto
        # ✅ prende l'indice corrente (così salva l'auto giusta nel file vivo)
        self.current_auto_index = getattr(detail, "selected_index", 0)
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

        # ---------- TOP BAR ----------
        top = MDBoxLayout(
            size_hint_y=None,
            height=dp(80),   # identico a Gomme
            padding=[20, 20, 20, 20],
            md_bg_color=(0.05, 0.1, 0.2, 1),  # BLU NOTTE
        )

        # Pulsante indietro
        back = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(34),
            on_release=lambda x: self.go_back(),
        )
        top.add_widget(back)

        # Titolo centrale
        title = MDLabel(
            text="Revisione",
            halign="center",
            valign="middle",
            bold=True,
            font_style="H4",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        top.add_widget(title)

        # Icona info a destra
        info_icon = MDIconButton(
            icon="information-outline",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(28),
            on_release=lambda x: self.show_info()
        )
        top.add_widget(info_icon)

        content.add_widget(top)

        # ---------- IMMAGINE ----------
        image_box = MDBoxLayout(size_hint_y=None, height=dp(140))
        try:
            img = Image(
                source="app/assets/icons/revisione.png",
                size_hint=(None, None),
                width=dp(150),
                height=dp(150),
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
        card = MDCard(
            orientation="vertical",
            spacing=dp(14),
            padding=dp(16),
            radius=[20, 20, 20, 20],
            md_bg_color=(0.94, 0.97, 1.00, 1),
            line_color=(0.05, 0.1, 0.2, 1),
            line_width=dp(1.4),
            elevation=0,
            size_hint_y=None,
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

        if imm and len(imm) < 10:
            self.label_prossima.text = "[b][size=16]Prossima revisione:[/size][/b]  [size=18]—[/size]"
            self.label_regola.text = "Calcolo: —"
            self.stato_revisione = "⚪"
            return

        if ultima and len(ultima) < 10:
            self.label_prossima.text = "[b][size=16]Prossima revisione:[/size][/b]  [size=18]—[/size]"
            self.label_regola.text = "Calcolo: —"
            self.stato_revisione = "⚪"
            return

        # CASO 1: esiste ultima revisione → +2 anni
        if ultima:
            try:
                dt = datetime.strptime(ultima, "%d/%m/%Y")
                prox = dt.replace(year=dt.year + 2).strftime("%d/%m/%Y")

                oggi = datetime.today()
                prox_date = datetime.strptime(prox, "%d/%m/%Y")

                if prox_date < oggi:
                    self.stato_revisione = "🔴"
                elif prox_date <= oggi + timedelta(days=60):
                    self.stato_revisione = "🟡"
                else:
                    self.stato_revisione = "⚪"

                self.label_prossima.text = (
                    f"[b][size=16]Prossima revisione:[/size][/b]  [size=18]{prox}[/size]"
                )
                self.label_regola.text = "Calcolo: revisione successiva (2 anni)"
                return
            except:
                pass

        # CASO 2: prima revisione → +4 anni
        if imm:
            try:
                dt = datetime.strptime(imm, "%d/%m/%Y")
                prox = dt.replace(year=dt.year + 4).strftime("%d/%m/%Y")

                oggi = datetime.today()
                prox_date = datetime.strptime(prox, "%d/%m/%Y")

                if prox_date < oggi:
                    self.stato_revisione = "🔴"
                elif prox_date <= oggi + timedelta(days=60):
                    self.stato_revisione = "🟡"
                else:
                    self.stato_revisione = "⚪"

                self.label_prossima.text = (
                    f"[b][size=16]Prossima revisione:[/size][/b]  [size=18]{prox}[/size]"
                )
                self.label_regola.text = "Calcolo: prima revisione (4 anni)"
                return
            except:
                pass

        self.label_prossima.text = "[b][size=16]Prossima revisione:[/size][/b]  [size=18]—[/size]"
        self.label_regola.text = "Calcolo: —"
        self.stato_revisione = "⚪"

    def on_imm_changed(self, instance, value):
        if value.strip():
            self.field_ultima.text = ""
        self.update_prossima()

    def on_ultima_changed(self, instance, value):
        if value.strip():
            self.field_anno.text = ""
        self.update_prossima()

    # ---------- SALVA ----------
    def salva(self):
        imm = self.field_anno.text.strip()
        ultima = self.field_ultima.text.strip() or None

        if not imm and not ultima:
            self.show_error("Inserisci una data di immatricolazione O una ultima revisione.")
            return

        if imm and not self.is_valid_date(imm):
            self.show_error("La data di immatricolazione non è valida.\nFormato richiesto: gg/mm/aaaa")
            return

        if ultima and not self.is_valid_date(ultima):
            self.show_error("La data dell'ultima revisione non è valida.\nFormato richiesto: gg/mm/aaaa")
            return

        try:
            if ultima:
                dt = datetime.strptime(ultima, "%d/%m/%Y")
                prox_date = dt.replace(year=dt.year + 2)
                self.label_regola.text = "Calcolo: revisione successiva (2 anni)"
            else:
                dt = datetime.strptime(imm, "%d/%m/%Y")
                prox_date = dt.replace(year=dt.year + 4)
                self.label_regola.text = "Calcolo: prima revisione (4 anni)"

            prossima = prox_date.strftime("%d/%m/%Y")
        except Exception:
            self.show_error("Errore nel calcolo della prossima revisione.")
            return

        oggi = datetime.today()
        if prox_date < oggi:
            stato = "🔴"
        elif prox_date <= oggi + timedelta(days=60):
            stato = "🟡"
        else:
            stato = "⚪"

        self.label_prossima.text = (
            f"[b][size=16]Prossima revisione:[/size][/b]  [size=18]{prossima}[/size]"
        )

        # --- aggiorna current_auto ---
        self.current_auto["anno_imm"] = imm
        self.current_auto.setdefault("revisione", {})
        self.current_auto["revisione"]["ultima"] = ultima
        self.current_auto["revisione"]["prossima"] = prossima

        # --- aggiorna scadenze per DetailAuto ---
        self.current_auto.setdefault("scadenze", {})
        self.current_auto["scadenze"].setdefault("revisione", {})
        self.current_auto["scadenze"]["revisione"]["ultimo"] = ultima or "—"
        self.current_auto["scadenze"]["revisione"]["prossimo"] = prossima
        self.current_auto["scadenze"]["revisione"]["stato"] = stato

        # ✅ salva su FILE VIVO (autonomo)
        self._save_by_index()

        self.go_back()

    # ✅ NUOVO: persist su file vivo
    def _save_by_index(self):
        ensure_live_file()
        data = load_data()
        autos = data.get("autos", [])

        idx = int(getattr(self, "current_auto_index", 0))
        if 0 <= idx < len(autos):
            autos[idx] = self.current_auto
            data["autos"] = autos
            save_data(data)

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
