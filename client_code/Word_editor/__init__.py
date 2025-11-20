from ._anvil_designer import Word_editorTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

anvil.js.window.document.execCommand("styleWithCSS", False, True)

class Word_editor(Word_editorTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_bold_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.js.window.document.execCommand("bold")

    def button_italic_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.js.window.document.execCommand("italic")

    def button_underlined_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.js.window.document.execCommand("underline")


    
    def drop_down_font_size_change(self, **event_args):
        size_px = self.drop_down_font_size.selected_value
        if not size_px:
            return
    
        # 1. Applique la taille interne : valeurs 1 à 7 (temporaire)
        # On mappe nos tailles px vers ces niveaux
        mapping = {
            "10": "1",
            "12": "2",
            "16": "3",
            "18": "4",
            "24": "5",
            "32": "6",
            "48": "7"
        }
    
        level = mapping.get(size_px, "3")
    
        anvil.js.window.document.execCommand("fontSize", False, level)
    
        # 2. Chrome ajoute un span avec style font-size: xxpx
        # On remplace le font-size par notre valeur exacte
        self._fix_font_size(size_px)

    def _fix_font_size(self, size_px):
        js = anvil.js.window

        selection = js.getSelection()
        if selection.rangeCount == 0:
            return

        range = selection.getRangeAt(0)
        node = range.commonAncestorContainer

        # On remonte jusqu'à trouver un span avec font-size
        while node and node.nodeType != 1:
            node = node.parentNode

        if node and node.style and node.style.fontSize:
            node.style.fontSize = f"{size_px}px"

    
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


    
    # --------------------------------------------------------------
    # 1) Changement de couleur depuis le DropDown
    # --------------------------------------------------------------
    def drop_down_color_change(self, **event_args):
        color = self.drop_down_color.selected_value
        if not color:
            return
    
        js = anvil.js.window
        sel = js.getSelection()
    
        # Vérifie qu'il y a du texte sélectionné
        if sel.rangeCount == 0 or sel.toString() == "":
            alert("Sélectionne du texte d'abord.")
            return
    
        # Applique la couleur interne (chrome crée <font> ou <span>)
        js.document.execCommand("foreColor", False, color)
    
        # Transforme ce que Chrome a créé en <span style="color:xxx">
        self._fix_color(color)
    
        # Force Chrome/Anvil à re-render immédiatement (clé !)
        self._force_render()
    
    
    # --------------------------------------------------------------
    # 2) Corrige les nœuds créés par execCommand("foreColor")
    #    pour garantir un <span style="color:xxx">
    # --------------------------------------------------------------
    def _fix_color(self, color):
        js = anvil.js.window
        selection = js.getSelection()
        if selection.rangeCount == 0:
            return
    
        range = selection.getRangeAt(0)
        node = range.commonAncestorContainer
    
        # remonte jusqu’à trouver un élément HTML
        while node and node.nodeType != 1:
            node = node.parentNode
    
        if not node:
            return
    
        # 1. Cas où Chrome a créé un <font color="red">
        if node.tagName and node.tagName.lower() == "font":
            new_span = js.document.createElement("span")
            new_span.style.color = color
            new_span.innerHTML = node.innerHTML
            node.parentNode.replaceChild(new_span, node)
            return
    
        # 2. Cas normal : Chrome a créé un <span>
        if hasattr(node, "style"):
            node.style.color = color
    
    
    # --------------------------------------------------------------
    # 3) Force un re-rendu visuel immédiat du DOM
    #    (sinon Chrome n'affiche parfois la couleur qu'après un clic)
    # --------------------------------------------------------------
    def _force_render(self):
        js = anvil.js.window
        sel = js.getSelection()
        if sel.rangeCount == 0:
            return
    
        # reprends la sélection → force Chrome à re-rendre
        range = sel.getRangeAt(0)
        sel.removeAllRanges()
        sel.addRange(range)