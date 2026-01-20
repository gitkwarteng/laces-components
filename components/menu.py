import dataclasses
from typing import List, Optional, Union

from django.urls import reverse

from .base import AutoTemplateStringComponent, TemplateStringComponent


@dataclasses.dataclass
class MenuSection(AutoTemplateStringComponent):
    title: str

    template = '''
    <li class="menu-title"><i class="ri-more-fill"></i> <span data-key="t-pages">{{ title }} </span></li>
    '''

@dataclasses.dataclass
class MenuItem(AutoTemplateStringComponent):
    label: str
    url_name: Optional[str] = None
    icon: Optional[str] = None
    active: bool = False

    template = '''
    <li class="nav-item">
        <a href="{{ url }}" class="nav-link" data-key="t-basic">
            {{ label }}
        </a>
    </li>
    '''

    def get_menu_id(self):
        return self.label.lower().replace(' ', '-')

    def get_url(self):
        if self.url_name:
            return reverse(self.url_name)
        else:
            return '#'

    def get_context_data(self, parent_context=None):
        context = super().get_context_data(parent_context)
        context.update({
            'url': self.get_url(),
            'id': self.get_menu_id(),
        })

        return context


@dataclasses.dataclass
class LevelOneMenuItem(MenuItem):
    badge: Optional[str] = None
    badge_class: Optional[str] = 'badge-pill bg-danger'
    submenus: Optional[List[Union['MenuItem', 'LevelTwoMenuItem']]] = None

    template = '''
    <li class="nav-item">
        <a class="nav-link menu-link" href={{ url }}>
            <i class="{{ icon }}"></i> <span data-key="t-widgets">{{ label }} </span>
            {% if badge %}
                <span class="badge {{ badge_class}}" data-key="t-hot">{{ badge }}</span>
            {% endif %}
        </a>
    </li>
    '''

    submenu_template = '''
    {% load laces %}
    
    <li class="nav-item{% if active %} active{% endif %}">
        <a class="nav-link menu-link" href="#{{ id }}" data-bs-toggle="collapse" role="button"
           aria-expanded="false" aria-controls="{{ id }}">
            <i class="{{ icon }}"></i> <span data-key="t-dashboards">{{ label }}</span>
            {% if badge %}
                <span class="badge {{ badge_class}}" data-key="t-hot">{{ badge }}</span>
            {% endif %}
        </a>
        <div class="collapse menu-dropdown" id="{{ id }}">
            <ul class="nav nav-sm flex-column">
                {% for menu in submenus %}
                    {% component menu with ignore=True only %}
                {% endfor %}
            </ul>
        </div>
    </li>
    '''

    def get_template(self, fragments=None):
        if self.submenus:
            return self.submenu_template
        else:
            return self.template



@dataclasses.dataclass
class LevelTwoMenuItem(LevelOneMenuItem):
    submenus: Optional[List['MenuItem']] = None

    template = '''
    <li class="nav-item">
        <a class="nav-link" href={{ url }}">
            {{ label }}
            {% if badge %}
                <span class="badge {{ badge_class}}" data-key="t-hot">{{ badge }}</span>
            {% endif %}
        </a>
    </li>
    '''

    submenu_template = '''
    {% load laces %}

    <li class="nav-item{% if active %} active{% endif %}">
        <a class="nav-link" href="#{{ id }}" data-bs-toggle="collapse" role="button"
           aria-expanded="false" aria-controls="{{ id }}">
            {{ label }}
            {% if badge %}
                <span class="badge {{ badge_class}}" data-key="t-hot">{{ badge }}</span>
            {% endif %}
        </a>
        <div class="collapse menu-dropdown" id="{{ id }}">
            <ul class="nav nav-sm flex-column">
                {% for menu in submenus %}
                    {% component menu with ignore=True only %}
                {% endfor %}
            </ul>
        </div>
    </li>
    '''


@dataclasses.dataclass
class Menu(AutoTemplateStringComponent):
    items: List[MenuItem] = dataclasses.field(default_factory=list)
    css_class: str = 'menu'

    template = '''
    {% load laces %}
    <nav class="{{ css_class }}">
        <ul class="menu-list">
            {% for item in items %}
                {% component item %}
            {% endfor %}
        </ul>
    </nav>
    '''