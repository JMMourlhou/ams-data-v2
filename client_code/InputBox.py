import anvil.server
import anvil
from functools import partial
from anvil_extras import augment
# from typing import List, Dict
from .

# automatic validation calling validator.are_all_valid() is only performed when clicking the default button

def _make_short_text_longer(text):
    n = int(max(8 - len(text), 0) / 2)
    return ' ' * n + text + ' ' * n


def _set_focus(sender, **event_args):
    sender.trigger('focus')


class InputBoxRow:
    def __init__(self, input_box: 'InputBox', row_type, text=None, prompt=None, validator=None, validator_args=None,
                 column_ratio=None, height=100, items=None, selected_value=None, checked=None, name=None, events=None,
                 visible=True, enabled=True):
        self.input_box = input_box
        self.row_type = row_type
        self.column_ratio = column_ratio or self.input_box.column_ratio
        self.validator = validator
        self.validator_args = validator_args
        self.events = events

        self.name = name or prompt or text

        self.width_left = int(self.input_box.width * self.column_ratio)
        self.width_right = self.input_box.width - self.width_left

        self.flow_panel = self.label = self.comp = None

        # create the label for the prompt, if required
        if row_type in {'textbox', 'textarea', 'dropdown', 'checkbox', 'button'}:
            self.flow_panel = anvil.FlowPanel(spacing_above=None, spacing_below=None, spacing='tiny', align='justify')
            self.input_box.linear_panel.add_component(self.flow_panel)

            if prompt is not None:
                self.label = anvil.RichText(content=prompt, spacing_above=None, spacing_below=None, width=self.width_left)
                self.flow_panel.add_component(self.label)
            else:
                self.width_right = self.input_box.width

        # create the main component
        if row_type == 'richtext':
            self.label = anvil.RichText(content=text, spacing_above=None, spacing_below=None)
            self.input_box.linear_panel.add_component(self.label)

        elif row_type == 'textbox':
            self.comp = anvil.TextBox(text=text, enabled=enabled, spacing_above=None, spacing_below=None, width=self.width_right)
            self.comp.add_event_handler('pressed_enter', partial(self.raise_event, self.input_box.pressed_enter))
            self.comp.select()
            self.complete_setup(self.comp)

        elif row_type == 'textarea':
            self.comp = anvil.TextArea(text=text, enabled=enabled, height=height, spacing_above=None, spacing_below=None, width=self.width_right)
            self.comp.select()
            self.complete_setup(self.comp)

        elif row_type == 'checkbox':
            self.comp = anvil.CheckBox(text=text, checked=checked, enabled=enabled, spacing_above=None, spacing_below=None, width=self.width_right)
            self.complete_setup(self.comp)

        elif row_type == 'button':
            self.comp = anvil.Button(text=_make_short_text_longer(text), enabled=enabled, spacing_above=None, spacing_below=None)
            self.complete_setup(self.comp)
            if not prompt:
                self.flow_panel.align = 'center'
            if not events or 'click' not in [e[0] for e in events]:
                # clicking on a button closes the dialog only if the click event for the button is not defined
                self.comp.add_event_handler('click', partial(self.raise_event, self.input_box.button_click))

        elif row_type == 'dropdown':
            self.comp = anvil.DropDown(items=items, selected_value=selected_value, enabled=enabled, spacing_above=None, spacing_below=None, width=self.width_right)
            self.complete_setup(self.comp)

        else:
            raise KeyError(f'Unexpected type: "{row_type}"')

        self.visible = visible

    @property
    def visible(self):
        return self.comp.visible

    @visible.setter
    def visible(self, value):
        for c in (self.comp, self.label, self.flow_panel):
            if c:
                c.visible = value

    @property
    def value(self):
        if self.row_type == 'textbox':  return self.comp.text
        if self.row_type == 'textarea': return self.comp.text
        if self.row_type == 'dropdown': return self.comp.selected_value
        if self.row_type == 'checkbox': return self.comp.checked

    @value.setter
    def value(self, value):
        for c in (self.comp, self.label, self.flow_panel):
            c.value = value

    def complete_setup(self, comp):
        self.flow_panel.add_component(comp)
        self.add_events(comp)
        self.add_validation(comp)

        if not self.input_box.focus_set and self.row_type != 'button':
            comp.add_event_handler('show', _set_focus)
            self.input_box.focus_set = True

    def add_validation(self, component):
        if self.validator:
            if type(self.validator) is list:
                self.validator_args = self.validator_args or [{}] * len(self.validator)
                for func, args in zip(self.validator, self.validator_args):
                    func(component, **args)
            else:
                self.validator_args = self.validator_args or {}
                self.validator(component, **self.validator_args)
            if self.validator:
                component.add_event_handler('hide',
                                            lambda event_name, sender: self.input_box.validator.hide_all_popovers())

    def add_events(self, component):
        for event_name, func in self.events or []:
            component.add_event_handler(event_name, partial(self.raise_event, func))

    def raise_event(self, func, **event_args):
        func(results=self.input_box.results, rows=self.input_box.rows, **event_args)


