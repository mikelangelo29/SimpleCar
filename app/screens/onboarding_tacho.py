from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivymd.app import MDApp
import random


class OnboardingTachimetroScreen(MDScreen):

    dialog = None   # Pop-up riutilizzabile

    def get_km(self):
        """
        Restituisce i km inseriti dall'utente nel Tachimetro Master.
        """
        return self.ids.km_field.text.strip()

    # 🔥 AGGIUNTA 1 — FUNZIONE PER MOSTRARE IL POPUP DI ERRORE
    def mostra_errore(self, messaggio):
        if not self.dialog:
            self.dialog = MDDialog(
                text=messaggio,
                buttons=[],
                auto_dismiss=True
            )
        else:
            self.dialog.text = messaggio

        self.dialog.open()

    # 🔥 AGGIUNTA 2 — FUNZIONE DI VALIDAZIONE E AVANZAMENTO
    def completa_onboarding(self):
        km = self.get_km()

        if not km:
            self.mostra_errore("Inserisci il chilometraggio prima di entrare nell’app.")
            return

        # Navigazione temporanea verso MyCars
        self.manager.current = "mycars"

    def crea_auto_e_apri_mycars(self):
        app = MDApp.get_running_app()

        # 1️⃣ Recupero dati Screen 2
        marca, modello = self.manager.get_screen("onb_create_auto").get_data()

        # 2️⃣ Km da Screen 3
        km = self.get_km()
        if not km:
            self.mostra_errore("Inserisci il chilometraggio prima di entrare nell’app.")
            return

        # 3️⃣ Struttura auto
        nuova_auto = {
            "marca": marca,
            "modello": modello,
            "targa": "",
            "km": int(km),
            "anno": "",
            "scadenze": {},
            "tacho_color": random.choice(["blue", "red", "purple", "orange", "green", "yellow"])
        }

        # 4️⃣ Carico autos
        autos = app.load_autos() or []
        autos.append(nuova_auto)

        # 5️⃣ Salvo
        app.save_autos(autos)

        # 6️⃣ Entro in MyCars
        self.manager.current = "mycars"

