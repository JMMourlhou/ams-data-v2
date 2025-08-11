from ._anvil_designer import PageBreakTemplate

def _css_length(v):
    try:
        return f"{float(v)}px"
    except (TypeError, ValueError):
        return v

class PageBreak(PageBreakTemplate):
    def __init__(self, **properties):
        self._props = {}
        self.init_components(**properties)

    @property
    def margin_top(self):
        return self._props.get("margin_top")

    @margin_top.setter
    def margin_top(self, value):
        self._props["margin_top"] = value
        self.dom_nodes["ae-page-break-margin-element"].style.marginTop = _css_length(value)

    @property
    def border(self):
        return self._props.get("border")

    @border.setter
    def border(self, value):
        self._props["border"] = value
        self.dom_nodes["ae-page-break-container"].style.border = value