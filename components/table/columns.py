import dataclasses
import datetime
import re
from typing import Optional, List, Any, Dict

from django.urls import reverse
from django.db import models
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from laces.components import Component

from ..enums import ViewActionScope, UpdateAction
from ..utils import two_d


@dataclasses.dataclass(frozen=False)
class BaseColumn(Component):
    name: str
    header: str = None
    key: str = None
    sortable: bool = True
    editable: bool = False
    align: str = "left"
    styles: str = ""
    classes: str = ""
    field_name = None

    template = '''<span>{value}</span>'''

    td_str = '''<td class="text-{align} {class}" style="{style}">%s</td>'''

    pk_field = "pk"

    def __post_init__(self):
        self.header = self.header or self.name.replace('_', ' ').replace('-', ' ').title()
        self.key = self.key or self.name
        self.field_name = self.name

    def get_value(self, row):
        keys = self.key.split('.')
        value = row

        for key in keys:
            if hasattr(value, key):
                value = getattr(value, key)
            elif isinstance(value, dict):
                value = value.get(key)
            else:
                return ""

            if value is None:
                return ""

        return value

    def get_id(self, row):
        if hasattr(row, self.pk_field):
            return getattr(row, self.pk_field)
        return row.get("id") if isinstance(row, dict) else None

    def get_row(self, context=None):
        return context.get("row") if context else None

    def render(self, row):
        return self.get_value(row)

    def get_styles(self):
        return self.styles

    def get_classes(self):
        return self.classes

    def get_template(self, value):
        return self.template if self.editable else value

    def get_template_data(self, value, row_id, row, extra_context=None):
        return {
            "value": value,
            "class": self.get_classes(),
            "style": self.get_styles(),
            'align':self.align
        }

    def render_html(self, parent_context=None):
        row  = self.get_row(parent_context)
        value = self.get_value(row)
        template_data = self.get_template_data(
            value, self.get_id(row), row, parent_context
        )
        # Render mode determines whether column is rendered with td element or only input.
        #  Options are either 'full' or 'partial'
        render_mode = parent_context.get("render_mode", 'full') if parent_context else 'full'

        column_string = self.td_str % self.get_template(value) if render_mode == 'full' else self.get_template(value)

        html_minified = re.sub(r'\s+', ' ', column_string).strip()

        return format_html(html_minified, **template_data)


@dataclasses.dataclass
class LinkColumn(BaseColumn):
    detail: bool = False
    url_name: str = None

    template = '''<span><a href="{url}" hx-get="{url}" class="">{value}</a></span>'''
    url_args: List[str] = dataclasses.field(default_factory=list)

    def get_url(self, row):
        try:
            if hasattr(row, 'get_detail_url'):
                return row.get_detail_url()
            if self.url_name:
                if self.detail:
                    self.url_args = ['pk'] + self.url_args
                args = [getattr(row, arg) for arg in self.url_args]
                return reverse(self.url_name, args=args)
            return "#"
        except:
            return "#"

    def get_template_data(self, value, row_id, row, extra_context=None):
        url = self.get_url(row)
        data = super().get_template_data(value, row_id, row, extra_context)
        data['url'] = url
        return data

    def get_template(self, value):
        return self.template


@dataclasses.dataclass(frozen=False)
class HTMLInputColumn(BaseColumn):
    input_type = "text"

    input_class:str = ""
    input_style:str = ""

    attrs:Dict[str, str] = dataclasses.field(default_factory=dict)

    template = '''
    <input type="{input_type}" name="{name}" id="{id}" value="{value}" class="form-control rounded text-{align}" {attrs} />
    '''

    def get_input_type(self):
        return self.input_type

    def get_template(self, value):
        return self.template if self.editable else '<span>{value}</span>'

    def get_input_name(self, row_id):
        return f'row-{row_id}-{self.field_name}'

    def get_value_from_data(self, row_id, data):
        return data.get(self.get_input_name(row_id))

    def get_template_data(self, value, row_id, row, extra_context=None):
        data = super().get_template_data(value, row_id, row)
        input_name = self.get_input_name(row_id)
        data.update({
            "input_type": self.get_input_type(),
            "name": input_name,
            "id": f'id_{input_name}',
            "input_class": self.input_class,
            'input_style': self.input_style,
            'attrs': mark_safe(" ".join([f'{key}={value}' for key, value in self.attrs.items()])),
        })

        return data

