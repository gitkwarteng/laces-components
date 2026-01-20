
from django.http import HttpResponse
from django.urls import reverse

from .form import FormComponent, FormButton
from .table.columns import BaseColumn
from .table.table import TableComponent
from .enums import ViewActionScope
from .exceptions import CommonException
from .response import htmx_render


class ComponentViewMixin:

    component_class = None
    component_name = 'component'

    def get_component_class(self):
        return self.component_class

    def get_component_name(self):
        return self.component_name or self.get_component_class().__name__

    def get_component_kwargs(self):
        return {}

    def get_component(self):
        return self.get_component_class()(**self.get_component_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.get_component_name()] = self.get_component()
        return context


class TableComponentViewMixin:

    columns = []
    editable = False
    numbered = True
    pk_field = 'pk'
    page_size = 20

    def get_table_columns(self):
        if not self.columns:
            # Check if model has defined list_display
            list_display = getattr(self.model, 'list_display', [])
            if not list_display:
                # Dynamically generate list_display from model fields
                list_display = [
                    BaseColumn(name=field.name, header=field.verbose_name)
                    for field in self.model._meta.fields
                ]

            self.columns = list_display

        return self.columns

    def get_table_component(self):
        return TableComponent(
            data=self.get_queryset(),
            columns=self.get_table_columns(),
            model=self.model,
            editable=self.editable,
            numbered=self.numbered,
            pk_field=self.pk_field,
            page_size=self.page_size
        )

    def post(self, request, *args, **kwargs):
        try:
            action_scope = request.POST.get('scope', '')
            if action_scope != ViewActionScope.TABLE.value or not request.htmx:
                return super().post(request, *args, **kwargs)

            component = self.get_table_component()

            html, error_msg = component.update(request)
            return self.send_response(
                request=request, content=html, is_success=error_msg is None, message=error_msg, **kwargs)

        except (ValueError, CommonException) as ex:
            return self.send_response(request, content='', message=ex.__str__(), is_success=False)

        except Exception as ex:
            return self.send_response(content='', message=ex.__str__(), is_success=False, request=request)

    def send_response(self, request, content, is_success=True, **kwargs):
        message = kwargs.pop('message', None)
        if request.htmx:
            response = HttpResponse(content)
            return htmx_render(response, message=message, is_success=is_success)
        else:
            ctx = self.get_context_data(**kwargs)
            return self.render_to_response(ctx)


class FormComponentViewMixin:

    form_class = None
    form_method:str = 'get'
    form_action: str = ''
    form_button: FormButton = None
    cancel_button: FormButton = None
    form_element_class = 'form needs-validation'
    show_field_labels = True

    def get_form_component(self):
        return FormComponent(
            method=self.form_method,
            form_class=self.form_element_class,
            form=self.get_form(),
            action=self.get_form_action(),
            submit_button=self.get_form_button(),
            cancel_button=self.get_cancel_button(),
            show_field_labels=self.show_field_labels
        )

    def get_form_action(self):
        return self.form_action or self.request.path

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_form(self, form_class=None):
        return self.form_class(**self.get_form_kwargs())

    def get_form_button(self):
        return self.form_button or FormButton(text='Save', button_type='submit', classes='btn-lg btn-success mt-3')

    def get_cancel_button(self):
        return self.cancel_button or FormButton(
            text='Cancel', button_type='link', classes='btn-lg btn-light mt-3 me-5', icon='ri-close-fill',
            url=reverse(f'{self.model._meta.app_label}:{self.model.url_base_name}-list')
        )

