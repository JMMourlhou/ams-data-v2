from ._anvil_designer import Word_editorTemplate
from anvil import *

import anvil.js

# Force execCommand to use inline CSS
anvil.js.window.document.execCommand("styleWithCSS", False, True)


class Word_editor(Word_editorTemplate):
    def __init__(self, **properties):

        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # drop_down_color init
        list_colors = [("Colors",""),("Red", "#FA0000"),("Green","#60FA00"),("Blue","#00C0FA"),("Orange","#FAA300"),("Yellow","#F2FA00")]
        self.drop_down_color.items = [(r[0],r[1]) for r in list_colors]

        # --------------------------------------------------------
        # Color treatment:
        # Inject a JS function that removes any previous color span 
        # --------------------------------------------------------
        js_code = """
        window.cleanColorInSelection = function() {
        
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;
        
            const range = sel.getRangeAt(0);
        
            // Function that removes a colored span but keeps its children
            function unwrapColorSpan(span) {
                const parent = span.parentNode;
                while (span.firstChild) parent.insertBefore(span.firstChild, span);
                parent.removeChild(span);
            }
        
            // STEP 1 — Clean spans inside the selected content
            const treeWalker = document.createTreeWalker(
                range.commonAncestorContainer,
                NodeFilter.SHOW_ELEMENT,
                {
                    acceptNode: (node) => {
                        if (node.tagName === "SPAN" &&
                            node.style &&
                            node.style.color) {
        
                            // Check if this span intersects with selection
                            const nRange = document.createRange();
                            nRange.selectNodeContents(node);
        
                            if (
                                range.compareBoundaryPoints(Range.END_TO_START, nRange) < 0 &&
                                range.compareBoundaryPoints(Range.START_TO_END, nRange) > 0
                            ) {
                                return NodeFilter.FILTER_ACCEPT;
                            }
                        }
                        return NodeFilter.FILTER_REJECT;
                    }
                }
            );
        
            let node;
            const to_unwrap = [];
            while ((node = treeWalker.nextNode())) {
                to_unwrap.push(node);
            }
        
            to_unwrap.forEach(n => unwrapColorSpan(n));
        
            // STEP 2 — Clean parent spans that fully wrap the selection
            function cleanParentSpans(node) {
                while (node && node.nodeType === 1) {
                    if (node.tagName === "SPAN" && node.style && node.style.color) {
        
                        // Check if span fully contains the selection
                        const parentRange = document.createRange();
                        parentRange.selectNodeContents(node);
        
                        if (
                            parentRange.compareBoundaryPoints(Range.START_TO_START, range) <= 0 &&
                            parentRange.compareBoundaryPoints(Range.END_TO_END, range) >= 0
                        ) {
                            unwrapColorSpan(node);
                        }
                    }
                    node = node.parentNode;
                }
            }
        
            cleanParentSpans(range.startContainer);
            cleanParentSpans(range.endContainer);
        };


        """
        anvil.js.window.eval(js_code)     ### ADDED

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        editor = anvil.js.window.document.getElementById("editor")
        editor.innerHTML = f"<p>{self.text}</p>"  

    # ------------------------
    # BOLD / ITALIC / UNDERLINE
    # ------------------------
    def button_bold_click(self, **event_args):
        anvil.js.window.document.execCommand("bold")

    def button_italic_click(self, **event_args):
        anvil.js.window.document.execCommand("italic")

    def button_underlined_click(self, **event_args):
        anvil.js.window.document.execCommand("underline")

    # ------------------------
    # FONT SIZE
    # ------------------------
    def drop_down_font_size_change(self, **event_args):
        size_px = self.drop_down_font_size.selected_value
        if not size_px:
            return

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
        self._fix_font_size(size_px)
        self.drop_down_font_size.selected_value = self.drop_down_font_size.items[0]

    def _fix_font_size(self, size_px):
        js = anvil.js.window

        selection = js.getSelection()
        if selection.rangeCount == 0:
            return

        range = selection.getRangeAt(0)
        node = range.commonAncestorContainer

        while node and node.nodeType != 1:
            node = node.parentNode

        if node and hasattr(node, "style") and node.style and node.style.fontSize:
            node.style.fontSize = f"{size_px}px"

    # ------------------------
    # ERASE FORMATTING
    # ------------------------
    def button_erase_click(self, **event_args):
        sel = anvil.js.window.getSelection()
        if sel.rangeCount == 0:
            return

        selected_text = sel.toString()
        if selected_text == "":
            alert("Sélectionne du texte.")
            return

        html = selected_text
        anvil.js.window.document.execCommand("insertHTML", False, html)

    # ------------------------
    # COLOR TREATMENT
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
    
        # (1) Save range
        self._save_selection()
    
        # (2) Clean all colored spans in the selection (real DOM)
        js.cleanColorInSelection()
    
        # (3) Get fresh range after cleanup
        sel = js.getSelection()
        range = sel.getRangeAt(0)
    
        # (4) Extract selected text
        text = sel.toString()
    
        # (5) Replace selection entirely by a new clean span
        html = f"<span style='color:{color}'>{text}</span>"
        js.document.execCommand("insertHTML", False, html)
    
        # (6) Focus editor
        editor.focus()
    
        # (7) Restore selection
        self._restore_selection()
    
        # Reset dropdown
        self.drop_down_color.selected_value = self.drop_down_color.items[0][1]


    # ------------------------
    # ALIGNMENTS
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
    
        self._save_selection()
    
        js.document.execCommand(command, False, None)
    
        editor.focus()
        self._restore_selection()
    
    # Common selection save/restore
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
        editor = anvil.js.window.document.getElementById("editor")
        self.text = editor.innerHTML
        self.raise_event('x-fin_saisie')

    def timer_1_tick(self, **event_args):
        with anvil.server.no_loading_indicator:
            result = anvil.server.call("ping")

    def timer_2_tick(self, **event_args):
        editor = anvil.js.window.document.getElementById("editor")
        self.text = editor.innerHTML
        self.raise_event('x-timer_text_backup')


    

    

            

   