@dataclasses.dataclass(frozen=False)
class TextColumn(HTMLInputColumn):
    hx_post:str = ''
    hx_target:str = 'closest td'
    hx_trigger:str = 'keyup[key=="Enter"] changed'
    hx_indicator:str = '#indicator'
    hx_swap:str = 'innerHTML'
    action:UpdateAction = UpdateAction.UPDATE_CELL
    scope: ViewActionScope = ViewActionScope.TABLE

    hx_attrs = ''' hx-post="{post}" hx-target="{target}" hx-trigger='{trigger}' hx-indicator="{indicator}" hx-swap="{swap} ignoreTitle:true" hx-push-url="false" '''

    template = '''
        <input type="{input_type}"
               name="{name}" id="{id}"
               value="{value}" autocomplete="off"
               data-submit="{submit}"
               hx-vals='{{"id": "{row_id}", "field": "{field}", "action":"{action}", "scope":"{scope}"}}'
               {htmx}
               class="form-control p-2 text-{align} {input_class}"
               style="{input_style}" {attrs} />
        '''

    def render(self, row):
        return escape(str(self.get_value(row) or ""))

    def get_hx_target(self):
        return 'closest td' if self.action.is_cell else 'closest tr'

    def get_htmx_attributes(self):
        return self.hx_attrs.format(
            post=self.hx_post,
            target=self.get_hx_target(),
            trigger=self.hx_trigger,
            indicator=self.hx_indicator,
            swap=self.hx_swap
        )

    def get_submit(self):
        return 'cell' if self.action.is_cell else 'row'

    def get_template_data(self, value, row_id, row, extra_context=None):

        # Check render mode from parent context
        render_mode = extra_context.get("render_mode", 'full') if extra_context else 'full'
        # Add out of band swap attribute to attributes if render mode is partial
        if render_mode == 'partial':
            self.attrs['hx-swap-oob'] = '"true"'

        data  = super().get_template_data(value, row_id, row, extra_context=extra_context)

        data.update({
            "row_id": row_id,
            "field": self.field_name,
            "htmx": mark_safe(self.get_htmx_attributes()),
            'submit':self.get_submit(),
            'action':self.action.value,
            'scope': self.scope.value,
        })
        return data


class NumberColumn(TextColumn):

    input_type = "number"


@dataclasses.dataclass(frozen=False)
class DecimalColumn(TextColumn):

    input_class:str = 'pe-2'
    align:str = 'end'

    def get_value(self, row):
        value = super().get_value(row)
        return two_d(value)


@dataclasses.dataclass(frozen=False)
class QuantityColumn(TextColumn):

    input_class:str = 'quantity-input'
    align:str = 'center'

    reduce_button_template = '''
         <button type="button" class="btn quantity-left-minus btn-subtle-danger" 
            name="{name}_down" value="-"  data-submit="{submit}"
            hx-vals='{{"id": "{row_id}", "field": "{field}", "action":"{action}", "operation":"-", "scope":"{scope}"}}'
            {button_htmx}
            data-type="minus" data-field="" style="padding:10px 15px;">
            <i class="fa fa-minus"></i>
        </button>
    '''

    increase_button_template = '''
         <button type="button" class="btn quantity-right-plus btn-subtle-success" 
         name="{name}_up" value="+"  data-submit="{submit}"
         hx-vals='{{"id": "{row_id}", "field": "{field}", "action":"{action}", "operation":"+", "scope":"{scope}"}}'
         {button_htmx}
            data-type="plus" data-field=""  style="padding:10px 15px;">
            <i class="fa fa-plus"></i>
            </button>
    '''

    # def get_value(self, row):
    #     value = super().get_value(row)
    #     return two_d(value)

    def get_button_htmx_attrs(self):
        return self.hx_attrs.format(
            post=self.hx_post,
            target=self.get_hx_target(),
            trigger='click',
            indicator=self.hx_indicator,
            swap=self.hx_swap
        )

    def get_template(self, value):
        if not self.editable:
            return super().get_template(value)

        return f'''
            <div class="input-group flex-nowrap" >
            {self.reduce_button_template}
            {super().get_template(value)}
            {self.increase_button_template}
            </div>
        '''

    def get_template_data(self, value, row_id, row, extra_context=None):
        data = super().get_template_data(value, row_id, row)
        data.update({
            "button_htmx": mark_safe(self.get_button_htmx_attrs())
        })
        return data


class DateColumn(TextColumn):

    input_type = "date"

    def render(self, row):
        date_value: datetime.date = self.get_value(row)
        return escape(date_value.strftime("%Y-%m-%d")) if date_value else ""


