from ._anvil_designer import Word_editorTemplate
from anvil import *
import anvil.js
from anvil.js import window
from datetime import datetime

# ========================================================================================
# Force the browser to use inline CSS formatting (style="...") instead of deprecated <font>
# This ensures compatibility with modern browsers and WeasyPrint.
# ========================================================================================
anvil.js.window.document.execCommand("styleWithCSS", False, True)


class Word_editor(Word_editorTemplate):

    # ====================================================================================
    # INITIALISATION # top_ligne_1, top_ligne_2 used for PDF export
    # ====================================================================================
    def __init__(self, top_ligne_1, top_ligne_2, **properties):

        # Anvil initialisation
        self.init_components(**properties)

        # Responsive UI (small screens → menus on sides)
        if window.innerWidth < 800:
            self.column_panel_menu1.visible = False
            self.column_panel_menu2.visible = False
            self.column_panel_menu1_left.visible = True
            self.column_panel_menu2_right.visible = True
            self.button_validation.visible = False
        else:
            self.column_panel_menu1.visible = True
            self.column_panel_menu2.visible = True
            self.column_panel_menu1_left.visible = False
            self.column_panel_menu2_right.visible = False

        # Titles used for PDF export
        self.top_ligne_1 = top_ligne_1
        self.top_ligne_2 = top_ligne_2


        # ====================================================================================
        # 1) CLEAN HTML (removes useless spans, empty paragraphs, redundant wrappers, etc.)
        # ====================================================================================
        js_clean_html = """
        window.cleanEditorHTML = function(root) {             // root = editable editor div
            if (!root) return;

            // Remove wrapper span while keeping its children
            function unwrap(node) {
                const parent = node.parentNode;
                if (!parent) return;
                while (node.firstChild) parent.insertBefore(node.firstChild, node);
                parent.removeChild(node);
            }

            // 1) Remove empty spans or spans without attributes
            const spans = root.querySelectorAll("span");
            spans.forEach(function(span) {
                if (!span.attributes || span.attributes.length === 0)
                    unwrap(span);
            });

            // 2) Merge nested spans that have identical styles
            const spans_same = root.querySelectorAll("span");
            spans_same.forEach(function(span) {
                const parent = span.parentNode;
                if (!parent || parent.tagName !== "SPAN") return;

                const cs = span.getAttribute("style") || "";
                const ps = parent.getAttribute("style") || "";

                const clean_cs = cs.replace(/\\s+/g, "").toLowerCase();
                const clean_ps = ps.replace(/\\s+/g, "").toLowerCase();

                if (clean_cs === clean_ps) unwrap(span);
            });

            // 3) Remove spans that contain no visible text
            const empty_spans = root.querySelectorAll("span");
            empty_spans.forEach(function(span) {
                const txt = span.textContent || "";
                const hasChild = span.querySelector("*");
                if (!hasChild && txt.trim() === "") unwrap(span);
            });

            // 4) Remove duplicate empty paragraphs (<p><br></p> or empty)
            let previousEmpty = false;
            root.querySelectorAll("p").forEach(function(p) {
                const txt = p.textContent || "";
                const isEmpty = txt.replace(/\\u00A0/g,"").trim() === "";
                if (isEmpty) {
                    if (previousEmpty) p.parentNode.removeChild(p);
                    previousEmpty = true;
                }
                else previousEmpty = false;
            });
        };
        """
        anvil.js.window.eval(js_clean_html)


        # ====================================================================================
        # 2) SELECTION OFFSETS (most robust method to restore selection after DOM changes)
        # ====================================================================================
        js_offsets = """
        window.editorSelection = {start:0, end:0};

        // Save selection → convert to absolute character offsets inside editor
        window.saveSelectionOffsets = function(root) {
            const sel = window.getSelection();
            if (!sel.rangeCount) return;

            const range = sel.getRangeAt(0);

            function getOffset(el, range, isEnd) {
                let offset = 0;
                const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                while (walker.nextNode()) {
                    const node = walker.currentNode;
                    if (node === range[isEnd ? "endContainer" : "startContainer"])
                        return offset + range[isEnd ? "endOffset" : "startOffset"];
                    offset += node.length;
                }
                return offset;
            }

            window.editorSelection.start = getOffset(root, range, false);
            window.editorSelection.end   = getOffset(root, range, true);
        };

        // Restore selection using saved offsets
        window.restoreSelectionOffsets = function(root) {
            const sel = window.getSelection();
            sel.removeAllRanges();

            function findNode(el, charIndex) {
                let walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                let count = 0;
                while (walker.nextNode()) {
                    const node = walker.currentNode;
                    if (count + node.length >= charIndex)
                        return {node, offset: charIndex - count};
                    count += node.length;
                }
                return null;
            }

            const start = findNode(root, window.editorSelection.start);
            const end   = findNode(root, window.editorSelection.end);
            if (!start || !end) return;

            const range = document.createRange();
            range.setStart(start.node, start.offset);
            range.setEnd(end.node, end.offset);
            sel.addRange(range);
        };
        """
        anvil.js.window.eval(js_offsets)


        # ====================================================================================
        # 3) CLEAN COLOR SPANS (used before recoloring text)
        # ====================================================================================
        js_clean_color = """
        window.cleanColorInSelection = function() {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;

            const range = sel.getRangeAt(0);

            function unwrap(span) {
                const parent = span.parentNode;
                while (span.firstChild) parent.insertBefore(span.firstChild, span);
                parent.removeChild(span);
            }

            const walker = document.createTreeWalker(
                range.commonAncestorContainer, NodeFilter.SHOW_ELEMENT,
                {
                    acceptNode: node =>
                        (node.tagName === "SPAN" &&
                         node.style && node.style.color)
                        ? NodeFilter.FILTER_ACCEPT
                        : NodeFilter.FILTER_REJECT
                }
            );

            let node;
            const list = [];
            while (node = walker.nextNode()) list.push(node);
            list.forEach(n => unwrap(n));
        };
        """
        anvil.js.window.eval(js_clean_color)



    # ====================================================================================
    # DISPLAY INITIAL CONTENT
    # ====================================================================================
    def form_show(self, **event_args):
        editor = anvil.js.window.document.getElementById("editor")
        editor.innerHTML = f"<p>{self.text}</p>"


    # ====================================================================================
    # BASIC FORMATTING ACTIONS
    # ====================================================================================
    def button_bold_click(self, **e):
        anvil.js.window.document.execCommand("bold")

    def button_italic_click(self, **e):
        anvil.js.window.document.execCommand("italic")

    def button_underlined_click(self, **e):
        anvil.js.window.document.execCommand("underline")


    # ====================================================================================
    # FONT SIZE HANDLING
    # ====================================================================================
    def drop_down_font_size_change(self, **e):
        size_px = self.drop_down_font_size.selected_value
        if not size_px:
            return

        mapping = {"10":"1","12":"2","16":"3","18":"4","24":"5","32":"6","48":"7"}

        anvil.js.window.document.execCommand("fontSize", False, mapping.get(size_px, "3"))

        self._fix_font_size(size_px)
        self.drop_down_font_size.selected_value = self.drop_down_font_size.items[0]

    def _fix_font_size(self, size_px):
        sel = anvil.js.window.getSelection()
        if sel.rangeCount == 0:
            return

        range = sel.getRangeAt(0)
        node = range.commonAncestorContainer

        while node and node.nodeType != 1:
            node = node.parentNode

        if hasattr(node, "style"):
            node.style.fontSize = f"{size_px}px"


    # ====================================================================================
    # ERASE FORMATTING
    # ====================================================================================
    def button_erase_click(self, **e):
        sel = anvil.js.window.getSelection()
        if sel.rangeCount == 0:
            return
        text = sel.toString()
        if not text:
            alert("Sélectionne du texte d'abord")
            return
        anvil.js.window.document.execCommand("insertHTML", False, text)


    # ====================================================================================
    # COLOR CHANGE (with selection preserved)
    # ====================================================================================
    def color_change(self, color, **event_args):
        js = anvil.js.window
        editor = js.document.getElementById("editor")
        sel = js.getSelection()

        if sel.rangeCount == 0 or sel.toString() == "":
            alert("Sélectionne le texte d'abord")
            return

        js.saveSelectionOffsets(editor)
        js.cleanColorInSelection()
        js.restoreSelectionOffsets(editor)

        js.document.execCommand("foreColor", False, color)
        js.restoreSelectionOffsets(editor)
        editor.focus()

    # Color buttons
    def button_red_click(self, **e):    self.color_change("#FA0000")
    def button_green_click(self, **e):  self.color_change("#60FA00")
    def button_blue_click(self, **e):   self.color_change("#00C0FA")
    def button_orange_click(self, **e): self.color_change("#FAA300")
    def button_yellow_click(self, **e): self.color_change("#F2FA00")


    # ====================================================================================
    # ALIGNMENT CONTROLS
    # ====================================================================================
    def _apply_alignment(self, command):
        js = anvil.js.window
        editor = js.document.getElementById("editor")

        if js.getSelection().rangeCount == 0:
            alert("Place le curseur dans un paragraphe")
            return

        js.document.execCommand(command, False, None)
        editor.focus()

    def button_align_left_click(self, **e):    self._apply_alignment("justifyLeft")
    def button_align_center_click(self, **e):  self._apply_alignment("justifyCenter")
    def button_align_right_click(self, **e):   self._apply_alignment("justifyRight")
    def button_align_justify_click(self, **e): self._apply_alignment("justifyFull")


    # ====================================================================================
    # BULLET LISTS
    # ====================================================================================
    def button_bullet_click(self, **e):
        js = anvil.js.window
        editor = js.document.getElementById("editor")
        if js.getSelection().rangeCount == 0:
            alert("Place le curseur dans un paragraphe")
            return
        js.document.execCommand("insertUnorderedList", False, None)
        editor.focus()


    # ====================================================================================
    # VALIDATION (save and return to caller)
    # ====================================================================================
    def button_validation_click(self, **e):
        editor = anvil.js.window.document.getElementById("editor")
        anvil.js.window.cleanEditorHTML(editor)
        self.text = editor.innerHTML
        self.raise_event('x-fin_saisie')
        self.remove_from_parent()


    # ====================================================================================
    # TIMER 1 — keeps server session alive
    # ====================================================================================
    def timer_1_tick(self, **event_args):
        with anvil.server.no_loading_indicator:
            try:
                anvil.server.call("ping")          # Very light server call
            except:
                pass


    # ====================================================================================
    # TIMER 2 — auto-save backup
    # ====================================================================================
    def timer_2_tick(self, **event_args):
        editor = anvil.js.window.document.getElementById("editor")
        anvil.js.window.cleanEditorHTML(editor)
        self.text = editor.innerHTML
        self.raise_event("x-timer_text_backup")


    # ====================================================================================
    # TIMER 3 — gentle blinking of validation button
    # ====================================================================================
    def timer_3_tick(self, **event_args):

        if self.button_validation.foreground == "theme:On Primary":
            self.button_validation.foreground = "theme:On Primary Container"
            self.button_validation_copy.foreground = "theme:On Primary Container"
        else:
            self.button_validation.foreground = "theme:On Primary"
            self.button_validation_copy.foreground = "theme:On Primary"


    # ====================================================================================
    # PDF EXPORT using uplink "render_pdf"
    # ====================================================================================
    def button_download_click(self, **e):

        js = anvil.js.window
        editor = js.document.getElementById("editor")

        # Clean HTML before sending to PDF engine
        anvil.js.window.cleanEditorHTML(editor)

        inner_html = editor.innerHTML

        # Minimal CSS for PDF
        css = """
            @page {
                size: A4;
                margin: 2cm;
            
                @top-right {
                    content: counter(page) " / " counter(pages);
                    font-size: 9pt;
                }
            
                @top-center {
                    content: string(title) "\A" string(subtitle);
                    white-space: pre;
                    font-size: 11pt;
                    font-weight: bold;
                    text-align: center;
            
                    padding-bottom: 2mm;     /* petit espace interne */
                    border-bottom: 1px solid #888;  /* ligne de séparation */
                    margin-bottom: 0;        /* supprime espace sous l’en-tête */
                }
            
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
            
            h1.doc-title {
                string-set: title content();
                display: block;
                height: 0;
                overflow: hidden;
            }
            
            h2.doc-subtitle {
                string-set: subtitle content();
                display: block;
                height: 0;
                overflow: hidden;
            }
            
            span.print-date {
                string-set: printdate content();
                display: block;
                height: 0;
                overflow: hidden;
            }
            """

        print_date = datetime.now().strftime("%d/%m/%Y à %H:%M")

        html_doc = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Word editor export</title>
        </head>
        
        <body>
        
            <!-- Variables invisibles pour WeasyPrint -->
            <h1 class="doc-title">{self.top_ligne_1}</h1>
            <h2 class="doc-subtitle">{self.top_ligne_2}</h2>
            <span class="print-date">Imprimé le {print_date}</span>
        
            <!-- Contenu du word editor -->
            {inner_html}
        
        </body>
        </html>
        """


        with anvil.server.no_loading_indicator:
            pdf_media = anvil.server.call("render_pdf", html_doc, css, self.top_ligne_1)

        if pdf_media:
            anvil.media.download(pdf_media)
        else:
            alert("Erreur lors de la génération du PDF")

    def button_exit_click(self, **event_args):
        """This method is called when the button is clicked"""
        editor = anvil.js.window.document.getElementById("editor")
        anvil.js.window.cleanEditorHTML(editor)
        self.text = ""
        self.param1 = "exit"
        self.raise_event('x-fin_saisie')
        self.remove_from_parent()

    def button_link_click(self, **event_args):
        """Insert a hyperlink around the currently selected text inside the contenteditable editor."""
        js = anvil.js.window
    
        # 1) Save the current selection BEFORE opening the alert.
        # Opening an Anvil alert removes focus from the editor and destroys
        # the selection/range, so we must store it now.
        saved_range = js.saveSelection()
    
        # If no selection exists, we cannot insert a link.
        if not saved_range or js.getSelection().toString().strip() == "":
            alert("Sélectionne d'abord un texte à transformer en lien.")  # French alert per your requirement
            return
    
        # 2) Create a TextBox where the user can input the URL.
        tb = TextBox(placeholder="https://example.com")
    
        # Show the alert (large=True ensures the TextBox is editable).
        # IMPORTANT: While the alert is open, the selection is lost — but we have saved it.
        res = alert(
            title="Insert Link",
            content=tb,
            large=True,
            buttons=[("OK", True), ("Cancel", False)]
        )
    
        # If the user pressed Cancel or entered an empty URL, stop here.
        if not res or not tb.text.strip():
            return
    
        link_url = tb.text.strip()
    
        # 3) Restore the text selection INSIDE the editor.
        # Without this step, execCommand() would have no range to apply the link to.
        js.restoreSelection(saved_range)
    
        # 4) Insert the hyperlink using execCommand().
        # This automatically wraps the selected text in:
        #     <a href="URL">selected text</a>
        try:
            js.document.execCommand("createLink", False, link_url)
        except Exception as e:
            # If something goes wrong, notify the user.
            alert(f"Unable to insert link.\nError: {e}")


