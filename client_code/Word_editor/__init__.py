from ._anvil_designer import Word_editorTemplate
from anvil import *

import anvil.js

# Pour le download du texte
from datetime import datetime


# Force execCommand to use inline CSS
anvil.js.window.document.execCommand("styleWithCSS", False, True)


class Word_editor(Word_editorTemplate):
    def __init__(self, top_ligne_1, top_ligne_2 , **properties):

        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        """   
        # drop_down_color init
        list_colors = [("Colors",""),("Red", "#FA0000"),("Green","#60FA00"),("Blue","#00C0FA"),("Orange","#FAA300"),("Yellow","#F2FA00")]
        self.drop_down_color.items = [(r[0],r[1]) for r in list_colors]
        """
        self.top_ligne_1 = top_ligne_1 # Titre, BT download 
        self.top_ligne_2 = top_ligne_2
        # --------------------------------------------------------
        # global HTML cleaner to keep saved HTML clean
        # --------------------------------------------------------
        js_code_clean = """
        window.cleanEditorHTML = function(root) {
            if (!root) return;

            // Helper: unwrap a node but keep its children
            function unwrap(node) {
                const parent = node.parentNode;
                if (!parent) return;
                while (node.firstChild) parent.insertBefore(node.firstChild, node);
                parent.removeChild(node);
            }

            // 1) Unwrap spans with no attributes (completely useless wrappers)
            const spans_no_attr = root.querySelectorAll("span");
            spans_no_attr.forEach(function(span) {
                if (!span.attributes || span.attributes.length === 0) {
                    unwrap(span);
                }
            });

            // 2) Merge nested spans that share the exact same style
            const spans_same_style = root.querySelectorAll("span");
            spans_same_style.forEach(function(span) {
                const parent = span.parentNode;
                if (!parent || parent.tagName !== "SPAN") return;

                const styleChild = span.getAttribute("style");
                const styleParent = parent.getAttribute("style");
                if (!styleChild || !styleParent) return;

                const normChild = styleChild.replace(/\\s+/g, '').toLowerCase();
                const normParent = styleParent.replace(/\\s+/g, '').toLowerCase();

                if (normChild === normParent) {
                    unwrap(span);
                }
            });

            // 3) Remove empty spans (no visible text, no element children)
            const spans_empty = root.querySelectorAll("span");
            spans_empty.forEach(function(span) {
                const text = span.textContent || "";
                const hasElementChild = !!span.querySelector("*");
                if (!hasElementChild && text.trim() === "") {
                    unwrap(span);
                }
            });
    
            // 4) Remove extra empty <p> but keep at most ONE in a row
            let paragraphs = root.querySelectorAll("p");
            let previousWasEmpty = false;
            
            paragraphs.forEach(function(p) {
                const text = p.textContent || "";
                const hasChild = p.querySelector("*") !== null;
            
                const isEmpty = (!hasChild && text.replace(/\u00A0/g, '').trim() === "");
            
                if (isEmpty) {
                    if (previousWasEmpty) {
                        // Remove the extra empty <p>
                        p.parentNode.removeChild(p);
                    } else {
                        previousWasEmpty = true;
                    }
                } else {
                    previousWasEmpty = false;
                }
            });
            
        };
        """
        anvil.js.window.eval(js_code_clean)
        
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

    # -------------------------------------------------------------------------------------------------------------------
    # COLOR TREATMENT
    # -------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------------
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
    anvil.js.window.eval(js_code)     
    
    def button_red_click(self, **event_args):
        color = "#FA0000"
        self.color_change(color)
        
    def button_green_click(self, **event_args):
        color = "#60FA00"
        self.color_change(color)   

    def button_blue_click(self, **event_args):
        color = "#00C0FA"
        self.color_change(color)  

    def button_orange_click(self, **event_args):
        color = "#FAA300"
        self.color_change(color)   

    def button_yellow_click(self, **event_args):
        color = "#F2FA00"
        self.color_change(color)  
        
    def color_change(self, color, **event_args):
        #color = from the corresponding color button 
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
        
        # (4b) Detect existing <span> if any and keep its styles
        container = range.commonAncestorContainer
        saved_style = ""
        
        if container.nodeType == 1 and container.tagName == "SPAN":
            saved_style = container.getAttribute("style") or ""
        else:
            parent = container.parentNode
            if parent and parent.tagName == "SPAN":
                saved_style = parent.getAttribute("style") or ""
        
        # Remove existing color rules from style
        import re
        saved_style = re.sub(r"color\s*:\s*[^;]+;?", "", saved_style).strip()
        
        # Rebuild clean style
        final_style = f"color:{color};"
        if saved_style:
            final_style = saved_style + ";" + final_style
        
        # (5) Replace selection with clean span preserving other styles
        html = f"<span style='{final_style}'>{text}</span>"
        js.document.execCommand("insertHTML", False, html)
    
        # (6) Focus editor
        editor.focus()
    
        # (7) Restore selection
        self._restore_selection()
    
        # Reset dropdown
        # self.drop_down_color.selected_value = self.drop_down_color.items[0][1]


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

        # Clean HTML before saving, to avoid dirty nested spans / useless wrappers
        anvil.js.window.cleanEditorHTML(editor)   
        
        self.text = editor.innerHTML
        self.raise_event('x-fin_saisie')

    def timer_1_tick(self, **event_args):
        with anvil.server.no_loading_indicator:
            result = anvil.server.call("ping")

    def timer_2_tick(self, **event_args):
        editor = anvil.js.window.document.getElementById("editor")

        # Clean HTML before autosave backup
        anvil.js.window.cleanEditorHTML(editor)
        
        self.text = editor.innerHTML
        self.raise_event('x-timer_text_backup')

    def button_download_click(self, **event_args):
        """Export current editor content as a PDF using the Uplink 'render_pdf'"""
        
        js = anvil.js.window
        editor = js.document.getElementById("editor")
    
        # Clean HTML before sending to server (remove useless spans, empty tags, etc.)
        anvil.js.window.cleanEditorHTML(editor)
    
        # Get inner HTML from editor
        inner_html = editor.innerHTML
        
        # Basic CSS for PDF rendering 
        css = """
            @page {
                size: A4;
                margin: 2cm;
        
                /* Ligne gauche : numéro de page */
                @top-left {
                    content: counter(page) " / " counter(pages);
                    font-size: 9pt;
                }
        
                /* Ligne 1 : titre */
                @top-center {
                    content: string(title) "\A" string(subtitle);
                    white-space: pre;      /* Obligatoire pour autoriser le retour à la ligne */
                    font-size: 11pt;
                    font-weight: bold;
                }
        
                /* Pied de page : date */
                @bottom-center {
                    content: string(printdate);
                    font-size: 9pt;
                }
            }
        
            body {
                font-family: DejaVu Sans, sans-serif;
                font-size: 11pt;
                line-height: 1.4;
            }
        
            p {
                margin: 0 0 6pt 0;
            }
        
            /* Variables cachées pour string-set */
            h1.doc-title {
                string-set: title content();
                display: none;
            }
        
            h2.doc-subtitle {
                string-set: subtitle content();
                display: none;
            }
        
            span.print-date {
                string-set: printdate content();
                display: none;
            }
        """

        # Date de l'impression
        print_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        alert(print_date)
        alert(self.top_ligne_1)
        # Wrap inner HTML into a minimal full HTML document
        html_doc = f"""
            <html>
            <head>
                <meta charset="utf-8">
            
                <!-- Définition des strings pour WeasyPrint -->
                <meta name="title" content="{self.top_ligne_1}">
                <meta name="subtitle" content="{self.top_ligne_2}">
                <meta name="printdate" content="Imprimé le {print_date}">
            
                <style>
                    /* string-set global */
                    meta[name=title] {{"string-set: title attr(content);"}}
                    meta[name=subtitle] {{"string-set: subtitle attr(content);"}}
                    meta[name=printdate] {{"string-set: printdate attr(content);"}}
                </style>
            
                <title>Word editor export</title>
            </head>
            <body>
                {inner_html}
            </body>
            </html>
            """

    
        # Call the Uplink function
        with anvil.server.no_loading_indicator:
            pdf_media = anvil.server.call("render_pdf", html_doc, css, "texte.pdf")
    
        if pdf_media:
            anvil.media.download(pdf_media)
        else:
            alert("PDF generation failed on server.")

    
        



    

    

            

   