@dataclasses.dataclass(frozen=False)
class SelectColumn(TextColumn):

    options: Optional[List[Any]] = None
    hx_trigger:str = 'change'

    template = '''
        <select name="{name}" id="{id}" autocomplete="off"
            hx-vals='{{"id": "{row_id}", "field": "{field}", "action":"{action}", "scope":"{scope}"}}'
            {htmx}
            data-submit="{submit}"
            class="form-select rounded" {attrs} >
            {options}
        </select>
    '''

    def get_value_options(self, value, row):
        if self.options:
            return self.options
        if not value:
            return []
        # Check if value is an instance of a model
        return [
            (item.id, item.__str__()) for item in value.__class__.objects.enabled()
        ] if isinstance(value, models.Model) else []

    def get_options(self, value, row):
        options_templ = []
        options = self.get_value_options(value, row)
        for value_id, label in options:
            selected = "selected" if value_id == value.id else ""
            options_templ.append(f'<option value="{value_id}" {selected}>{label}</option>')
        if options_templ:
            return mark_safe("\n".join(options_templ))
        return ""

    def get_template_data(self, value, row_id, row, extra_context=None):
        data = super().get_template_data(value, row_id, row)
        data.update({
            "options": mark_safe(self.get_options(value, row))
        })
        return data


@dataclasses.dataclass(kw_only=True, frozen=False)
class ButtonColumn(HTMLInputColumn):
    btn_class: str = "primary"
    label:str = "Click"
    url:str = "#"
    key = "id"
    editable = False
    sortable = False
    input_type:str = 'button'
    scope: ViewActionScope = ViewActionScope.TABLE

    template = '''
        <button type="{input_type}"
                name="action" value="update-row"
                class="btn btn-{btn_class} px-3 py-2 rounded" 
                data-submit="row"
                hx-vals='{{"id": "{row_id}"}}'
                hx-indicator="#indicator"
                hx-post="{url}" hx-target="closest tr" hx-swap="outerHTML">
            {label}
        </button>
    '''

    def get_url(self, row_id, row):
        return ""

    def get_template(self, value):
        return self.template

    def get_template_data(self, value, row_id, row, extra_context=None):
        data = super().get_template_data(value, row_id, row)
        data.update({
            "row_id": row_id,
            "btn_class": self.btn_class,
            "label": self.label,
            "url": self.get_url(row_id, row),
            # 'hx_vals':'js:{...getRowData(this)}'
            'scope': self.scope.value,
        })

        return data


class LinkButtonColumn(ButtonColumn):
    template = '''
            <a href="#" role="{input_type}"
                    class="btn btn-{btn_class} px-3 py-1 rounded" 
                    data-submit="row"
                    hx-vals='{{"id": "{row_id}", "action":"update-row", "scope":"{scope}"}}'
                    hx-indicator="#indicator"
                    hx-post="{url}" hx-target="closest tr" hx-swap="outerHTML">
                {label}
            </a>
        '''

class DeleteButtonColumn(ButtonColumn):

    template = '''
        <div class="position-relative">
            <div class="hover-actions" style="top: -20px;">
                <a href="#" style="border-radius: .8rem;"
                    class="btn btn-subtle-danger text-danger px-3" 
                    data-submit="row"
                    hx-vals='{{"id": "{row_id}", "action":"delete", "scope":"{scope}"}}'
                    hx-indicator="#indicator"
                    hx-post="{url}" hx-target="closest tr" hx-swap="delete">
                    <i class="fa text-center fa-trash"></i>
                </a>
            </div>
        </div>
        '''

class AddRowButtonColumn(ButtonColumn):
    template = '''
        <input type="hidden" data-submit="row" name="product_id" id="new-row"
            hx-vals='{{"action":"add", "scope":"{scope}"}}'
            hx-indicator="#indicator" hx-trigger="changed"
            hx-post="{url}" hx-target="closest tr" hx-swap="none" />
        '''



class ModalLinkButtonColumn(ButtonColumn):
    onclick:str = 'V.modals.detail_modal(this)'

    template = '''
            <a href="{url}" role="{input_type}"
                onclick="{onclick};return false;"
                class="btn btn-{btn_class} px-3 py-1 rounded" 
            >
                {label}
            </a>
        '''

    def get_template_data(self, value, row_id, row, extra_context=None):
        data = super().get_template_data(value, row_id, row)
        data.update({
            "onclick": self.onclick,
        })

        return data