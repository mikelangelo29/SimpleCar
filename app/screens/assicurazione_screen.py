from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from app.storage.data_store import load_data, save_data, ensure_live_file
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


class AssicurazioneScreen(MDScreen):
    """
    Screen Assicurazione — schema base EasyCar:
    top bar 80 + immagine centrata + card unica + RADIO durata (6/12 mesi)
    + decorrenza + importo opzionale + label scadenza/stato + ANNULLA/SALVA.

    Salvataggio standard:
    - auto["assicurazione"] = {durata_mesi, decorrenza, scadenza, importo}
    - auto["scadenze"]["assicurazione"] = {ultimo, prossimo, stato}  con stato ⚪🟡🔴
    """

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

        blk = self.current_auto.get("assicurazione")
        if not isinstance(blk, dict):
            blk = {}

        blk.setdefault("durata_mesi", 12)     # default annuale
        blk.setdefault("decorrenza", "")
        blk.setdefault("scadenza", "")
        blk.setdefault("importo", None)

        self.current_auto["assicurazione"] = blk

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
            text="Assicurazione",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H4",
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

        # piccolo spacer sotto top bar (coerente)
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
                source=os.path.join("app", "assets", "icons", "assicurazione.png"),
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
            img_box.add_widget(MDLabel(text="🛡️", halign="center", font_style="H1"))

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

        card.add_widget(MDLabel(
            text="Durata polizza",
            theme_text_color="Custom",
            text_color=BLU,
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        # RADIO durata
        self.rb_semestrale = self._radio_row("Semestrale (6 mesi)", 6)
        self.rb_annuale = self._radio_row("Annuale (12 mesi)", 12)
        card.add_widget(self.rb_semestrale)
        card.add_widget(self.rb_annuale)

        # Decorrenza
        card.add_widget(MDLabel(
            text="Decorrenza (inizio copertura)",
            theme_text_color="Custom",
            text_color=BLU,
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        self.field_decorrenza = MDTextField(
            hint_text="gg/mm/aaaa",
            mode="rectangle",
            size_hint_y=None,
            height=dp(46),
        )
        self.field_decorrenza.bind(text=lambda *a: self._update_view())
        card.add_widget(self.field_decorrenza)

        # Importo (opzionale)
        card.add_widget(MDLabel(
            text="Importo (€) (opzionale)",
            theme_text_color="Custom",
            text_color=BLU,
            bold=True,
            size_hint_y=None,
            height=dp(24)
        ))

        self.field_importo = MDTextField(
            hint_text="es. 520",
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(46),
        )
        card.add_widget(self.field_importo)

        # label output: scadenza + stato
        self.label_scadenza = MDLabel(
            text="Scadenza calcolata: —",
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
    # RADIO
    # =========================================================
    def _radio_row(self, label, value):
        row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
        )

        cb = MDCheckbox(group="assicurazione_durata")
        cb.bind(active=lambda inst, active, v=value: self._set_durata(v, active))

        lab = MDLabel(
            text=label,
            theme_text_color="Custom",
            text_color=BLU,
            valign="middle",
            halign="left",
        )
        lab.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        row.add_widget(cb)
        row.add_widget(lab)

        # salvo riferimento per selezionare al load
        row._cb = cb
        row._value = value
        return row

    def _set_durata(self, value, active):
        if not active:
            return
        self.durata_mesi = int(value)
        self._update_view()

    # =========================================================
    # LOAD / VIEW
    # =========================================================
    def _load_values(self):
        if not getattr(self, "current_auto", None):
            return

        blk = self.current_auto.get("assicurazione", {})
        durata = int(blk.get("durata_mesi", 12) or 12)
        decor = blk.get("decorrenza", "") or ""
        imp = blk.get("importo", None)

        self.durata_mesi = durata
        self.field_decorrenza.text = decor

        if imp is None:
            self.field_importo.text = ""
        else:
            self.field_importo.text = str(imp)

        # seleziona radio coerente
        if durata == 6:
            self.rb_semestrale._cb.active = True
        else:
            self.rb_annuale._cb.active = True

    def _update_view(self):
        # calcola scadenza e stato solo se decorrenza valida
        durata = int(getattr(self, "durata_mesi", 12) or 12)
        decor = getattr(self, "field_decorrenza", None)
        decor_txt = decor.text.strip() if decor else ""

        if not decor_txt or not self._is_valid_date(decor_txt):
            self.label_scadenza.text = "Scadenza calcolata: —"
            self.label_stato.text = "Stato: —"
            return

        scadenza = self._add_months(decor_txt, durata)
        stato = self._compute_state(scadenza)

        self.label_scadenza.text = f"Scadenza calcolata: {scadenza}"
        self.label_stato.text = f"Stato: {self._stato_to_text(stato)}"
        # colore testo stato (solo testo, niente sfondo)
        self.label_stato.text_color = self._stato_color(stato)

    # =========================================================
    # SAVE
    # =========================================================
    def _save_values(self):
        if not getattr(self, "current_auto", None):
            self._show_error("Nessuna auto selezionata.")
            return

        decorrenza = self.field_decorrenza.text.strip()
        if not decorrenza or not self._is_valid_date(decorrenza):
            self._show_error("Inserisci una data di decorrenza valida (gg/mm/aaaa).")
            return

        durata = int(getattr(self, "durata_mesi", 12) or 12)
        if durata not in (6, 12):
            durata = 12

        scadenza = self._add_months(decorrenza, durata)
        stato = self._compute_state(scadenza)

        imp_txt = self.field_importo.text.strip()
        importo = None
        if imp_txt:
            try:
                importo = int(imp_txt)
            except:
                self._show_error("Importo non valido.")
                return

        # ---- blocco specifico ----
        self.current_auto["assicurazione"] = {
            "durata_mesi": durata,
            "decorrenza": decorrenza,
            "scadenza": scadenza,
            "importo": importo
        }

        # ---- scadenze standard (per DetailAuto) ----
        scad = self.current_auto.setdefault("scadenze", {})
        scad["assicurazione"] = {
            "ultimo": decorrenza,
            "prossimo": scadenza,
            "stato": stato
        }

        # ---- persist autos.json ----
        if hasattr(self, "current_auto_index"):
            self._save_by_index()
        else:
            self._save_full_fallback()

        self._go_back()

    # =========================================================
    # DATE / STATE
    # =========================================================
    def _is_valid_date(self, s):
        try:
            d, m, y = self._parse_date(s)
            date(y, m, d)
            return True
        except:
            return False

    def _parse_date(self, s):
        # accetta gg/mm/aaaa ma normalizza anche gg/mm/aa -> gg/mm/20aa
        parts = s.strip().split("/")
        if len(parts) != 3:
            raise ValueError("Formato data")

        d = int(parts[0])
        m = int(parts[1])

        y_str = parts[2].strip()
        if not y_str.isdigit():
            raise ValueError("Anno non valido")

        # --- normalizzazione anno ---
        if len(y_str) == 2:
            # regola pratica: 00-79 -> 2000-2079, 80-99 -> 1980-1999
            yy = int(y_str)
            y = 2000 + yy if yy <= 79 else 1900 + yy
        elif len(y_str) == 4:
            y = int(y_str)
        else:
            raise ValueError("Anno deve essere a 2 o 4 cifre")

        return d, m, y


    def _fmt_date(self, d, m, y):
        return f"{d:02d}/{m:02d}/{y:04d}"

    def _add_months(self, date_str, months):
        d, m, y = self._parse_date(date_str)

        # converti a mese assoluto, poi ricalcola
        total = (y * 12 + (m - 1)) + int(months)
        new_y = total // 12
        new_m = (total % 12) + 1

        # clamp giorno all’ultimo giorno del nuovo mese
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
        # colori testo: rosso / arancio / blu-notte (coerenti senza cambiare sfondo)
        if stato == "🔴":
            return (0.85, 0.1, 0.1, 1)
        if stato == "🟡":
            return (0.95, 0.55, 0.1, 1)
        return BLU

    # =========================================================
    # PERSISTENZA (stesso pattern di DischiFrenoScreen)
    # =========================================================
    def _save_by_index(self):
        ensure_live_file()
        data = load_data()

        idx = int(self.current_auto_index)
        autos = data.get("autos", [])

        if 0 <= idx < len(autos):
            autos[idx] = self.current_auto
            data["autos"] = autos
            save_data(data)


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
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=BLU,
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def _open_info_dialog(self):
        dialog = MDDialog(
            title="Assicurazione",
            text=(
                "Inserisci la data di decorrenza (inizio copertura) e scegli la durata.\n\n"
                "La scadenza viene calcolata automaticamente:\n"
                "• Semestrale = 6 mesi\n"
                "• Annuale = 12 mesi\n\n"
                "Lo stato diventa 'In scadenza' negli ultimi 30 giorni."
            ),
            buttons=[MDRaisedButton(text="OK", md_bg_color=BLU, on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def _go_back(self):
        self.manager.current = "detail_auto"
