from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.widget import MDWidget
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

import json
import os

BLU_NOTTE = get_color_from_hex("0D1B2A")
AZZURRO_ICONA = (0.18, 0.45, 1, 1)


class MyCarsScreen(MDScreen):
    dialog_delete = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data_path = "app/data/autos.json"

        # ---------- TOP BAR ----------
        top_bar = MDTopAppBar(
            title="",
            elevation=0,
            md_bg_color=BLU_NOTTE,
            left_action_items=[
                ["home", lambda x: setattr(self.manager, "current", "home")]
            ],
        )
        self.add_widget(top_bar)

        # ---------- ROOT ----------
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

        # ---------- Bottone Aggiungi Auto ----------
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

        # ---------- Lista ----------
        self.list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            size_hint_y=None,
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll_box.add_widget(self.list_box)

        self.root_layout.add_widget(scroll)
        self.add_widget(self.root_layout)

        # ---------- FOOTER / NAVBAR ----------
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

        def go_home(*args):
            self.manager.current = "home"

        home_icon.bind(
            on_touch_down=lambda i, t: go_home() if home_icon.collide_point(t.x, t.y) else False
        )

        footer.add_widget(home_icon)
        self.add_widget(footer)

    # ---------- LOAD AUTOS ----------
    def on_pre_enter(self, *args):
        self.load_autos()

    def load_autos(self):
        self.list_box.clear_widgets()

        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump({"autos": []}, f, indent=4)

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        autos = data.get("autos", [])
        self.btn_add.disabled = len(autos) >= 1

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

        # ---------- AUTO PRESENTE ----------
        auto = autos[0]

        marca = auto.get("marca", "")
        modello = auto.get("modello", "")
        km = auto.get("km", 0)
        titolo = " ".join([x for x in [marca, modello] if x.strip()])

        # ---------- CARD AUTO ----------
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            radius=[20, 20, 20, 20],
            elevation=0,
            size_hint=(1, None),
            height=dp(310),
            style="outlined",
            line_color=(0.8, 0.8, 0.8, 1),
            line_width=1.2,
        )

        # ---------- HEADER CLICCABILE ----------
        header_box = MDBoxLayout(
            orientation="horizontal",
            padding=(5, 5),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
        )

        title_label = MDLabel(
            text=str(titolo),
            font_style="H5",
            halign="left",
            valign="center",
        )

        details_icon = MDIcon(
            icon="chevron-right",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),  # grigio elegante
            font_size=dp(32),
        )


        header_box.add_widget(title_label)
        header_box.add_widget(details_icon)

        def open_details(*args):
            self.manager.current = "detail_auto"

        header_box.bind(
            on_touch_down=lambda w, t: open_details()
            if header_box.collide_point(t.x, t.y)
            else False
        )

        card.add_widget(header_box)

        # separatore
        card.add_widget(MDWidget(size_hint_y=None, height=dp(2)))
        card.add_widget(MDBoxLayout(md_bg_color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(1)))

        # ---------- Icona + KM ----------
        row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            size_hint_y=None,
            height=dp(45)
        )

        row.add_widget(
            MDIcon(
                icon="car",
                font_size=dp(40),
                theme_text_color="Custom",
                text_color=AZZURRO_ICONA
            )
        )

        row.add_widget(
            MDLabel(
                text=f"Chilometraggio: {km} km",
                theme_text_color="Secondary"
            )
        )

        card.add_widget(row)

        # ---------- PULSANTI ----------
        buttons = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(110)
        )

        update_btn = MDRaisedButton(
            text="Aggiorna KM",
            md_bg_color=BLU_NOTTE,
            text_color=(1, 1, 1, 1),
            elevation=0,
            size_hint=(1, None),
            height=dp(45),
            on_release=lambda x: self.open_update_km_dialog(km)
        )

        delete_btn = MDRaisedButton(
            text="Elimina Auto",
            md_bg_color=(0.9, 0.1, 0.1, 1),
            text_color=(1, 1, 1, 1),
            elevation=0,
            size_hint=(1, None),
            height=dp(45),
            on_release=lambda x: self.confirm_delete()
        )

        buttons.add_widget(update_btn)
        buttons.add_widget(delete_btn)

        card.add_widget(MDWidget(size_hint_y=None, height=dp(10)))
        card.add_widget(buttons)

        self.list_box.add_widget(card)

    # ---------- DIALOG DELETE AUTO ----------
    def confirm_delete(self):
        if not self.dialog_delete:
            self.dialog_delete = MDDialog(
                title="Eliminare l'auto?",
                text="Sicuro di voler eliminare l'auto?",
                buttons=[
                    MDFlatButton(text="ANNULLA", on_release=lambda x: self.dialog_delete.dismiss()),
                    MDFlatButton(text="ELIMINA", text_color=(1, 0, 0, 1),
                                 on_release=lambda x: self.delete_auto())
                ],
            )
        self.dialog_delete.open()

    def delete_auto(self):
        self.dialog_delete.dismiss()
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump({"autos": []}, f, indent=4)
        self.load_autos()

    # ---------- AGGIORNA KM ----------
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

        if data["autos"]:
            data["autos"][0]["km"] = new_km

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.dialog_update.dismiss()
        self.load_autos()
