import dataclasses
import re

from django.utils.safestring import mark_safe
from laces.components import Component


class TemplateStringComponent(Component):

    template: str = ''''''

    def get_template(self, fragments=None):
        return self.template

    def render_html(self, parent_context=None):
        from django.template import Template, RequestContext

        fragments = parent_context.get('fragments', '') if parent_context else None

        ignore_context = parent_context.get('ignore', True) if parent_context else True

        context_data = self.get_context_data(parent_context)

        if not ignore_context:
            context_data.update(parent_context.flatten() if parent_context and isinstance(parent_context, RequestContext) else parent_context or {})

        template = Template(self.get_template(fragments))

        # Get request from parent context if available
        request = parent_context.get('request') if parent_context else None

        rendered_template = template.render(RequestContext(request, context_data))
        minified_template = re.sub(r'\s+', ' ', rendered_template).strip()
        return mark_safe(minified_template)



class AutoContextMixin:
    def get_context_data(self, parent_context=None):
        return {field.name: getattr(self, field.name) for field in dataclasses.fields(self)}


class AutoTemplateStringComponent(AutoContextMixin, TemplateStringComponent):
    pass