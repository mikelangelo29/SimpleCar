from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.widget import MDWidget
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import json
import os


BLU_NOTTE = get_color_from_hex("0D1B2A")
AZZURRO = get_color_from_hex("3A6EA5")  # blu più chiaro per Aggiorna KM


class MyCarsScreen(MDScreen):
    dialog_delete = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data_path = "app/data/autos.json"

        # ---------- TOP BAR ----------
        top_bar = MDTopAppBar(
            title="Le mie Auto",
            elevation=0,
            md_bg_color=BLU_NOTTE,
            left_action_items=[
                ["home", lambda x: setattr(self.manager, "current", "home")]
            ],
        )
        self.add_widget(top_bar)

        # ---------- ROOT LAYOUT ----------
        self.root_layout = MDBoxLayout(orientation="vertical")

        scroll = MDScrollView()
        scroll_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=(dp(20), dp(20), dp(20), dp(20)),
            size_hint_y=None,
        )
        scroll_box.bind(minimum_height=scroll_box.setter("height"))
        scroll.add_widget(scroll_box)
        self.scroll_box = scroll_box

        # ---------- BOTTONE AGGIUNGI AUTO ----------
        self.btn_add = MDRaisedButton(
            text="Aggiungi Auto",
            md_bg_color=BLU_NOTTE,
            text_color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(50),
            elevation=0,
            on_release=lambda x: setattr(self.manager, "current", "add_auto")
        )
        self.scroll_box.add_widget(self.btn_add)

        # ---------- LISTA AUTO ----------
        self.list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            size_hint_y=None,
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll_box.add_widget(self.list_box)

        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

        # ---------- FOOTER ----------
        footer = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            md_bg_color=BLU_NOTTE,
            padding=(dp(10), dp(10)),
            pos_hint={"y": 0}
        )

        home_icon = MDIcon(
            icon="home",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_size=dp(38)
        )

        home_icon.bind(
            on_touch_down=lambda i, t: setattr(self.manager, "current", "home")
            if home_icon.collide_point(t.x, t.y)
            else False
        )

        footer.add_widget(home_icon)
        self.add_widget(footer)

    # ---------- ON ENTER ----------
    def on_pre_enter(self, *args):
        self.load_autos()

    # ---------- LOAD AUTOS ----------
    def load_autos(self):
        self.list_box.clear_widgets()

        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump({"autos": []}, f, indent=4)

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])
        self.btn_add.disabled = False   # PRO mode

        # ---------- NESSUNA AUTO ----------
        if len(autos) == 0:
            empty_card = MDCard(
                orientation="vertical",
                padding=dp(15),
                radius=[20, 20, 20, 20],
                elevation=0,
                size_hint=(1, None),
                height=dp(120),
            )

            empty_card.add_widget(
                MDLabel(
                    text="Nessuna auto registrata.",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="H6"
                )
            )

            empty_card.add_widget(
                MDLabel(
                    text="Premi 'Aggiungi Auto' per inserirne una.",
                    halign="center",
                    theme_text_color="Secondary"
                )
            )

            self.list_box.add_widget(empty_card)
            return

        # ---------- AUTO PRESENTI ----------
        for i, auto in enumerate(autos):

            marca = auto.get("marca", "")
            modello = auto.get("modello", "")
            km = auto.get("km", 0)
            titolo = " ".join([x for x in [marca, modello] if x.strip()])

            color = auto.get("tacho_color", "purple")  # prima auto purple
            tacho_source = f"app/assets/icons/tacho_{color}.png"

            # ---------- CARD ----------
            card = MDCard(
                orientation="vertical",
                padding=dp(15),
                radius=[20, 20, 20, 20],
                elevation=0,
                shadow_softness=0,
                shadow_offset=(0, 0),
                size_hint=(1, None),
                height=dp(360),
                style="outlined",
                line_color=BLU_NOTTE,
                line_width=0.8,
            )

            # ---------- HEADER ----------
            header_box = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                padding=(0, dp(1), 0, dp(4)),
                size_hint_y=None,
                height=dp(55),
            )

            title_label = MDLabel(
                text=titolo,
                font_style="H5",
                halign="left",
                valign="middle",
            )

            details_icon = MDIcon(
                icon="chevron-right",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
                font_size=dp(30),
            )

            header_box.add_widget(title_label)
            header_box.add_widget(details_icon)

            def make_callback(index):
                return lambda w, t: self.open_detail(index) if w.collide_point(t.x, t.y) else False

            header_box.bind(on_touch_down=make_callback(i))


            card.add_widget(header_box)

            # ---------- SEPARATORE ----------
            card.add_widget(
                MDBoxLayout(
                    md_bg_color=BLU_NOTTE,
                    size_hint_y=None,
                    height=dp(2)
                )
            )
            card.add_widget(MDWidget(size_hint_y=None, height=dp(6)))

            # ---------- TACHIMETRO + KM ----------
            tacho_row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(20),
                size_hint_y=None,
                height=dp(120),
                padding=(0, dp(10)),
            )

            tacho_image = Image(
                source=tacho_source,
                size_hint=(None, None),
                size=(dp(110), dp(110)),
            )

            km_box = MDCard(
                radius=[14, 14, 14, 14],
                elevation=2,
                padding=(dp(18), dp(10)),
                size_hint=(None, None),
                size=(dp(140), dp(55)),
                md_bg_color=(0.95, 0.95, 0.95, 1),
            )

            km_label = MDLabel(
                text=f"{km:,} km".replace(",", "."),
                font_style="H6",
                halign="center",
                valign="middle",
                theme_text_color="Primary",
            )

            km_box.add_widget(km_label)
            tacho_row.add_widget(tacho_image)
            tacho_row.add_widget(km_box)
            card.add_widget(tacho_row)

            card.add_widget(MDWidget(size_hint_y=None, height=dp(12)))

            # ---------- BOTTONI ----------
            buttons = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(120),
            )

            update_btn = MDRaisedButton(
                text="Aggiorna KM",
                md_bg_color=AZZURRO,
                text_color=(1, 1, 1, 1),
                elevation=0,
                size_hint=(1, None),
                height=dp(45),
                on_release=lambda x, auto=auto: self.open_update_km_dialog(auto["km"]),
            )

            delete_btn = MDRaisedButton(
                text="Elimina Auto",
                md_bg_color=(1, 0.23, 0.25, 1),    # Rosso Instagram
                text_color=(1, 1, 1, 1),           # Testo bianco
                elevation=0,                       # Nessun rilievo stile Instagram
                ripple_color=(0.8, 0, 0.1, 1),     # Ripple rosso scuro pieno
                size_hint=(1, None),
                height=dp(45),
                on_release=lambda x, a=auto: self.confirm_delete_specific(a)
            )


            buttons.add_widget(update_btn)
            buttons.add_widget(delete_btn)
            card.add_widget(buttons)

            # ---------- ADD CARD ----------
            self.list_box.add_widget(card)

            # ---------- SPACER PER LO SCROLL ----------
            self.list_box.add_widget(MDWidget(size_hint_y=None, height=dp(18)))

    # ---------- OPEN DETAIL ----------
    def open_detail(self, index):
        detail = self.manager.get_screen("detail_auto")
        detail.selected_index = index
        self.manager.current = "detail_auto"

    # ---------- DELETE AUTO ----------
    def confirm_delete_specific(self, auto):
        self.auto_to_delete = auto

        self.dialog_delete = MDDialog(
            title="Eliminare l'auto?",
            text="Sicuro di voler eliminare questa auto?",
            buttons=[
                MDFlatButton(text="ANNULLA", on_release=lambda x: self.dialog_delete.dismiss()),
                MDFlatButton(
                    text="ELIMINA",
                    text_color=(1, 0, 0, 1),
                    on_release=lambda x: self.delete_auto(auto),
                ),
            ],
        )
        self.dialog_delete.open()

    def delete_auto(self, auto):
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])
        autos.remove(auto)

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump({"autos": autos}, f, indent=4)

        self.dialog_delete.dismiss()
        self.load_autos()

    # ---------- UPDATE KM ----------
    def open_update_km_dialog(self, current_km):
        from kivymd.uix.textfield import MDTextField

        self.km_field = MDTextField(
            hint_text="Nuovo chilometraggio",
            text=str(current_km),
            input_filter="int",
            mode="rectangle"
        )

        self.dialog_update = MDDialog(
            title="Aggiorna chilometraggio",
            type="custom",
            content_cls=self.km_field,
            buttons=[
                MDFlatButton(text="ANNULLA", on_release=lambda x: self.dialog_update.dismiss()),
                MDFlatButton(text="SALVA", text_color=BLU_NOTTE,
                             on_release=lambda x: self.save_new_km())
            ],
        )

        self.dialog_update.open()

    def save_new_km(self):
        new_km = self.km_field.text.strip()

        if not new_km.isdigit():
            self.km_field.error = True
            return

        new_km = int(new_km)

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # aggiorna solo il primo (poi lo correggiamo per auto specifica)
        if data["autos"]:
            data["autos"][0]["km"] = new_km

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.dialog_update.dismiss()
        self.load_autos()
