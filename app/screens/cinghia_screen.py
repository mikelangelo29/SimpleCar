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


BLU = get_color_from_hex("0D1B2A")
CARD_BG = (0.94, 0.97, 1.00, 1)  # #F0F6FF
BORDO = BLU


class CinghiaScreen(MDScreen):
    """
    Screen Cinghia distribuzione — stesso schema degli altri:
    - Radio intervallo km: 80k / 100k / 120k
    - Km ultima sostituzione (obbligatorio)
    - Data sostituzione (opzionale) SOLO promemoria
    - Stato calcolato SOLO su km
    - Salva sia in auto["cinghia"] sia in auto["scadenze"]["cinghia"]
    """

    data_path = "app/data/autos.json"

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

        cg = self.current_auto.get("cinghia")
        if not isinstance(cg, dict):
            cg = {}

        cg.setdefault("intervallo_km", 100000)   # default medio
        cg.setdefault("ultimo_km", None)
        cg.setdefault("prossimo_km", None)
        cg.setdefault("data", "")               # opzionale (solo promemoria)

        self.current_auto["cinghia"] = cg
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
            text="Cinghia distribuzione",
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

        # (la solita riga per abbassare un pelo)
        container.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(10)))

        # ---------- IMMAGINE ----------
        img_box = MDBoxLayout(size_hint_y=None, height=dp(140))
        try:
            img = Image(
                source="app/assets/icons/cinghia.png",
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
            img_box.add_widget(MDLabel(text="🛞", halign="center", font_style="H1"))

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
            text="Intervallo d’utilizzo (km)",
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=BLU,
        ))
        title_row.add_widget(MDIconButton(
            icon="information-outline",
            theme_text_color="Custom",
            text_color=BLU,
            icon_size=dp(20),
            on_release=lambda x: self._show_info(),
        ))
        card.add_widget(title_row)

        # Radio 80k / 100k / 120k
        self.rb_80 = self._radio_row("80.000 km", 80000)
        self.rb_100 = self._radio_row("100.000 km", 100000)
        self.rb_120 = self._radio_row("120.000 km", 120000)
        card.add_widget(self.rb_80["row"])
        card.add_widget(self.rb_100["row"])
        card.add_widget(self.rb_120["row"])

        # Km ultima sostituzione (obbligatorio)
        self.field_ultimo = MDTextField(
            hint_text="Km dell’ultima sostituzione (obbligatorio)",
            input_filter="int",
            mode="rectangle",
            line_color_normal=BLU,
            line_color_focus=BLU,
            size_hint_y=None,
            height=dp(48),
        )
        self.field_ultimo.bind(text=self._on_changed)
        card.add_widget(self.field_ultimo)

        # Data sostituzione (opzionale) — solo promemoria
        self.field_data = MDTextField(
            hint_text="Data sostituzione (opzionale)  gg/mm/aaaa",
            mode="rectangle",
            line_color_normal=BLU,
            line_color_focus=BLU,
            size_hint_y=None,
            height=dp(48),
        )
        self.field_data.bind(text=self._on_changed)
        card.add_widget(self.field_data)

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

        cb = MDCheckbox(group="cinghia_interval")
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
        self.intervallo_km = int(value)
        self._update_view()

    # =========================================================
    # LOAD
    # =========================================================
    def _load_values(self):
        if not getattr(self, "current_auto", None):
            return

        cg = self.current_auto.get("cinghia", {}) or {}

        self.intervallo_km = int(cg.get("intervallo_km", 100000) or 100000)

        ultimo = cg.get("ultimo_km", None)
        self.field_ultimo.text = "" if ultimo is None else str(ultimo)

        self.field_data.text = (cg.get("data", "") or "").strip()

        self.rb_80["cb"].active = (self.intervallo_km == 80000)
        self.rb_100["cb"].active = (self.intervallo_km == 100000)
        self.rb_120["cb"].active = (self.intervallo_km == 120000)

    def _on_changed(self, instance, value):
        self._update_view()

    # =========================================================
    # CALCO PROSSIMO (solo km)
    # =========================================================
    def _update_view(self):
        txt = self.field_ultimo.text.strip()
        if not txt.isdigit():
            self.lbl_prossimo.text = "Prossima sostituzione: —"
            return

        ultimo = int(txt)
        prossimo = ultimo + int(getattr(self, "intervallo_km", 100000))
        self.lbl_prossimo.text = f"Prossima sostituzione: {prossimo} km"

    # =========================================================
    # SALVA
    # =========================================================
    def _save_values(self):
        if not getattr(self, "current_auto", None):
            self._show_error("Nessuna auto selezionata.")
            return

        txt = self.field_ultimo.text.strip()
        if not txt.isdigit():
            self._show_error("Inserisci i km dell’ultima sostituzione.")
            return

        ultimo_km = int(txt)
        intervallo = int(getattr(self, "intervallo_km", 100000))
        prossimo_km = ultimo_km + intervallo
        data_txt = self.field_data.text.strip()

        # Stato: giallo se entro ~15% intervallo (min 1000 km) — SOLO KM
        try:
            km_attuali = int(self.current_auto.get("km", 0) or 0)
        except:
            km_attuali = 0

        soglia_gialla = max(1000, int(intervallo * 0.15))

        if km_attuali >= prossimo_km:
            stato = "🔴"
        elif (prossimo_km - km_attuali) <= soglia_gialla:
            stato = "🟡"
        else:
            stato = "⚪"

        # Blocco specifico
        self.current_auto.setdefault("cinghia", {})
        self.current_auto["cinghia"]["intervallo_km"] = intervallo
        self.current_auto["cinghia"]["ultimo_km"] = ultimo_km
        self.current_auto["cinghia"]["prossimo_km"] = prossimo_km
        self.current_auto["cinghia"]["data"] = data_txt

        # Scadenze (per DetailAuto)
        scad = self.current_auto.setdefault("scadenze", {})
        scad["cinghia"] = {
            "ultimo": str(ultimo_km),
            "prossimo": str(prossimo_km),
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
            title="Intervallo d’utilizzo",
            text=(
                "Indica dopo quanti chilometri, in media, la cinghia di distribuzione "
                "andrebbe sostituita.\n\n"
                "Lo stato viene calcolato sui km.\n"
                "La data serve solo come promemoria."
            ),
            buttons=[MDRaisedButton(text="OK", md_bg_color=BLU, on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def _go_back(self):
        self.manager.current = "detail_auto"
