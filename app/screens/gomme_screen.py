from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import json
import os


BLU = get_color_from_hex("0D1B2A")
VERDE = (0.00, 0.42, 0.30, 1)
ROSSO = (0.91, 0.26, 0.26, 1)
PURPLE = (0.36, 0.29, 0.55, 1)

CARD_ACTIVE = (0.92, 0.96, 1.00, 1)   # bianco-azzurro elegante
CARD_INACTIVE = (0.96, 0.96, 0.96, 1) # grigio molto chiaro

BORDO_ACTIVE = BLU



class GommeScreen(MDScreen):
    """Screen gestione gomme.

    Prima di entrare:
        gomme_screen = manager.get_screen("gomme")
        gomme_screen.current_auto = self.auto
    """

    data_path = "app/data/autos.json"

    # =========================================================
    # CICLO DI VITA
    # =========================================================
    def on_pre_enter(self, *args):
        self._ensure_structure()
        self._build_ui()
        self._load_values()
        self._update_view()

    # =========================================================
    # STRUTTURA BASE GOMME
    # =========================================================
    def _ensure_structure(self):
        """Garantisce che current_auto abbia il blocco gomme
        con almeno Treno 1 e un 'attivo' valido.
        """
        if not getattr(self, "current_auto", None):
            return

        gomme = self.current_auto.get("gomme")
        if not isinstance(gomme, dict):
            gomme = {}

        # Treno 1 sempre presente
        if "t1" not in gomme:
            gomme["t1"] = {"km_montaggio": None}

        # Treno attivo
        if gomme.get("attivo") not in ("t1", "t2"):
            gomme["attivo"] = "t1"

        self.current_auto["gomme"] = gomme
        self._save_full()

    # =========================================================
    # COSTRUZIONE UI
    # =========================================================
    def _build_ui(self):
        self.clear_widgets()

        root = FloatLayout()
        self.add_widget(root)

        main = MDBoxLayout(orientation="vertical")
        root.add_widget(main)

        # ---------- TOP BAR ----------
        top = MDBoxLayout(
            size_hint_y=None,
            height=dp(70),
            padding=[15, 15, 15, 15],
            md_bg_color=BLU,
        )
        back = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1),
            on_release=lambda x: self._go_back(),
        )
        
        top.add_widget(back)
        
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

        # ---------- TRENO 1 ----------
        self.card_t1 = self._create_card("Treno 1", "t1")
        container.add_widget(self.card_t1)

        # ---------- TOGGLE TRENO 2 (AGGIUNGI / ELIMINA) ----------
        self.btn_t2_toggle = MDRaisedButton(
            text="+ AGGIUNGI TRENO 2",
            md_bg_color=BLU,
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(45),
            on_release=lambda x: self._toggle_t2(),
        )
        container.add_widget(self.btn_t2_toggle)

        # Card Treno 2 (inserita solo se esiste in dati)
        self.card_t2 = self._create_card("Treno 2", "t2")

        # ---------- SALVA ----------
        self.btn_save = MDRaisedButton(
            text="SALVA",
            md_bg_color=BLU,
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(48),
            on_release=lambda x: self._save_values(),
        )
        container.add_widget(self.btn_save)

        # ---------- "TACHIMETRO" KM AUTO + AGGIORNA ----------
        tacho_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80),
        )

        tacho_box = MDBoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(4),
            md_bg_color=(0.97, 0.97, 0.97, 1),
        )
        tacho_label = MDLabel(
            text="Km attuali auto",
            font_style="Caption",
            halign="left",
        )
        self.lbl_master_value = MDLabel(
            text="— km",
            font_style="H5",
            halign="left",
        )
        tacho_box.add_widget(tacho_label)
        tacho_box.add_widget(self.lbl_master_value)
        tacho_row.add_widget(tacho_box)

        self.btn_update_km = MDRaisedButton(
            text="AGGIORNA KM",
            md_bg_color=(1, 1, 1, 1),
            text_color=BLU,
            size_hint=(None, None),
            width=dp(140),
            height=dp(48),
            on_release=lambda x: self._popup_update_km(),
        )
        tacho_row.add_widget(self.btn_update_km)

        container.add_widget(tacho_row)

        # ---------- SWITCH T1 / T2 ----------
        self.btn_switch = MDRaisedButton(
            text="",
            md_bg_color=BLU,
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(46),
            on_release=lambda x: self._switch_trains(),
        )
        self.btn_switch.opacity = 0
        self.btn_switch.disabled = True
        container.add_widget(self.btn_switch)

        # ---------- FRASE ESPLICATIVA IN FONDO ----------
        container.add_widget(
            MDLabel(
                text=(
                    "Quando monti un treno, il conteggio dei suoi km "
                    "parte dal chilometraggio attuale.\n"
                    "Gli altri treni si fermano finché non li rimonti."
                ),
                font_style="Caption",
                halign="left",
                size_hint_y=None,
                height=dp(50),
            )
        )

        # Icona overlay
        overlay = Image(
            source="app/assets/tyre.png",
            size_hint=(None, None),
            width=dp(60),
            height=dp(60),
            pos_hint={"right": 0.98, "y": 0.02},
        )
        root.add_widget(overlay)

    # =========================================================
    # CREAZIONE CARD TRENO
    # =========================================================
    def _create_card(self, title, key):
        box = MDBoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            md_bg_color=CARD_INACTIVE,
        )
        box.bind(minimum_height=box.setter("height"))
        box.tr_key = key

        header = MDBoxLayout(size_hint_y=None, height=dp(30))
        lbl = MDLabel(text=title, font_style="H6", bold=True)
        badge = MDLabel(text="", halign="right", font_style="Caption")
        box.lbl_badge = badge
        header.add_widget(lbl)
        header.add_widget(badge)
        box.add_widget(header)

        box.km = MDTextField(
            hint_text="Km al montaggio (obbligatorio)",
            input_filter="int",
            size_hint_y=None,
            height=dp(48),
        )
        box.km.bind(text=self._km_changed)
        box.add_widget(box.km)

        box.lbl_percorsi = MDLabel(
            text="Km percorsi: —",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
        )
        box.add_widget(box.lbl_percorsi)

        return box

    # =========================================================
    # CARICAMENTO VALORI
    # =========================================================
    def _load_values(self):
        gomme = self.current_auto.get("gomme", {})
        km_master = self.current_auto.get("km", 0)
        self.lbl_master_value.text = f"{km_master} km"

        # Treno 1
        t1 = gomme.get("t1", {})
        if t1.get("km_montaggio") is not None:
            self.card_t1.km.text = str(t1["km_montaggio"])

        # Treno 2
        if "t2" in gomme:
            parent = self.btn_t2_toggle.parent
            if self.card_t2 not in parent.children:
                idx = parent.children.index(self.btn_t2_toggle)
                parent.add_widget(self.card_t2, index=idx)

            t2 = gomme.get("t2", {})
            if t2.get("km_montaggio") is not None:
                self.card_t2.km.text = str(t2["km_montaggio"])

            # ← QUI: COLORE ROSSO
            self.btn_t2_toggle.text = "- ELIMINA TRENO 2"
            self.btn_t2_toggle.md_bg_color = ROSSO

        else:
            # ← QUI: COLORE VERDE SMERALDO
            self.btn_t2_toggle.text = "+ AGGIUNGI TRENO 2"
            self.btn_t2_toggle.md_bg_color = VERDE

    # =========================================================
    # AGGIORNAMENTO GRAFICA E CALCOLI
    # =========================================================
    def _update_view(self):
        gomme = self.current_auto.get("gomme", {})
        attivo = gomme.get("attivo", "t1")
        km_master = self.current_auto.get("km", 0)

        # ----------------------------------------------------------
        # Calcolo km percorsi per ogni treno
        # ----------------------------------------------------------
        def fill(box):
            txt = box.km.text.strip()
            if not txt.isdigit():
                box.lbl_percorsi.text = "Km percorsi: —"
                return
            km_m = int(txt)
            box.lbl_percorsi.text = f"Km percorsi: {max(0, km_master - km_m)}"

        fill(self.card_t1)
        if "t2" in gomme:
            fill(self.card_t2)

        # ----------------------------------------------------------
        # Evidenziazione treno montato
        # ----------------------------------------------------------

        if attivo == "t1":
            # Treno 1 attivo
            self.card_t1.md_bg_color = CARD_ACTIVE
            self.card_t1.line_color = BORDO_ACTIVE   # blu notte
            self.card_t1.line_width = 2
            self.card_t1.lbl_badge.text = "MONTATO ORA"

            # Treno 2 inattivo
            if hasattr(self, "card_t2"):
                self.card_t2.md_bg_color = CARD_INACTIVE
                self.card_t2.line_color = (0, 0, 0, 0)  # bordo invisibile
                self.card_t2.lbl_badge.text = ""

        else:
            # Treno 2 attivo
            if hasattr(self, "card_t2"):
                self.card_t2.md_bg_color = CARD_ACTIVE
                self.card_t2.line_color = BORDO_ACTIVE   # blu notte
                self.card_t2.line_width = 2
                self.card_t2.lbl_badge.text = "MONTATO ORA"

            # Treno 1 inattivo
            self.card_t1.md_bg_color = CARD_INACTIVE
            self.card_t1.line_color = (0, 0, 0, 0)
            self.card_t1.lbl_badge.text = ""



        # ----------------------------------------------------------
        # Switch attivo solo se esiste T2
        # ----------------------------------------------------------
        if "t2" in gomme:
            self.btn_switch.disabled = False
            self.btn_switch.opacity = 1

            if attivo == "t1":
                self.btn_switch.text = "SMONTA T1 → MONTA T2"
            else:
                self.btn_switch.text = "SMONTA T2 → MONTA T1"

            # ⭐ COLORE PERSONALIZZATO DEL BOTTONE SMONTA/MONTA
            self.btn_switch.md_bg_color = PURPLE

        else:
            self.btn_switch.disabled = True
            self.btn_switch.opacity = 0


    def _km_changed(self, instance, value):
        """Aggiorna i km percorsi live mentre digiti."""
        self._update_view()

    # =========================================================
    # AZIONI UTENTE
    # =========================================================

    def _toggle_t2(self):
        gomme = self.current_auto.get("gomme", {})
        parent = self.btn_t2_toggle.parent

        if "t2" in gomme:
            # --------- ELIMINA TRENO 2 ----------
            gomme.pop("t2", None)

            if self.card_t2 in parent.children:
                parent.remove_widget(self.card_t2)

            # Se stava montato T2 torna T1
            if gomme.get("attivo") == "t2":
                gomme["attivo"] = "t1"

            self.btn_t2_toggle.text = "+ AGGIUNGI TRENO 2"
            self.btn_t2_toggle.md_bg_color = VERDE

        else:
            # --------- AGGIUNGI TRENO 2 ----------
            gomme["t2"] = {"km_montaggio": None}

            if self.card_t2 not in parent.children:
                idx = parent.children.index(self.btn_t2_toggle)
                parent.add_widget(self.card_t2, index=idx)

            self.btn_t2_toggle.text = "- ELIMINA TRENO 2"
            self.btn_t2_toggle.md_bg_color = ROSSO

        self.current_auto["gomme"] = gomme
        self._save_full()
        self._update_view()


    def _switch_trains(self):
        """Cambia il treno montato (T1 ↔ T2)."""
        gomme = self.current_auto.get("gomme", {})
        attivo = gomme.get("attivo", "t1")
        if "t2" not in gomme:
            return

        self._show("Ricorda: aggiorna i km dell'auto prima di cambiare treno.")

        gomme["attivo"] = "t2" if attivo == "t1" else "t1"
        self.current_auto["gomme"] = gomme
        self._save_full()
        self._update_view()

    def _save_values(self):
        """Salva i km di montaggio per T1 e T2."""
        gomme = self.current_auto.get("gomme", {})

        # T1 obbligatorio
        km1_txt = self.card_t1.km.text.strip()
        if not km1_txt.isdigit():
            self._show("Inserisci i km del Treno 1.")
            return
        gomme.setdefault("t1", {})["km_montaggio"] = int(km1_txt)

        # T2 opzionale
        if "t2" in gomme:
            km2_txt = self.card_t2.km.text.strip()
            if km2_txt:
                if not km2_txt.isdigit():
                    self._show("I km del Treno 2 devono essere numerici.")
                    return
                gomme["t2"]["km_montaggio"] = int(km2_txt)

        self.current_auto["gomme"] = gomme
        self._save_full()
        self._update_view()
        self._show("Dati salvati.")

    def _popup_update_km(self):
        """Popup per aggiornare il chilometraggio master dell'auto."""
        dialog = None
        field = MDTextField(
            hint_text="Km attuali",
            input_filter="int",
            size_hint_y=None,
            height=dp(48),
        )

        def save_new_km(x):
            txt = field.text.strip()
            if not txt.isdigit():
                self._show("Inserisci un valore numerico.")
                return
            self.current_auto["km"] = int(txt)
            self._save_full()
            self._load_values()
            self._update_view()
            dialog.dismiss()

        dialog = MDDialog(
            title="Aggiorna chilometri",
            type="custom",
            content_cls=field,
            buttons=[
                MDRaisedButton(
                    text="ANNULLA",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="OK",
                    md_bg_color=BLU,
                    on_release=save_new_km,
                ),
            ],
        )
        dialog.open()

    # =========================================================
    # PERSISTENZA
    # =========================================================
    def _save_full(self):
        """Salva current_auto dentro autos.json."""
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
    # UTILITY
    # =========================================================
    def _show(self, msg):
        dialog = MDDialog(
            title="Gomme",
            text=msg,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=BLU,
                    on_release=lambda x: dialog.dismiss(),
                )
            ],
        )
        dialog.open()

    def _go_back(self):
        self.manager.current = "detail_auto"
