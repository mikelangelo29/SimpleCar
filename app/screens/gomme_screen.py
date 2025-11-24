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

    def on_pre_enter(self):
        self.build_ui()

    def build_ui(self):

        self.clear_widgets()

        # ======================================================
        # FLOAT ROOT
        # ======================================================
        root = FloatLayout()
        self.add_widget(root)

        # ======================================================
        # BOX VERTICALE (TOP BAR + CONTENUTO)
        # ======================================================
        main = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
        )
        root.add_widget(main)

        # ======================================================
        # TOP BAR
        # ======================================================
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

        # ======================================================
        # SCROLL AREA
        # ======================================================
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

        # ======================================================
        # TITOLO PRINCIPALE — TIPO DI SET
        # ======================================================
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

        # Row unico
        row1 = MDBoxLayout(size_hint_y=None, height=dp(40))
        self.rb_unico = MDCheckbox(group="setg", active=True)
        row1.add_widget(MDLabel(text="Set unico (4 stagioni)", font_style="Body1"))
        row1.add_widget(self.rb_unico)
        container.add_widget(row1)

        # Row doppio
        row2 = MDBoxLayout(size_hint_y=None, height=dp(40))
        self.rb_doppio = MDCheckbox(group="setg")
        row2.add_widget(MDLabel(text="Doppio set (estive + invernali)", font_style="Body1"))
        row2.add_widget(self.rb_doppio)
        container.add_widget(row2)

        self.rb_unico.bind(active=self.on_set_change)
        self.rb_doppio.bind(active=self.on_set_change)

        # Linea separatrice
        container.add_widget(
            MDBoxLayout(size_hint_y=None, height=dp(1), md_bg_color=(0.85, 0.85, 0.85, 1))
        )

        # ======================================================
        # BOX SEZIONI
        # ======================================================
        self.sections_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(30),
            size_hint_y=None,
        )
        self.sections_box.bind(minimum_height=self.sections_box.setter("height"))
        container.add_widget(self.sections_box)

        # Costruisco le sezioni
        self.box_4s = self._create_box("Quattro stagioni")
        self.box_est = self._create_box("Estive")
        self.box_inv = self._create_box("Invernali")

        # Default
        self.show_unico()

        # ======================================================
        # SALVA
        # ======================================================
        salva = MDRaisedButton(
            text="SALVA",
            md_bg_color=BLU_NOTTE,
            pos_hint={"center_x": 0.5},
            on_release=self.save
        )
        container.add_widget(salva)

        # ======================================================
        # OVERLAY ICON IN BASSO A DESTRA
        # ======================================================
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
    # CREO LE SEZIONI
    # ==========================================================
    def _create_box(self, titolo):

        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[0, 8, 0, 8],
            size_hint_y=None,
        )
        box.bind(minimum_height=box.setter("height"))

        # TITOLO SEZIONE
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

        # SCEGLI INTERVALLO
        box.add_widget(MDLabel(
            text="Scegli il tuo intervallo:",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(26)
        ))

        # KM
        box.add_widget(MDLabel(
            text="KM",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(22)
        ))

        km_row = MDBoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(40)
        )

        km35 = MDCheckbox(group=f"km_{titolo}")
        km45 = MDCheckbox(group=f"km_{titolo}")
        km50 = MDCheckbox(group=f"km_{titolo}")

        km_row.add_widget(self._row(km35, "35.000"))
        km_row.add_widget(self._row(km45, "45.000"))
        km_row.add_widget(self._row(km50, "50.000"))

        box.add_widget(km_row)

        # DATA / KM MONTAGGIO
        data = MDTextField(hint_text=f"Data montaggio {titolo}", readonly=True)
        data.bind(on_focus=lambda inst, foc, d=data: foc and self.open_calendar(d))

        km = MDTextField(hint_text=f"Km montaggio {titolo}", input_filter="int")

        box.data = data
        box.km = km
        box.km_opts = [km35, km45, km50]

        box.add_widget(data)
        box.add_widget(km)

        return box

    # ==========================================================
    # ROW CHECKBOX + NUMERO PERFETTO
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
            shorten=False,
            halign="left",
            size_hint_x=None,
            width=dp(56)     # <-- LA TUA MISURA PERFETTA
        )
        r.add_widget(label)

        return r

    # ==========================================================
    # SET UNICO / DOPPIO SET
    # ==========================================================
    def on_set_change(self, inst, val):
        if inst is self.rb_unico and val:
            self.show_unico()
        elif inst is self.rb_doppio and val:
            self.show_doppio()

    def show_unico(self):
        self.sections_box.clear_widgets()
        self.sections_box.add_widget(self.box_4s)

    def show_doppio(self):
        self.sections_box.clear_widgets()
        self.sections_box.add_widget(self.box_est)
        self.sections_box.add_widget(self.box_inv)

    # ==========================================================
    # DATE PICKER
    # ==========================================================
    def open_calendar(self, field):
        self._field = field
        picker = MDDatePicker()
        picker.bind(on_save=self.set_date)
        picker.open()

    def set_date(self, inst, value, date_range):
        self._field.text = value.strftime("%d/%m/%Y")

    # ==========================================================
    def save(self, *args):
        print("TODO: salvataggio gomme")

    # ==========================================================
    def go_back(self):
        self.manager.current = "detail_auto"
