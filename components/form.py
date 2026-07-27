import dataclasses
from typing import Optional, List

from django.forms import Form as DjangoForm
from django.utils.safestring import mark_safe

from .base import AutoTemplateStringComponent
from .enums import InlineFormsetDisplay


@dataclasses.dataclass
class FormButton(AutoTemplateStringComponent):
    text: str
    url: str = ''
    # Button type can be a submit, reset, button or link.
    # link button will use a link instead of button element
    button_type: str = 'button'
    classes: str = 'btn-primary'
    icon: str = 'ri-save-3-fill '

    template = '''
    {% if button_type == 'link' %}
        <a href="{{ url }}" class="btn {{ classes }}"><i class="{{ icon }} align-bottom me-1"></i> {{ text }}</a>
    {% else %}
        <button type="{{ button_type }}" class="btn {{ classes }}">
        <i class="{{ icon }} align-bottom me-1"></i>{{ text }}</button>
    {% endif %}
    '''


@dataclasses.dataclass
class FormComponent(AutoTemplateStringComponent):
    """
    Renders a form with bootstrap classes
    """
    form:DjangoForm
    submit_button: Optional[FormButton] = None
    cancel_button: Optional[FormButton] = None
    action:str = ""
    method:str = 'get'
    form_id:str = None
    css_class:str = 'form'
    field_size: str = 'col-md-6 col-12'
    show_field_labels:bool = True
    alignment:str = 'left'

    htmx_attrs: Optional[str] = None

    template = '''
    {% load widget_tweaks laces %}
    <form method="{{ method }}" class="{{ css_class }}" action="{{ action }}" hx-{{ method }}="{{ action }}" id="#{{ form_id }}" {{ htmx_attrs }}>
        {% if form.non_field_errors %}
            <div class="alert alert-danger" role="alert">
                {% for error in form.non_field_errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}
        {% if method.lower == 'post' %}
            {% csrf_token %}
        {% endif %}
        <div class="row justify-content-{{alignment}} px-3">
            {% for field in form %}
                {% include 'components/forms/form-field.html' with field=field field_size=field_size show_field_labels=show_field_labels %}
            {% endfor %}
            
            {% if method != 'get' %} </div><div class="row justify-content-center"> {% endif %} 
            <div class="col col-auto mb-2">
                <div class="hstack gap-2 justify-content-end d-print-none mt-4 mt-md-0">
                    
                    {% if cancel_button %}
                        {% component cancel_button %}
                    {% endif %}
                    
                    {% if submit_button %}
                        {% component submit_button %}
                    {% endif %}
                </div>
            </div>
        </div>
        
    </form>
    '''


@dataclasses.dataclass
class InlineFormset:
    form: DjangoForm = None
    form_class: DjangoForm = DjangoForm
    method: str = 'post'
    id: str = None
    css_class: str = 'form'
    title: str = 'Items'
    # Inline formsets can be rendered as table or list
    # table will render the formset as a table, list will render as a list
    display: InlineFormsetDisplay = InlineFormsetDisplay.TABLE


@dataclasses.dataclass
class InlineFormsetFormComponent(FormComponent):
    """
    Renders a form with bootstrap classes
    """
    formsets: List[InlineFormset] = dataclasses.field(default_factory=list)

    template = '''
    {% load widget_tweaks laces %}
    <form method="{{ method }}" class="{{ form_class }}" action="{{ action }}" id="#{{ form_id }}">
        {% if form.non_field_errors %}
            <div class="alert alert-danger" role="alert">
                {% for error in form.non_field_errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}
        {% if method.lower == 'post' %}
            {% csrf_token %}
        {% endif %}
        <div class="row justify-content-{{alignment}} px-3">
            {% for field in form %}
                {% include 'components/forms/form-field.html' with field=field field_size=field_size show_field_labels=show_field_labels %}
            {% endfor %}
        </div>
        
        {% if formsets %}
            {% for formset in formsets %}
            
                <h3 class="mb-3">{{ formset.title }} </h3>
                <hr class="my-2">
                <div class="row justify-content-center px-3">
                    {% if formset.display.value == 'table' %}
                        {% include 'components/forms/table-formset.html' with formset=formset.form %}
                    {% else %}
                        {% include 'components/forms/list-formset.html' with formset=formset.form %}
                    {% endif %}
                </div>
            
            {% endfor %}
        {% endif %}
        
        <div class="row justify-content-center">
            <div class="col col-auto mb-2">
                <div class="hstack gap-2 justify-content-end d-print-none mt-4 mt-md-0">
                    {% if cancel_button %}
                        {% component cancel_button %}
                    {% endif %}
                    
                    {% if submit_button %}
                        {% component submit_button %}
                    {% endif %}
                </div>
            </div>
        </div>
        
    </form>
    '''