class InputBox:
    def __init__(self, title=None, buttons=None, large=False, dismissible=True, default_button='OK', column_ratio=0.6,
                 validator=None, form_show=None, items=None):
        self.title = title
        self.buttons = ['OK'] if buttons is None else buttons
        self.large = large
        self.dismissible = dismissible
        self.default_button = default_button
        self.column_ratio = column_ratio
        self.validator = validator
        self.form_show = form_show

        self.clicked_button = None
        self.rows_list: List[InputBoxRow] = []
        self.rows: Dict[str, InputBoxRow] = {}

        self.linear_panel = anvil.LinearPanel(spacing_above=None, spacing_below=None)
        self.width = 545 if self.large else 245
        self.width_left = int(self.width * self.column_ratio)
        self.width_right = self.width - self.width_left
        self.focus_set = False
        self.default_button_comp = None

        if form_show:
            self.linear_panel.add_event_handler('show', partial(self.raise_event, self.form_show))

        for item in items or []:
            item_type = item.get('type', 'textbox')
            if 'type' in item:
                del item['type']
            if item_type == 'richtext': self.add_richtext(**item)
            if item_type == 'textbox':  self.add_textbox(**item)
            if item_type == 'textarea': self.add_textarea(**item)
            if item_type == 'checkbox': self.add_checkbox(**item)
            if item_type == 'dropdown': self.add_dropdown(**item)
            if item_type == 'button':   self.add_button(**item)

    def show(self):
        # add flow panel with buttons at the bottom of the linear panel
        if self.buttons:
            flow_panel = anvil.FlowPanel(align='right', spacing='small', spacing_below=None)
            self.linear_panel.add_component(flow_panel)

            for item in self.buttons:
                comp = anvil.Button(text=_make_short_text_longer(item), spacing_above=None, spacing_below=None)
                flow_panel.add_component(comp)
                comp.add_event_handler('click', partial(self.raise_event, self.button_click))

        # find the default button
        all_buttons = [row.comp for row in self.rows_list if row.row_type=='button']
        if self.buttons:
            all_buttons.extend(flow_panel.get_components())

        for button in all_buttons:
            if button.text.strip() == self.default_button:
                self.default_button_comp = button
                if not self.focus_set:
                    self.default_button_comp.add_event_handler('show', _set_focus)
                break

        # show the input box and return the clicked button
        return anvil.alert(self.linear_panel, title=self.title, buttons=None, large=self.large, dismissible=self.dismissible)

    def button_click(self, sender, **event_args):
        if self.validator and sender is self.default_button_comp:
            if not self.validator.are_all_valid():
                return
        self.clicked_button = sender.text.strip()
        self.linear_panel.raise_event("x-close-alert", value=self.clicked_button)

    def pressed_enter(self, **event_args):
        if self.default_button_comp:
            self.default_button_comp.raise_event('click')

    def add_richtext(self, text, name=None, events=None, visible=True):
        self._add_row(InputBoxRow(row_type='richtext', input_box=self, text=text, name=name, events=events, visible=visible))

    def add_textbox(self, text, prompt=None, validator=None, validator_args=None, column_ratio=None, name=None, events=None, visible=True, enabled=True):
        self._add_row(InputBoxRow(row_type='textbox', input_box=self, text=text, prompt=prompt, validator=validator, validator_args=validator_args, column_ratio=column_ratio, name=name, events=events, visible=visible, enabled=enabled))

    def add_textarea(self, text, prompt=None, validator=None, validator_args=None, column_ratio=None, name=None, events=None, visible=True, enabled=True):
        self._add_row(InputBoxRow(row_type='textarea', input_box=self, text=text, prompt=prompt, validator=validator, validator_args=validator_args, column_ratio=column_ratio, name=name, events=events, visible=visible, enabled=enabled))

    def add_dropdown(self, items, selected_value=None, prompt=None, validator=None, validator_args=None, column_ratio=None, name=None, events=None, visible=True, enabled=True):
        self._add_row(InputBoxRow(row_type='dropdown', input_box=self, items=items, selected_value=selected_value, prompt=prompt, validator=validator, validator_args=validator_args, column_ratio=column_ratio, name=name, events=events, visible=visible, enabled=enabled))

    def add_checkbox(self, text=None, checked=True, prompt=None, column_ratio=None, name=None, events=None, visible=True, enabled=True):
        self._add_row(InputBoxRow(row_type='checkbox', input_box=self, text=text, checked=checked, prompt=prompt, column_ratio=column_ratio, name=name, events=events, visible=visible, enabled=enabled))

    def add_button(self, text, name=None, prompt=None, events=None, visible=True, enabled=True):
        self._add_row(InputBoxRow(row_type='button', input_box=self, text=text, prompt=prompt, name=name, events=events, visible=visible, enabled=enabled))

    def _add_row(self, row):
        self.rows_list.append(row)
        if row.name:
            self.rows[row.name] = row

    @property
    def results(self):
        results = {row.name: row.value for row in self.rows_list if row.row_type not in ('richtext', 'button')}
        results['clicked_button'] = self.clicked_button
        return results

    def raise_event(self, func, **event_args):
        func(results=self.results, rows=self.rows, **event_args)


