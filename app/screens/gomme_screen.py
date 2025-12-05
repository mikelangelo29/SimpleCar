import json
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.pickers import MDDatePicker

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex


BLU_NOTTE = get_color_from_hex("0D1B2A")


class GommeScreen(MDScreen):

    # ==========================================================
    # INIT GOMME — crea struttura se manca
    # ==========================================================
    def init_gomme(self):
        auto = self.current_auto

        if "gomme" not in auto:
            auto["gomme"] = {
                "tipo": "4stagioni",
                "intervallo": None,
                "km_ultimo_cambio": None,
                "data_montaggio": None,
                "montate": None,
                "estive": {
                    "intervallo": None,
                    "km_ultimo_cambio": None,
                    "data_montaggio": None
                },
                "invernali": {
                    "intervallo": None,
                    "km_ultimo_cambio": None,
                    "data_montaggio": None
                }
            }
            self.save_json()

    # ==========================================================
    # CALCOLI
    # ==========================================================
    def km_fatti(self, treno):
        auto_km = self.current_auto.get("km", 0)
        ultimo = treno.get("km_ultimo_cambio")
        if ultimo is None:
            return 0
        return max(0, auto_km - ultimo)

    def km_residui(self, treno):
        intervallo = treno.get("intervallo")
        if not intervallo:
            return None
        return intervallo - self.km_fatti(treno)

    def get_stato(self, residui):
        if residui is None:
            return "—"
        if residui > 5000:
            return "🟢 Regolare"
        elif residui > 0:
            return "🟡 In scadenza"
        return "🔴 Da sostituire"

    # ==========================================================
    def on_pre_enter(self):
        self.init_gomme()
        self.build_ui()

    # ==========================================================
    def build_ui(self):

        self.clear_widgets()

        auto = self.current_auto
        gomme = auto["gomme"]

        root = FloatLayout()
        self.add_widget(root)

        main = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
        )
        root.add_widget(main)

        # TOP BAR
        topbar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(70),
            padding=[15, 15, 15, 15],
            spacing=dp(15),
            md_bg_color=BLU_NOTTE,
        )
        btn_back = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=lambda x: self.go_back()
        )
        titolo = MDLabel(
            text="Gomme",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H5"
        )

        topbar.add_widget(btn_back)
        topbar.add_widget(titolo)
        main.add_widget(topbar)

        scroll = MDScrollView()
        main.add_widget(scroll)

        container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(25),
            padding=dp(20),
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter("height"))
        scroll.add_widget(container)

        # TIPO SET
        container.add_widget(
            MDLabel(
                text="TIPO DI SET",
                font_style="H5",
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(48),
                padding=[0, 10, 0, 10],
            )
        )

        # SET UNICO
        row1 = MDBoxLayout(size_hint_y=None, height=dp(40))
        self.rb_unico = MDCheckbox(group="setg", active=gomme["tipo"] == "4stagioni")
        row1.add_widget(MDLabel(text="Set unico (4 stagioni)", font_style="Body1"))
        row1.add_widget(self.rb_unico)
        container.add_widget(row1)

        # DOPPIO
        row2 = MDBoxLayout(size_hint_y=None, height=dp(40))
        self.rb_doppio = MDCheckbox(group="setg", active=gomme["tipo"] == "doppio")
        row2.add_widget(MDLabel(text="Doppio set (estive + invernali)", font_style="Body1"))
        row2.add_widget(self.rb_doppio)
        container.add_widget(row2)

        self.rb_unico.bind(active=self.on_set_change)
        self.rb_doppio.bind(active=self.on_set_change)

        container.add_widget(
            MDBoxLayout(size_hint_y=None, height=dp(1), md_bg_color=(0.85, 0.85, 0.85, 1))
        )

        # SEZIONI
        self.sections_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(30),
            size_hint_y=None,
        )
        self.sections_box.bind(minimum_height=self.sections_box.setter("height"))
        container.add_widget(self.sections_box)

        # Box
        self.box_4s = self._create_box("Quattro stagioni")
        self.box_est = self._create_box("Estive")
        self.box_inv = self._create_box("Invernali")

        if gomme["tipo"] == "4stagioni":
            self.show_unico()
        else:
            self.show_doppio()

        # SALVA
        salva = MDRaisedButton(
            text="SALVA",
            md_bg_color=BLU_NOTTE,
            pos_hint={"center_x": 0.5},
            on_release=self.save
        )
        container.add_widget(salva)

        overlay = Image(
            source="app/assets/tyre.png",
            size_hint=(None, None),
            height=dp(60),
            width=dp(60),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"right": 0.98, "y": 0.03}
        )
        root.add_widget(overlay)

    # ==========================================================
    def _create_box(self, titolo):

        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[0, 8, 0, 8],
            size_hint_y=None,
        )
        box.bind(minimum_height=box.setter("height"))

        box.add_widget(
            MDLabel(
                text=titolo.capitalize(),
                font_style="H6",
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(32),
                padding=[0, 10, 0, 8],
            )
        )

        # INTERVALLO
        box.add_widget(MDLabel(
            text="Scegli il tuo intervallo:",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(26)
        ))

        km_row = MDBoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(40)
        )

        km35 = MDCheckbox(group=f"km_{titolo}")
        km45 = MDCheckbox(group=f"km_{titolo}")
        km50 = MDCheckbox(group=f"km_{titolo}")

        km_row.add_widget(self._row(km35, "35000"))
        km_row.add_widget(self._row(km45, "45000"))
        km_row.add_widget(self._row(km50, "50000"))

        box.km_opts = [km35, km45, km50]

        box.add_widget(km_row)

        # CAMPI CALCOLATI
        box.label_fatti = MDLabel(
            text="Km fatti: —",
            font_style="Body2",
            size_hint_y=None,
            height=dp(22)
        )
        box.add_widget(box.label_fatti)

        box.label_residui = MDLabel(
            text="Km residui: —",
            font_style="Body2",
            size_hint_y=None,
            height=dp(22)
        )
        box.add_widget(box.label_residui)

        box.label_stato = MDLabel(
            text="Stato: —",
            font_style="Body2",
            size_hint_y=None,
            height=dp(22)
        )
        box.add_widget(box.label_stato)

        box.add_widget(MDLabel(size_hint_y=None, height=dp(10)))

        # DATA + PULSANTE MONTA
        box.data = MDTextField(hint_text=f"Data montaggio {titolo}", readonly=True)
        box.data.bind(on_focus=lambda inst, foc, d=box.data: foc and self.open_calendar(d))
        box.add_widget(box.data)

        btn_monta = MDRaisedButton(
            text=f"MONTA {titolo.upper()}",
            md_bg_color=BLU_NOTTE,
            on_release=lambda x, t=titolo: self.monta_treno(t)
        )
        box.add_widget(btn_monta)

        return box

    # ==========================================================
    def _row(self, check, text):
        r = MDBoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(12),
        )
        r.add_widget(check)
        label = MDLabel(
            text=text,
            font_size="14sp",
            halign="left",
            size_hint_x=None,
            width=dp(56)
        )
        r.add_widget(label)
        return r

    # ==========================================================
    # SET UNICO / DOPPIO
    # ==========================================================
    def on_set_change(self, inst, val):
        if inst is self.rb_unico and val:
            self.current_auto["gomme"]["tipo"] = "4stagioni"
            self.save_json()
            self.show_unico()
        elif inst is self.rb_doppio and val:
            self.current_auto["gomme"]["tipo"] = "doppio"
            self.save_json()
            self.show_doppio()

    def show_unico(self):
        self.sections_box.clear_widgets()
        self.sections_box.add_widget(self.box_4s)

    def show_doppio(self):
        self.sections_box.clear_widgets()
        self.sections_box.add_widget(self.box_est)
        self.sections_box.add_widget(self.box_inv)

    # ==========================================================
    def open_calendar(self, field):
        self._field = field
        picker = MDDatePicker()
        picker.bind(on_save=self.set_date)
        picker.open()

    def set_date(self, inst, value, date_range):
        self._field.text = value.strftime("%d/%m/%Y")

    # ==========================================================
    def monta_treno(self, titolo):

        auto = self.current_auto
        gomme = auto["gomme"]
        km_auto = auto.get("km", 0)

        if gomme["tipo"] == "4stagioni":
            gomme["km_ultimo_cambio"] = km_auto
            gomme["data_montaggio"] = None

        else:
            if titolo.lower() == "estive":
                gomme["montate"] = "estive"
                gomme["estive"]["km_ultimo_cambio"] = km_auto
            else:
                gomme["montate"] = "invernali"
                gomme["invernali"]["km_ultimo_cambio"] = km_auto

        self.save_json()
        self.build_ui()

    # ==========================================================
    def save(self, *args):
        self.save_json()
        self.build_ui()

    # ==========================================================
    def save_json(self):
        path = "app/data/autos.json"

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])

        # Trova l’auto corrente nel JSON
        for idx, a in enumerate(autos):
            if a["modello"] == self.current_auto["modello"] and a["targa"] == self.current_auto["targa"]:
                autos[idx] = self.current_auto
                break

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ==========================================================
    def go_back(self):
        self.manager.current = "detail_auto"

