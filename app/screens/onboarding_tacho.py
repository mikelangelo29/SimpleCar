from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty

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
        self.manager.current = "autos"