def alert2(richtext, title=None, buttons=None, large=False, dismissible=True, default_button='OK'):
    ib = InputBox(title, buttons, large, dismissible, default_button=default_button)
    ib.add_richtext(richtext)
    ib.show()
    return ib.clicked_button


def input_box(items, title=None, buttons=None, large=False, dismissible=True, default_button='OK', column_ratio=0.6, validator=None, form_show=None):
    ib = InputBox(items=items, title=title, buttons=buttons, large=large, dismissible=dismissible, default_button=default_button, column_ratio=column_ratio, validator=validator, form_show=form_show)
    ib.show()
    return ib.results

def multi_select_dropdown(title, items, text=None, show_select_all=False, show_ok_cancel=True):
    def set_checkboxes(rows, value):
        for name in ['One', 'Two', 'Three', 'Four']:
            if rows[name].comp.enabled:
                rows[name].comp.checked = value

    def multiselectdropdown_selectall(rows, **event_args):
        set_checkboxes(rows, True)

    def multiselectdropdown_deselectall(rows, **event_args):
        set_checkboxes(rows, False)

    buttons = ['OK', 'Cancel'] if show_ok_cancel else []
    ib = InputBox(title, buttons)

    if text:
        ib.add_richtext(text)

    if show_select_all:
        ib.add_button('Select all', events=[('click', multiselectdropdown_selectall)])
        ib.add_button('Deselect all', events=[('click', multiselectdropdown_deselectall)])

    for item in items:
        if item:
            ib.add_checkbox(
                text=item[0],
                checked=item[1] if len(item) > 1 else True,
                prompt=item[2] if len(item) > 2 else None,
                enabled=item[3] if len(item) > 3 else True,
                name=item[0],
            )
        else:
            ib.add_richtext("---")

    ib.show()

    return ib.results
