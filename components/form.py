import dataclasses
from typing import Optional

from django.forms import Form as DjangoForm

from .base import AutoTemplateStringComponent


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
    action:str = ''
    method:str = 'get'
    form_id:str = None
    form_class:str = 'form'
    field_size: str = 'col-md-6 col-12'
    show_field_labels:bool = True

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
        <div class="row justify-content-center">
            {% for field in form %}
                <div class="mb-md-2 mb-3 {{ field_size }}">
                    {% if show_field_labels %}
                        <label for="{{ field.id_for_label }}" class="form-label">{{ field.label }}</label>
                    {% endif %}
                    {% if field.field.widget.input_type == 'textarea' %}
                        <textarea name="{{ field.name }}" id="{{ field.id_for_label }}" class="form-control w-100 {% if field.errors %}is-invalid{% endif %}" rows="3">{{ field.value|default:'' }}</textarea>
                    {% elif field.field.widget.input_type == 'checkbox' %}
                    <div class="form-check">
                        <input type="checkbox" name="{{ field.name }}" id="{{ field.id_for_label }}" class="form-check-input {% if field.errors %}is-invalid{% endif %}" {% if field.value %}checked{% endif %}>
                    </div>
                    {% elif field.field.widget.input_type == 'select' %}
                        {% render_field field class+="form-select w-100" placeholder=field.label %}
                    {% else %}
                        {% render_field field class+="form-control w-100" placeholder=field.label %}
                    {% endif %}
                    {% if field.errors %}
                        <div class="invalid-feedback">{{ field.errors.0 }}</div>
                    {% endif %}
                    {% if field.help_text %}
                        <small class="form-text text-muted">{{ field.help_text }}</small>
                    {% endif %}
                </div>
            {% endfor %}
            
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