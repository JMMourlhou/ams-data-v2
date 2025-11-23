from ._anvil_designer import Word_editorTemplate
from anvil import *

import anvil.js

# On force execCommand à utiliser des styles CSS inline
anvil.js.window.document.execCommand("styleWithCSS", False, True)


class Word_editor(Word_editorTemplate):
    def __init__(self, **properties):
 
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # drop_down_color init
        list_colors = [("Colors",""),("Red", "#FA0000"),("Green","#60FA00"),("Blue","#00C0FA"),("Orange","#FAA300"),("Yellow","#F2FA00")]
        self.drop_down_color.items = [(r[0],r[1]) for r in list_colors]
        

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        # text is the property declared for the form in the "Edit properties and events left menu"
        editor = anvil.js.window.document.getElementById("editor")
        editor.innerHTML = f"<p>{self.text}</p>"  
    
    # ------------------------
    # BOLD / ITALIC / UNDERLINE
    # ------------------------
    def button_bold_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.js.window.document.execCommand("bold")

    def button_italic_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.js.window.document.execCommand("italic")

    def button_underlined_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.js.window.document.execCommand("underline")

    # ------------------------
    # FONT SIZE
    # ------------------------
    def drop_down_font_size_change(self, **event_args):
        size_px = self.drop_down_font_size.selected_value
        if not size_px:
            return

        # 1. Applique la taille interne : valeurs 1 à 7 (temporaire)
        mapping = {
            "10": "1",
            "12": "2",
            "16": "3",
            "18": "4",
            "24": "5",
            "32": "6",
            "48": "7",
        }

        level = mapping.get(size_px, "3")

        anvil.js.window.document.execCommand("fontSize", False, level)

        # 2. Chrome ajoute un span avec font-size
        # On remplace le font-size par notre valeur exacte
        self._fix_font_size(size_px)

        # On ré-initialise la drop down
        self.drop_down_font_size.selected_value = self.drop_down_font_size.items[0]

    def _fix_font_size(self, size_px):
        js = anvil.js.window

        selection = js.getSelection()
        if selection.rangeCount == 0:
            return

        range = selection.getRangeAt(0)
        node = range.commonAncestorContainer

        # On remonte jusqu'à trouver un élément HTML
        while node and node.nodeType != 1:
            node = node.parentNode

        if node and hasattr(node, "style") and node.style and node.style.fontSize:
            node.style.fontSize = f"{size_px}px"

    # ------------------------
    # ERASE FORMATTING (texte "normal")
    # ------------------------
    def button_erase_click(self, **event_args):
        """This method is called when the button is clicked"""
        sel = anvil.js.window.getSelection()
        if sel.rangeCount == 0:
            return

        selected_text = sel.toString()
        if selected_text == "":
            alert("Sélectionne du texte.")
            return

        # Supprime tout le style : remplace par un texte propre
        html = selected_text  # sans balises

        anvil.js.window.document.execCommand("insertHTML", False, html)

    # ------------------------
    # Color Treatment
    # ------------------------
    def drop_down_color_change(self, **event_args):
        color = self.drop_down_color.selected_value
        if not color:
            return
    
        js = anvil.js.window
        editor = js.document.getElementById("editor")
    
        sel = js.getSelection()
        if sel.rangeCount == 0 or sel.toString() == "":
            alert("Sélectionne du texte d'abord.")
            return
    
        # 1) Sauvegarde la sélection
        self._save_selection()
    
        try:
            # 2) Applique la couleur via surroundContents
            range = sel.getRangeAt(0)
            span = js.document.createElement("span")
            span.style.color = color
            range.surroundContents(span)
        except:
            # fallback multi-nœuds
            fragment = range.cloneContents()
            temp = js.document.createElement("div")
            temp.appendChild(fragment)
            html = temp.innerHTML
            js.document.execCommand("insertHTML", False, f"<span style='color:{color}'>{html}</span>")
    
        # 3) Re-focus pour réveiller Anvil
        editor.focus()
    
        # 4) Restore la sélection (Chrome + Anvil re-render immédiatement)
        self._restore_selection()
    
        # 5) Petit trick : toucher l'attribut style pour forcer refresh
        editor.style.borderColor = editor.style.borderColor

        # drop down init, 1st row, 2d color
        self.drop_down_color.selected_value = self.drop_down_color.items[0][1]

    


    # ------------------------
    # ALIGNEMENTS
    # ------------------------
    def button_align_left_click(self, **event_args):
        self._apply_alignment("justifyLeft")
    
    def button_align_center_click(self, **event_args):
        self._apply_alignment("justifyCenter")
    
    def button_align_right_click(self, **event_args):
        self._apply_alignment("justifyRight")
    
    def button_align_justify_click(self, **event_args):
        self._apply_alignment("justifyFull")

    
    def _apply_alignment(self, command):
        js = anvil.js.window
        editor = js.document.getElementById("editor")
    
        sel = js.getSelection()
        if sel.rangeCount == 0:
            alert("Sélectionne un paragraphe ou place le curseur dedans.")
            return
    
        # Sauvegarder la sélection pour la restaurer après
        self._save_selection()
    
        # Appliquer l'alignement
        js.document.execCommand(command, False, None)
    
        # Refocus pour réveiller Anvil
        editor.focus()
    
        # Restaurer la sélection
        self._restore_selection()
    
        
    # Comon treatment for Color & Align treatments
    def _save_selection(self):
        js = anvil.js.window
        sel = js.getSelection()
        if sel.rangeCount > 0:
            self._saved_range = sel.getRangeAt(0).cloneRange()

    def _restore_selection(self):
        js = anvil.js.window
        if not hasattr(self, "_saved_range"):
            return

        sel = js.getSelection()
        sel.removeAllRanges()
        sel.addRange(self._saved_range)

    def button_validation_click(self, **event_args):
        """This method is called when the button is clicked"""
        # 1. Récupérer le HTML du contenteditable
        editor = anvil.js.window.document.getElementById("editor")
        self.text = editor.innerHTML  # texte is the  property of the form 
        self.raise_event('x-fin_saisie')

    def timer_1_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        # Pour empêcher le msg session expired (suffit pour ordinateur, pas pour tel)
        with anvil.server.no_loading_indicator:
            result = anvil.server.call("ping")
        print(f"Word Editor: ping on server to prevent 'session expired' every 5 min, server answer:{result}")

    def timer_2_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        # 1. Récupérer le HTML du contenteditable
        editor = anvil.js.window.document.getElementById("editor")
        self.text = editor.innerHTML  # texte is the  property of the form 
        print(f"Word Editor: sending the HTML text content: {self.text}")
        self.raise_event('x-timer_text_backup')

    

    

            

   
