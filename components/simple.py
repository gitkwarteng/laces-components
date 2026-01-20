import dataclasses
from typing import Any

from django.utils.html import format_html
from laces.components import Component


@dataclasses.dataclass(frozen=False)
class SimpleTemplateComponent(Component):
    field: str = None
    data: Any = None

    template = '''<span>{value}</span>'''

    def get_template(self, extra_contenxt=None):
        return self.template

    def get_template_data(self, extra_context=None):
        return {
            "field": self.field,
            "data": self.data
        }

    def render_html(self, parent_context=None):
        template_data = self.get_template_data(
            parent_context
        )
        return format_html(self.get_template(parent_context), **template_data)
