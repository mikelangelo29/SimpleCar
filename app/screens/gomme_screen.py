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

CARD_ACTIVE = (0.92, 0.96, 1.00, 1)    # bianco-azzurro elegante
CARD_INACTIVE = (0.96, 0.96, 0.96, 1)  # grigio molto chiaro
AZZURRO_GLACIALE = (0.94, 0.97, 1.00, 1)  # #F0F6FF
BORDO_ACTIVE = BLU


class GommeScreen(MDScreen):
    """Screen gestione gomme (T1/T2).
    Mantiene logica e JSON attuali, ma rende UI più coerente col resto:
    - immagine centrata come gli altri screen
    - niente popup aggiornamento km qui
    - T1 = USATO, T2 = DI RISERVA (solo label)
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

        # ---------- TOP BAR (80dp, come gli altri) ----------
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
            text="Gomme",
            halign="center",
            valign="middle",
            bold=True,
            font_style="H4",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        top.add_widget(title)

        # bilanciamento a destra (niente icona piccola)
        top.add_widget(MDBoxLayout(size_hint_x=0.2))

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

        # spacer “un millimetro”
        container.add_widget(MDBoxLayout(size_hint=(1, None), height=dp(10)))

        # ---------- IMMAGINE (come gli altri) ----------
        img_box = MDBoxLayout(size_hint_y=None, height=dp(140))
        try:
            img = Image(
                source="app/assets/icons/gomme.png",
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

        # ---------- LABEL INFORMATIVA KM AUTO (solo info) ----------
        self.lbl_master_value = MDLabel(
            text="Km auto attuali: —",
            font_style="Subtitle2",
            theme_text_color="Custom",
            text_color=BLU,
            halign="center",
            size_hint_y=None,
            height=dp(24),
        )
        container.add_widget(self.lbl_master_value)

        # ---------- CARD USATO (T1) ----------
        self.card_t1 = self._create_card("SET 1", "t1")
        container.add_widget(self.card_t1)

        # ---------- TOGGLE T2 (AGGIUNGI / ELIMINA) ----------
        self.btn_t2_toggle = MDRaisedButton(
            text="+ AGGIUNGI TRENO 2",
            md_bg_color=BLU,
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(45),
            on_release=lambda x: self._toggle_t2(),
        )
        container.add_widget(self.btn_t2_toggle)

        # Card DI RISERVA (T2) (inserita solo se esiste)
        self.card_t2 = self._create_card("SET 2", "t2")

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

        # ---------- NOTA (come prima, ma coerente) ----------
        nota = MDLabel(
            text=(
                "Quando monti un treno, il conteggio dei suoi km "
                "parte dal chilometraggio attuale.\n"
                "Gli altri treni si fermano finché non li rimonti."
            ),
            font_style="Caption",
            halign="center",
            italic=True,
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(55),
        )
        container.add_widget(nota)

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
        self.lbl_master_value.text = f"Km auto attuali: {km_master} km"

        # T1
        t1 = gomme.get("t1", {})
        if t1.get("km_montaggio") is not None:
            self.card_t1.km.text = str(t1["km_montaggio"])

        # T2
        if "t2" in gomme:
            parent = self.btn_t2_toggle.parent
            if self.card_t2 not in parent.children:
                idx = parent.children.index(self.btn_t2_toggle)
                parent.add_widget(self.card_t2, index=idx)

            t2 = gomme.get("t2", {})
            if t2.get("km_montaggio") is not None:
                self.card_t2.km.text = str(t2["km_montaggio"])

            self.btn_t2_toggle.text = "- ELIMINA TRENO 2"
            self.btn_t2_toggle.md_bg_color = ROSSO
        else:
            self.btn_t2_toggle.text = "+ AGGIUNGI TRENO 2"
            self.btn_t2_toggle.md_bg_color = VERDE

    # =========================================================
    # AGGIORNAMENTO GRAFICA E CALCOLI
    # =========================================================
    def _update_view(self):
        gomme = self.current_auto.get("gomme", {})
        attivo = gomme.get("attivo", "t1")
        km_master = self.current_auto.get("km", 0)

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

        # evidenzia treno in uso
        if attivo == "t1":
            self.card_t1.md_bg_color = CARD_ACTIVE
            self.card_t1.line_color = BORDO_ACTIVE
            self.card_t1.line_width = 2
            self.card_t1.lbl_badge.text = "IN USO"

            if hasattr(self, "card_t2"):
                self.card_t2.md_bg_color = CARD_INACTIVE
                self.card_t2.line_color = (0, 0, 0, 0)
                self.card_t2.lbl_badge.text = ""
        else:
            if hasattr(self, "card_t2"):
                self.card_t2.md_bg_color = CARD_ACTIVE
                self.card_t2.line_color = BORDO_ACTIVE
                self.card_t2.line_width = 2
                self.card_t2.lbl_badge.text = "IN USO"

            self.card_t1.md_bg_color = CARD_INACTIVE
            self.card_t1.line_color = (0, 0, 0, 0)
            self.card_t1.lbl_badge.text = ""

        # switch solo se esiste T2
        if "t2" in gomme:
            self.btn_switch.disabled = False
            self.btn_switch.opacity = 1

            if attivo == "t1":
                self.btn_switch.text = "SMONTA SET 1 → MONTA SET 2"
            else:
                self.btn_switch.text = "SMONTA SET 2 → MONTA SET 1"

            self.btn_switch.md_bg_color = PURPLE
        else:
            self.btn_switch.disabled = True
            self.btn_switch.opacity = 0

    def _km_changed(self, instance, value):
        self._update_view()

    # =========================================================
    # AZIONI UTENTE
    # =========================================================
    def _toggle_t2(self):
        gomme = self.current_auto.get("gomme", {})
        parent = self.btn_t2_toggle.parent

        if "t2" in gomme:
            gomme.pop("t2", None)

            if self.card_t2 in parent.children:
                parent.remove_widget(self.card_t2)

            if gomme.get("attivo") == "t2":
                gomme["attivo"] = "t1"

            self.btn_t2_toggle.text = "+ AGGIUNGI TRENO 2"
            self.btn_t2_toggle.md_bg_color = VERDE
        else:
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
        gomme = self.current_auto.get("gomme", {})
        attivo = gomme.get("attivo", "t1")
        if "t2" not in gomme:
            return

        self._show("Ricorda: aggiorna i km dell'auto in Dettaglio Auto prima di cambiare treno.")
        gomme["attivo"] = "t2" if attivo == "t1" else "t1"
        self.current_auto["gomme"] = gomme
        self._save_full()
        self._update_view()

    # =========================================================
    # SALVATAGGIO GOMME + SCADENZE (come tuo)
    # =========================================================
    def _save_values(self):
        auto = self.current_auto
        gomme = auto.setdefault("gomme", {})

        attivo = gomme.get("attivo", "t1")
        t = gomme.setdefault(attivo, {})

        km_master = auto.get("km", 0)

        txt = self.card_t1.km.text.strip() if attivo == "t1" else self.card_t2.km.text.strip()
        if not txt.isdigit():
            km_montaggio = None
        else:
            km_montaggio = int(txt)

        t["km_montaggio"] = km_montaggio

        INTERVALLO = 45000

        if km_montaggio is None:
            km_percorsi = None
            km_residui = None
            stato = "⚪"
        else:
            km_percorsi = max(0, km_master - km_montaggio)
            km_residui = max(0, INTERVALLO - km_percorsi)

            if km_percorsi >= 45000:
                stato = "🔴"
            elif km_percorsi >= 38000:
                stato = "🟡"
            else:
                stato = "⚪"

        scad = auto.setdefault("scadenze", {})
        scad["gomme"] = {
            "treno": attivo.upper().replace("T", "T"),
            "km_percorsi": km_percorsi if km_percorsi is not None else "—",
            "km_residui": km_residui if km_residui is not None else "—",
            "stato": stato
        }

        # salvataggio per indice (coerente col resto)
        data_path = os.path.join("app", "data", "autos.json")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        idx = self.current_auto_index
        data["autos"][idx] = auto

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.manager.current = "detail_auto"

    # =========================================================
    # PERSISTENZA
    # =========================================================
    def _save_full(self):
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
