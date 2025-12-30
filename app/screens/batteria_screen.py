from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import json
import os
from datetime import datetime, date


BLU = get_color_from_hex("0D1B2A")
CARD_BG = (0.94, 0.97, 1.00, 1)  # #F0F6FF
BORDO = BLU


class BatteriaScreen(MDScreen):
    """
    Batteria — stesso schema:
    - Radio intervallo (anni)
    - Data ultima sostituzione (obbligatoria)
    - Calcolo prossima data
    - Stato ⚪🟡🔴 su tempo (soglia 15% intervallo, min 30 giorni)
    - Salva in auto["batteria"] e auto["scadenze"]["batteria"] con {ultimo, prossimo, stato}
    """

    data_path = "app/data/autos.json"

    def on_pre_enter(self, *args):
        self._ensure_structure()
        self._build_ui()
        self._load_values()
        self._update_view()

    # =========================================================
    # HELPERS DATE
    # =========================================================
    def _parse_date(self, s: str):
        s = (s or "").strip()
        try:
            return datetime.strptime(s, "%d/%m/%Y").date()
        except:
            return None

    def _format_date(self, d: date):
        return d.strftime("%d/%m/%Y")

    def _add_years(self, d: date, years: int):
        # Gestione semplice e robusta: se 29/02 -> 28/02 negli anni non bisestili
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            # 29 febbraio
            return d.replace(month=2, day=28, year=d.year + years)

    # =========================================================
    # STRUTTURA DATI
    # =========================================================
    def _ensure_structure(self):
        if not getattr(self, "current_auto", None):
            return

        bt = self.current_auto.get("batteria")
        if not isinstance(bt, dict):
            bt = {}

        bt.setdefault("intervallo_anni", 4)  # default medio
        bt.setdefault("ultima_data", "")     # obbligatoria in SALVA
        bt.setdefault("prossima_data", "")

        self.current_auto["batteria"] = bt
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
            padding=[20, 20, 20, 20],
            md_bg_color=BLU,
        )

        back = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(34),
            on_release=lambda x: self._go_back(),
        )
        top.add_widget(back)

        title = MDLabel(
            text="Batteria",
            halign="center",
            valign="middle",
            bold=True,
            font_style="H4",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        top.add_widget(title)

        info = MDIconButton(
            icon="information-outline",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(28),
            on_release=lambda x: self._show_info(),
        )
        top.add_widget(info)

        main.add_widget(top)

        # ---------- SCROLL ----------
        scroll = MDScrollView()
        main.add_widget(scroll)

        container = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter("height"))
        scroll.add_widget(container)

        # solita riga per "un millimetro"
        container.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(10)))

        # ---------- IMMAGINE ----------
        img_box = MDBoxLayout(size_hint_y=None, height=dp(140))
        try:
            img = Image(
                source="app/assets/icons/batteria.png",
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
            img_box.add_widget(MDLabel(text="🔋", halign="center", font_style="H1"))

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

        # Titolo card + i
        title_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            spacing=dp(6),
        )
        title_row.add_widget(MDLabel(
            text="Intervallo d’utilizzo (anni)",
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=BLU,
        ))

        card.add_widget(title_row)

        # Radio: 3 / 4 / 5 anni (medie pratiche)
        self.rb_3 = self._radio_row("3 anni", 3)
        self.rb_4 = self._radio_row("4 anni", 4)
        self.rb_5 = self._radio_row("5 anni", 5)
        card.add_widget(self.rb_3["row"])
        card.add_widget(self.rb_4["row"])
        card.add_widget(self.rb_5["row"])

        # Data ultima sostituzione (obbligatoria)
        self.field_ultima = MDTextField(
            hint_text="Data ultima sostituzione (obbligatoria)  gg/mm/aaaa",
            mode="rectangle",
            line_color_normal=BLU,
            line_color_focus=BLU,
            size_hint_y=None,
            height=dp(48),
        )
        self.field_ultima.bind(text=self._on_changed)
        card.add_widget(self.field_ultima)

        # Prossimo (info)
        self.lbl_prossimo = MDLabel(
            text="Prossima sostituzione: —",
            font_style="Subtitle2",
            theme_text_color="Custom",
            text_color=BLU,
            halign="center",
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(self.lbl_prossimo)

        # ---------- BOTTONI ----------
        buttons = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60),
        )
        buttons.add_widget(MDFlatButton(text="ANNULLA", on_release=lambda x: self._go_back()))
        buttons.add_widget(MDRaisedButton(text="SALVA", on_release=lambda x: self._save_values()))
        container.add_widget(buttons)

        container.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(20)))

    # =========================================================
    # RADIO
    # =========================================================
    def _radio_row(self, label, value):
        row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
        )

        cb = MDCheckbox(group="batteria_interval")
        cb.bind(active=lambda inst, active, v=value: self._set_interval(v, active))

        lab = MDLabel(
            text=label,
            theme_text_color="Custom",
            text_color=BLU,
            valign="middle",
        )

        row.add_widget(cb)
        row.add_widget(lab)
        return {"row": row, "cb": cb, "value": value}

    def _set_interval(self, value, active):
        if not active:
            return
        self.intervallo_anni = int(value)
        self._update_view()

    # =========================================================
    # LOAD
    # =========================================================
    def _load_values(self):
        if not getattr(self, "current_auto", None):
            return

        bt = self.current_auto.get("batteria", {}) or {}
        self.intervallo_anni = int(bt.get("intervallo_anni", 4) or 4)

        self.field_ultima.text = (bt.get("ultima_data", "") or "").strip()

        self.rb_3["cb"].active = (self.intervallo_anni == 3)
        self.rb_4["cb"].active = (self.intervallo_anni == 4)
        self.rb_5["cb"].active = (self.intervallo_anni == 5)

    def _on_changed(self, instance, value):
        self._update_view()

    # =========================================================
    # CALCO PROSSIMO + LABEL
    # =========================================================
    def _update_view(self):
        d = self._parse_date(self.field_ultima.text)
        if not d:
            self.lbl_prossimo.text = "Prossima sostituzione: —"
            return

        anni = int(getattr(self, "intervallo_anni", 4))
        next_d = self._add_years(d, anni)
        self.lbl_prossimo.text = f"Prossima sostituzione: {self._format_date(next_d)}"

    # =========================================================
    # SALVA
    # =========================================================
    def _save_values(self):
        if not getattr(self, "current_auto", None):
            self._show_error("Nessuna auto selezionata.")
            return

        d = self._parse_date(self.field_ultima.text)
        if not d:
            self._show_error("Inserisci una data valida.\nFormato richiesto: gg/mm/aaaa")
            return

        anni = int(getattr(self, "intervallo_anni", 4))
        next_d = self._add_years(d, anni)

        # Stato su tempo
        oggi = date.today()
        giorni_tot = max(1, (next_d - d).days)
        soglia_gialla = max(30, int(giorni_tot * 0.15))  # 15% (min 30 giorni)

        giorni_residui = (next_d - oggi).days

        if giorni_residui < 0:
            stato = "🔴"
        elif giorni_residui <= soglia_gialla:
            stato = "🟡"
        else:
            stato = "⚪"

        # Blocco specifico
        self.current_auto.setdefault("batteria", {})
        self.current_auto["batteria"]["intervallo_anni"] = anni
        self.current_auto["batteria"]["ultima_data"] = self._format_date(d)
        self.current_auto["batteria"]["prossima_data"] = self._format_date(next_d)

        # Scadenze (per DetailAuto)
        scad = self.current_auto.setdefault("scadenze", {})
        scad["batteria"] = {
            "ultimo": self._format_date(d),
            "prossimo": self._format_date(next_d),
            "stato": stato
        }

        # Persist
        if hasattr(self, "current_auto_index"):
            self._save_by_index()
        else:
            self._save_full_fallback()

        self._go_back()

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
        if not os.path.exists(self.data_path):
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])
        for a in autos:
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
    # INFO / ERROR / NAV
    # =========================================================
    def _show_error(self, msg):
        dialog = MDDialog(
            title="Errore",
            text=msg,
            buttons=[MDRaisedButton(text="OK", md_bg_color=BLU, on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def _show_info(self):
        dialog = MDDialog(
            title="Batteria",
            text=(
                "L’intervallo d’utilizzo indica ogni quanti anni, in media, "
                "la batteria andrebbe sostituita.\n\n"
                "È una stima:\n"
                "• scegli un valore più basso se fai molti tragitti brevi, "
                "uso cittadino o start&stop;\n"
                "• scegli un valore più alto se percorri spesso tratti extraurbani.\n\n"
                "Lo stato viene calcolato sul tempo.\n"
                "Inserisci la data dell’ultima sostituzione."
            ),
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=BLU,
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()


    def _go_back(self):
        self.manager.current = "detail_auto"
