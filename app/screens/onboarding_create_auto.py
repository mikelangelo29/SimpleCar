from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog

class OnboardingCreateAutoScreen(MDScreen):

    dialog = None

    def get_data(self):
        """
        Funzione comodissima che useremo in fase di integrazione:
        restituisce marca e modello inseriti dall'utente.
        """
        marca = self.ids.marca_field.text.strip()
        modello = self.ids.modello_field.text.strip()
        return marca, modello
    
     # 🔥 AGGIUNTA 1 — POPUP DI ERRORE
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

    # 🔥 AGGIUNTA 2 — FUNZIONE DI VALIDAZIONE E NAVIGAZIONE
    def vai_avanti(self):
        marca, modello = self.get_data()

        if not marca or not modello:
            self.mostra_errore("Inserisci marca e modello prima di proseguire.")
            return

        # Se tutto è ok → vai allo screen successivo
        self.manager.current = "onb_tacho"
