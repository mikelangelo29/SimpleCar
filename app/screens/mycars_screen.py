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
from app.storage.license import max_cars
from kivy.uix.widget import Widget as MDWidget

from app.storage.data_store import load_data, save_data, ensure_live_file


BLU_NOTTE = get_color_from_hex("0D1B2A")
AZZURRO = get_color_from_hex("3A6EA5")  # blu più chiaro per Aggiorna KM


class MyCarsScreen(MDScreen):
    dialog_delete = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.data_path = "app/data/autos.json"  # DEPRECATO: il seed non si riscrive, usa data_store (file vivo)

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
            on_release=lambda x: self.try_open_add_auto()
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

        ensure_live_file()
        data = load_data()

        # ✅ INTERI: difese su struttura dati (Android può restituire roba sporca)
        if not isinstance(data, dict):
            data = {"autos": []}

        autos = data.get("autos", [])

        if not isinstance(autos, list):
            autos = []

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

            # ✅ INTERI: km sempre convertito a int (Android spesso salva stringhe)
            raw_km = auto.get("km", 0)
            try:
                km = int(raw_km)
            except (TypeError, ValueError):
                km = 0

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
                text=titolo.upper(),
                font_style="H5",
                halign="left",
                valign="middle",
                theme_text_color="Custom",
                text_color=BLU_NOTTE,
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
                height=dp(150),
            )

            update_btn = MDRaisedButton(
                text="Aggiorna KM",
                md_bg_color=AZZURRO,
                text_color=(1, 1, 1, 1),
                elevation=0,
                size_hint=(1, None),
                height=dp(45),
                # ✅ INTERI: niente KeyError + passa valore robusto
                on_release=lambda x, auto=auto: self.open_update_km_dialog(auto.get("km", 0)),
            )

            buttons.add_widget(update_btn)

            second_row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(45),
            )

            edit_btn = MDRaisedButton(
                text="Modifica Auto",
                md_bg_color=BLU_NOTTE,
                text_color=(1, 1, 1, 1),
                elevation=0,
                size_hint=(1, None),
                on_release=lambda x, a=auto, i=i: self.open_edit_popup(a, i)
            )

            delete_btn = MDRaisedButton(
                text="Elimina Auto",
                md_bg_color=(0.80, 0.18, 0.23, 1),
                text_color=(1, 1, 1, 1),
                elevation=0,
                ripple_color=(0.8, 0, 0.1, 1),
                size_hint=(1, None),
                on_release=lambda x, a=auto: self.confirm_delete_specific(a)
            )

            second_row.add_widget(edit_btn)
            second_row.add_widget(delete_btn)

            buttons.add_widget(second_row)

            card.add_widget(buttons)

            self.list_box.add_widget(card)
            self.list_box.add_widget(MDWidget(size_hint_y=None, height=dp(18)))

    def try_open_add_auto(self):
        ensure_live_file()
        data = load_data()
        autos = data.get("autos", [])

        limit = max_cars()
        if len(autos) >= limit:

            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                padding=(dp(12), dp(8)),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))

            content.add_widget(
                MDLabel(
                    text=(
                        "Nella versione gratuita puoi gestire 1 sola auto.\n"
                        "Con PRO puoi gestire fino a 10 auto.\n\n"
                        "Se hai già acquistato PRO, ripristina l’acquisto."
                    ),
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(90),
                )
            )

            # --- dopo la MDLabel del testo ---
            content.add_widget(MDWidget(size_hint_y=None, height=dp(8)))  # ✅ scarto tra testo e bottoni

            content.add_widget(
                MDRaisedButton(
                    text="SBLOCCA PRO",
                    md_bg_color=(1.0, 0.55, 0.0, 1),  # arancione
                    text_color=(1, 1, 1, 1),
                    size_hint=(1, None),
                    height=dp(44),
                    on_release=lambda x: self.unlock_pro_dev(),
                )
            )

            content.add_widget(
                MDRaisedButton(
                    text="RIPRISTINA ACQUISTO",
                    md_bg_color=(0.55, 0.25, 0.70, 1),  # purple
                    text_color=(1, 1, 1, 1),
                    size_hint=(1, None),
                    height=dp(44),
                    on_release=lambda x: self.restore_purchase_dev(),
                )
            )

            content.add_widget(
                MDFlatButton(
                    text="ANNULLA",
                    theme_text_color="Custom",
                    text_color=AZZURRO,               # se AZZURRO è già definito nel progetto
                    size_hint=(1, None),
                    height=dp(44),
                    on_release=lambda x: self.dialog_limit.dismiss(),
                )
            )

            self.dialog_limit = MDDialog(
                title="Sblocca EasyCar PRO",
                type="custom",
                content_cls=content,
            )
            self.dialog_limit.open()
            return


        self.manager.current = "add_auto"

    def unlock_pro_dev(self):
        from app.storage.license import set_pro

        set_pro(True)  # scrive su license.json
        self.dialog_limit.dismiss()
        self.manager.current = "add_auto"


    def restore_purchase_dev(self):
        from app.storage.license import set_pro

        set_pro(True)  # DEV: simula ripristino
        self.dialog_limit.dismiss()
        self.manager.current = "add_auto"




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
        ensure_live_file()
        data = load_data()
        autos = data.get("autos", [])

        if auto in autos:
            autos.remove(auto)

        save_data({"autos": autos})

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
        ensure_live_file()
        new_km = self.km_field.text.strip()

        if not new_km.isdigit():
            self.km_field.error = True
            return

        new_km = int(new_km)

        data = load_data()

        # aggiorna solo il primo (poi lo correggiamo per auto specifica)
        if data.get("autos"):
            data["autos"][0]["km"] = new_km

        save_data(data)

        self.dialog_update.dismiss()
        self.load_autos()
    def open_edit_popup(self, auto, index):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField

        self.edit_index = index

        self.edit_marca = MDTextField(
            hint_text="Marca",
            text=auto.get("marca", ""),
            mode="rectangle"
        )

        self.edit_modello = MDTextField(
            hint_text="Modello",
            text=auto.get("modello", ""),
            mode="rectangle"
        )

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(self.edit_marca)
        content.add_widget(self.edit_modello)

        self.dialog_edit = MDDialog(
            title="Modifica Nome Auto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="ANNULLA", on_release=lambda x: self.dialog_edit.dismiss()),
                MDFlatButton(text="SALVA", text_color=BLU_NOTTE,
                            on_release=lambda x: self.save_edit_name()),
            ],
        )
        self.dialog_edit.open()

    def save_edit_name(self):
        ensure_live_file()
        new_marca = self.edit_marca.text.strip()
        new_modello = self.edit_modello.text.strip()

        data = load_data()

        data["autos"][self.edit_index]["marca"] = new_marca
        data["autos"][self.edit_index]["modello"] = new_modello

        save_data(data)

        self.dialog_edit.dismiss()
        self.load_autos()


