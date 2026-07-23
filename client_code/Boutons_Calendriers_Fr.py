from anvil.js.window import document


def traduire_boutons_calendrier():
    """
    Quand je dois saisir l'heure, le picktime est coché
       les boutons ok, retour sont en englais
    Ce module traduit les boutons des DatePicker Anvil qui existent
    actuellement dans la page.
    Si on place ce script ds Main, ne fonctionne pas 
       car le calendrier nest pas encore créé

    SOLUTION: Appeler ce module après la création de chaque formulaire contenant un DatePicker.
    !!!!  les boutons js  .applyBtn et .cancelBtn ne sont pas présents dans le DOM juste après le init_components().
          Il faut donc lancer la traduction des boutons du calendrier lorsque le DatePicker est effectivement affiché:
          date_picker_1_show:
          
                # POur afficher OK et Retour en FRancais (calendrier)
                # Cette méthode se lance qd le date_picker component s'affiche
                def date_picker_1_show(self, **event_args):
                    from .. import Boutons_Calendriers_Fr
                    Boutons_Calendriers_Fr.traduire_boutons_calendrier()
                """

    for btn in document.querySelectorAll(
        ".daterangepicker .applyBtn"
    ):
        btn.textContent = "OK"

    for btn in document.querySelectorAll(
        ".daterangepicker .cancelBtn"
    ):
        btn.textContent = "Retour"
