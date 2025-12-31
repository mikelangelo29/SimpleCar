from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import json
import os
import calendar
from datetime import date


BLU = get_color_from_hex("0D1B2A")
CARD_BG = (0.94, 0.97, 1.00, 1)  # #F0F6FF
BORDO = BLU


class BolloScreen(MDScreen):
    """
    Bollo (corretto): chiediamo ULTIMO PAGAMENTO, calcoliamo SCADENZA (+12 mesi).
    Schema base EasyCar con titolo H4 in top bar.
    """

    def on_pre_enter(self, *args):
        self._ensure_structure()
        self._build_ui()
        self._load_values()
        self._update_view()

    # =========================================================
    # STRUTTURA DATI
    # =========================================================
    def _ensure_structure(self):
        if not getattr(self, "current_auto", None):
            return

        blk = self.current_auto.get("bollo")
        if not isinstance(blk, dict):
            blk = {}

        blk.setdefault("ultimo_pagamento", "")
        blk.setdefault("durata_mesi", 12)
        blk.setdefault("scadenza", "")
        blk.setdefault("importo", None)

        self.current_auto["bollo"] = blk
        self._save_full_fallback()

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self):
        self.clear_widgets()

        root = FloatLayout()
        self.add_widget(root)

        main = MDBoxLayout(orientation="vertical")
        root.add_widget(main)

        # ---------- TOP BAR (80) ----------
        top = MDBoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            spacing=dp(10),
            md_bg_color=BLU
        )

        btn_back = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=lambda x: self._go_back()
        )

        title = MDLabel(
            text="Bollo",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H4",  # COME DISCHI FRENO
            halign="left",
            valign="middle",
        )

        btn_info = MDIconButton(
            icon="information-outline",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=lambda x: self._open_info_dialog()
        )

        top.add_widget(btn_back)
        top.add_widget(title)
        top.add_widget(btn_info)
        main.add_widget(top)

        main.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(10)))

        # ---------- SCROLL ----------
        scroll = MDScrollView()
        main.add_widget(scroll)

        container = MDBoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(10), dp(18), dp(20)],
            spacing=dp(14),
            size_hint_y=None
        )
        container.bind(minimum_height=container.setter("height"))
        scroll.add_widget(container)

        # ---------- IMMAGINE CENTRATA ----------
        img_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(190),
            padding=[0, dp(10), 0, 0],
        )
        try:
            img = Image(
                source=os.path.join("app", "assets", "icons", "bollo.png"),
                size_hint=(None, None),
                width=dp(170),
                height=dp(170),
                allow_stretch=True,
                keep_ratio=True,
            )
            img_box.add_widget(MDBoxLayout())
            img_box.add_widget(img)
            img_box.add_widget(MDBoxLayout())
        except:
            img_box.add_widget(MDLabel(text="🧾", halign="center", font_style="H1"))
        container.add_widget(img_box)

        # ---------- CARD ----------
        card = MDBoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(12),
            size_hint_y=None,
            md_bg_color=CARD_BG,
        )
        card.bind(minimum_height=card.setter("height"))
        card.line_color = BORDO
        card.line_width = 2
        container.add_widget(card)

        # Ultimo pagamento
        card.add_widget(MDLabel(
            text="Ultimo pagamento",
            theme_text_color="Custom",
            text_color=BLU,
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        self.field_ultimo = MDTextField(
            hint_text="gg/mm/aaaa",
            mode="rectangle",
            size_hint_y=None,
            height=dp(46),
        )
        self.field_ultimo.bind(text=lambda *a: self._update_view())
        card.add_widget(self.field_ultimo)

        # Importo
        card.add_widget(MDLabel(
            text="Importo (€) (opzionale)",
            theme_text_color="Custom",
            text_color=BLU,
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        self.field_importo = MDTextField(
            hint_text="es. 210",
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(46),
        )
        card.add_widget(self.field_importo)

        # Output: prossima scadenza + stato
        self.label_scadenza = MDLabel(
            text="Prossima scadenza: —",
            theme_text_color="Custom",
            text_color=BLU,
            size_hint_y=None,
            height=dp(22)
        )
        self.label_stato = MDLabel(
            text="Stato: —",
            theme_text_color="Custom",
            text_color=BLU,
            size_hint_y=None,
            height=dp(22)
        )
        card.add_widget(self.label_scadenza)
        card.add_widget(self.label_stato)

        # ---------- BUTTONS ----------
        buttons = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        buttons.add_widget(MDFlatButton(text="ANNULLA", on_release=lambda x: self._go_back()))
        buttons.add_widget(MDRaisedButton(text="SALVA", on_release=lambda x: self._save_values()))
        container.add_widget(buttons)

        container.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(20)))

    # =========================================================
    # LOAD / VIEW
    # =========================================================
    def _load_values(self):
        if not getattr(self, "current_auto", None):
            return

        blk = self.current_auto.get("bollo", {})
        ultimo = blk.get("ultimo_pagamento", "") or ""
        imp = blk.get("importo", None)

        self.field_ultimo.text = ultimo
        self.field_importo.text = "" if imp is None else str(imp)

    def _update_view(self):
        ultimo = self.field_ultimo.text.strip() if self.field_ultimo else ""
        if not ultimo or not self._is_valid_date(ultimo):
            self.label_scadenza.text = "Prossima scadenza: —"
            self.label_stato.text = "Stato: —"
            self.label_stato.text_color = BLU
            return

        scadenza = self._add_months(ultimo, 12)
        stato = self._compute_state(scadenza)

        self.label_scadenza.text = f"Prossima scadenza: {scadenza}"
        self.label_stato.text = f"Stato: {self._stato_to_text(stato)}"
        self.label_stato.text_color = self._stato_color(stato)

    # =========================================================
    # SAVE
    # =========================================================
    def _save_values(self):
        if not getattr(self, "current_auto", None):
            self._show_error("Nessuna auto selezionata.")
            return

        ultimo = self.field_ultimo.text.strip()
        if not ultimo or not self._is_valid_date(ultimo):
            self._show_error("Inserisci una data di ultimo pagamento valida (gg/mm/aaaa).")
            return

        durata = 12
        scadenza = self._add_months(ultimo, durata)
        stato = self._compute_state(scadenza)

        imp_txt = self.field_importo.text.strip()
        importo = None
        if imp_txt:
            try:
                importo = int(imp_txt)
            except:
                self._show_error("Importo non valido.")
                return

        # --- blocco specifico ---
        self.current_auto["bollo"] = {
            "ultimo_pagamento": ultimo,
            "durata_mesi": durata,
            "scadenza": scadenza,
            "importo": importo
        }

        # --- scadenze standard ---
        scad = self.current_auto.setdefault("scadenze", {})
        scad["bollo"] = {
            "ultimo": ultimo,
            "prossimo": scadenza,
            "stato": stato
        }

        # --- persist ---
        if hasattr(self, "current_auto_index"):
            self._save_by_index()
        else:
            self._save_full_fallback()

        self._go_back()

    # =========================================================
    # DATE / STATE
    # =========================================================
    def _parse_date(self, s):
        # gg/mm/aaaa con supporto gg/mm/aa -> 20aa/19aa
        parts = s.strip().split("/")
        if len(parts) != 3:
            raise ValueError("Formato data")

        d = int(parts[0])
        m = int(parts[1])

        y_str = parts[2].strip()
        if not y_str.isdigit():
            raise ValueError("Anno non valido")

        if len(y_str) == 2:
            yy = int(y_str)
            y = 2000 + yy if yy <= 79 else 1900 + yy
        elif len(y_str) == 4:
            y = int(y_str)
        else:
            raise ValueError("Anno deve essere a 2 o 4 cifre")

        return d, m, y

    def _fmt_date(self, d, m, y):
        return f"{d:02d}/{m:02d}/{y:04d}"

    def _is_valid_date(self, s):
        try:
            d, m, y = self._parse_date(s)
            date(y, m, d)
            return True
        except:
            return False

    def _add_months(self, date_str, months):
        d, m, y = self._parse_date(date_str)

        total = (y * 12 + (m - 1)) + int(months)
        new_y = total // 12
        new_m = (total % 12) + 1

        last_day = calendar.monthrange(new_y, new_m)[1]
        new_d = min(d, last_day)

        return self._fmt_date(new_d, new_m, new_y)

    def _days_until(self, date_str):
        d, m, y = self._parse_date(date_str)
        target = date(y, m, d)
        return (target - date.today()).days

    def _compute_state(self, scadenza_str):
        days = self._days_until(scadenza_str)
        if days < 0:
            return "🔴"
        if days <= 30:
            return "🟡"
        return "⚪"

    def _stato_to_text(self, stato):
        if stato == "🔴":
            return "Scaduto"
        if stato == "🟡":
            return "In scadenza"
        return "Regolare"

    def _stato_color(self, stato):
        if stato == "🔴":
            return (0.85, 0.1, 0.1, 1)
        if stato == "🟡":
            return (0.95, 0.55, 0.1, 1)
        return BLU

    # =========================================================
    # PERSISTENZA
    # =========================================================
    def _save_by_index(self):
        data_path = os.path.join("app", "data", "autos.json")
        if not os.path.exists(data_path):
            return

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        idx = int(self.current_auto_index)
        if "autos" in data and 0 <= idx < len(data["autos"]):
            data["autos"][idx] = self.current_auto

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _save_full_fallback(self):
        self.data_path = os.path.join("app", "data", "autos.json")
        if not os.path.exists(self.data_path):
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "autos" not in data or not isinstance(data["autos"], list):
            return

        for a in data["autos"]:
            if (
                a.get("marca") == self.current_auto.get("marca")
                and a.get("modello") == self.current_auto.get("modello")
                and a.get("targa") == self.current_auto.get("targa")
            ):
                a.update(self.current_auto)
                break

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # =========================================================
    # DIALOG / NAV
    # =========================================================
    def _show_error(self, msg):
        dialog = MDDialog(
            title="Errore",
            text=msg,
            buttons=[MDRaisedButton(text="OK", md_bg_color=BLU, on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def _open_info_dialog(self):
        dialog = MDDialog(
            title="Bollo",
            text=("Inserisci la data dell'ultimo pagamento.\n\n"
                  "EasyCar calcola automaticamente la prossima scadenza a 12 mesi.\n"
                  "Lo stato diventa 'In scadenza' negli ultimi 30 giorni."),
            buttons=[MDRaisedButton(text="OK", md_bg_color=BLU, on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def _go_back(self):
        self.manager.current = "detail_auto"
