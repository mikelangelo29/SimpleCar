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

import os  # lo lasciamo, non dà fastidio

# ✅ NUOVO: runtime storage (file VIVO)
from app.storage.data_store import load_data, save_data, ensure_live_file


BLU = get_color_from_hex("0D1B2A")
CARD_BG = (0.94, 0.97, 1.00, 1)          # #F0F6FF
BORDO = BLU


class TagliandoScreen(MDScreen):
    """
    Screen Tagliando — stile coerente con Revisione (top bar 80 + immagine centrata).
    Lo stato NON viene mostrato qui: viene salvato in scadenze per DetailAuto.
    """

   
    # =========================================================
    # CICLO DI VITA
    # =========================================================
    def on_pre_enter(self, *args):
        self._ensure_structure()
        self._build_ui()
        self._load_values()
        self._update_view()

    # =========================================================
    # STRUTTURA BASE
    # =========================================================
    def _ensure_structure(self):
        if not getattr(self, "current_auto", None):
            return

        tag = self.current_auto.get("tagliando")
        if not isinstance(tag, dict):
            tag = {}

        tag.setdefault("intervallo_km", 15000)
        tag.setdefault("ultimo_km", None)
        tag.setdefault("prossimo_km", None)

        self.current_auto["tagliando"] = tag

        # Salvataggio "soft" (non richiede current_auto_index)
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

        # ---------- TOP BAR (identico a Revisione: 80) ----------
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
            text="Tagliando",
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

        # ---------- IMMAGINE (come Revisione, NO overlay) ----------
        img_box = MDBoxLayout(size_hint_y=None, height=dp(140))
        try:
            img = Image(
                source="app/assets/icons/tagliando.png",
                size_hint=(None, None),
                width=dp(150),
                height=dp(150),
                allow_stretch=True,
                keep_ratio=True,
            )
            img_box.add_widget(MDBoxLayout())
            img_box.add_widget(img)
            img_box.add_widget(MDBoxLayout())
        except:
            img_box.add_widget(MDLabel(text="🛠️", halign="center", font_style="H1"))

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

        # titolo
        card.add_widget(MDLabel(
            text="Ogni quanti km fai il tagliando?",
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=BLU,
            size_hint_y=None,
            height=dp(28),
        ))

        # radio group
        self.rb_10 = self._radio_row("10.000 km", 10000)
        self.rb_15 = self._radio_row("15.000 km", 15000)
        self.rb_20 = self._radio_row("20.000 km", 20000)
        card.add_widget(self.rb_10["row"])
        card.add_widget(self.rb_15["row"])
        card.add_widget(self.rb_20["row"])

        # ultimo km
        self.field_ultimo = MDTextField(
            hint_text="Km dell’ultimo tagliando (obbligatorio)",
            input_filter="int",
            mode="rectangle",
            line_color_normal=BLU,
            line_color_focus=BLU,
            size_hint_y=None,
            height=dp(48),
        )
        self.field_ultimo.bind(text=self._on_changed)
        card.add_widget(self.field_ultimo)

        # prossimo (solo info)
        self.lbl_prossimo = MDLabel(
            text="Prossimo tagliando: —",
            font_style="Subtitle2",
            theme_text_color="Custom",
            text_color=BLU,
            halign="center",
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(self.lbl_prossimo)

        # ---------- BOTTONI (come Revisione: Annulla + Salva) ----------
        buttons = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=None,
            height=dp(60),
        )
        buttons.add_widget(MDFlatButton(text="ANNULLA", on_release=lambda x: self._go_back()))
        buttons.add_widget(MDRaisedButton(text="SALVA", on_release=lambda x: self._save_values()))
        container.add_widget(buttons)

        # spazio finale
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

        cb = MDCheckbox(group="tagliando_interval")
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

        tag = self.current_auto.get("tagliando", {}) or {}
        self.intervallo_km = int(tag.get("intervallo_km", 15000) or 15000)

        ultimo = tag.get("ultimo_km", None)
        self.field_ultimo.text = "" if ultimo is None else str(ultimo)

        # radio attivo
        self.rb_10["cb"].active = (self.intervallo_km == 10000)
        self.rb_15["cb"].active = (self.intervallo_km == 15000)
        self.rb_20["cb"].active = (self.intervallo_km == 20000)

    def _on_changed(self, instance, value):
        self._update_view()

    # =========================================================
    # CALCOLO (solo prossimo)
    # =========================================================
    def _update_view(self):
        txt = self.field_ultimo.text.strip()
        if not txt.isdigit():
            self.lbl_prossimo.text = "Prossimo tagliando: —"
            return

        ultimo = int(txt)
        prossimo = ultimo + int(getattr(self, "intervallo_km", 15000))
        self.lbl_prossimo.text = f"Prossimo tagliando: {prossimo} km"

    # =========================================================
    # SALVA (scrive anche scadenze per DetailAuto)
    # =========================================================
    def _save_values(self):
        if not getattr(self, "current_auto", None):
            self._show_error("Nessuna auto selezionata.")
            return

        txt = self.field_ultimo.text.strip()
        if not txt.isdigit():
            self._show_error("Inserisci i km dell’ultimo tagliando.")
            return

        ultimo_km = int(txt)
        intervallo = int(getattr(self, "intervallo_km", 15000))
        prossimo_km = ultimo_km + intervallo

        # ---- stato (coerente con Gomme: ~15% intervallo, min 1000 km) ----
        km_attuali = 0
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

        # ---- salva blocco interno tagliando ----
        self.current_auto.setdefault("tagliando", {})
        self.current_auto["tagliando"]["intervallo_km"] = intervallo
        self.current_auto["tagliando"]["ultimo_km"] = ultimo_km
        self.current_auto["tagliando"]["prossimo_km"] = prossimo_km

        # ---- salva in scadenze (per DetailAuto) ----
        scad = self.current_auto.setdefault("scadenze", {})
        scad["tagliando"] = {
            "ultimo": str(ultimo_km),
            "prossimo": str(prossimo_km),
            "stato": stato
        }

        # ---- persist autos.json (FILE VIVO) ----
        if hasattr(self, "current_auto_index"):
            self._save_by_index()
        else:
            self._save_full_fallback()

        self._go_back()

    # ✅ MODIFICATO: salva sul file VIVO, non sul seed
    def _save_by_index(self):
        ensure_live_file()
        data = load_data()

        idx = int(self.current_auto_index)
        autos = data.get("autos", [])
        if 0 <= idx < len(autos):
            autos[idx] = self.current_auto
            data["autos"] = autos
            save_data(data)

    # ✅ MODIFICATO: salva sul file VIVO, non sul seed
    def _save_full_fallback(self):
        ensure_live_file()
        data = load_data()

        autos = data.get("autos", [])
        for a in autos:
            if (
                a.get("marca") == self.current_auto.get("marca")
                and a.get("modello") == self.current_auto.get("modello")
                and a.get("targa") == self.current_auto.get("targa")
            ):
                a.update(self.current_auto)
                break

        data["autos"] = autos
        save_data(data)

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

    def _show_info(self):
        dialog = MDDialog(
            title="Come funziona il tagliando?",
            text=(
                "1) Scegli ogni quanti km fai il tagliando\n"
                "2) Inserisci i km dell’ultimo tagliando\n"
                "3) EasyCar calcola il prossimo\n\n"
                "Lo stato (Regolare / In scadenza / Scaduto)\n"
                "viene mostrato nel dettaglio auto."
            ),
            buttons=[MDRaisedButton(text="OK", md_bg_color=BLU, on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def _go_back(self):
        self.manager.current = "detail_auto"
