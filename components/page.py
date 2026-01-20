import dataclasses
from typing import List, Optional

from .base import AutoTemplateStringComponent, TemplateStringComponent
from .card import SummaryCardList
from .form import FormComponent

@dataclasses.dataclass
class Breadcrumb(AutoTemplateStringComponent):
    title: str
    url: str
    active: bool = False

    template = '''
        {% if active %}
            <li class="breadcrumb-item active">{{ title }}</li>
        {% else %}
            <li class="breadcrumb-item"><a href="{{url}}">{{ title }}</a></li>
        {% endif %}
    '''


@dataclasses.dataclass
class Heading(AutoTemplateStringComponent):
    title:str
    breadcrumbs: List[Breadcrumb] = dataclasses.field(default_factory=list)

    template = '''
    {% load laces %}
    <div class="row">
        <div class="col-12">
            <div class="page-title-box d-sm-flex align-items-center justify-content-between bg-galaxy-transparent">
                <h4 class="mb-sm-0">{{title}}</h4>
                <div class="page-title-right">
                    <ol class="breadcrumb m-0">
                        {% for item in breadcrumbs %}
                            {% component item %}
                        {% endfor %}
                    </ol>
                </div>

            </div>
        </div>
    </div>
    '''

@dataclasses.dataclass
class Page(AutoTemplateStringComponent):
    heading: Heading
    body: TemplateStringComponent

    template = '''
    {% load laces %}
    
    {% component heading %}
    
    {% component body %}

    '''


@dataclasses.dataclass
class ListPageBody(AutoTemplateStringComponent):
    title: str
    create_url: str = ''
    table: Optional[TemplateStringComponent] = None
    summary: Optional[SummaryCardList] = None
    filter_form: Optional[FormComponent] = None

    template = '''
    {% load laces %}
    
    {% if summary %} 
        {% component summary %}
    {% endif %}
        
    <div class="row">
        <div class="col-lg-12">
            <div class="card" id="itemList">

                <div class="card-header border-0">
                    <div class="d-flex align-items-center">
                        <h5 class="card-title mb-0 flex-grow-1">{{ title }}</h5>
                        <div class="flex-shrink-0">
                            <div class="d-flex gap-2 flex-wrap">
                                <button class="btn btn-primary" id="remove-actions"
                                        onClick="deleteMultiple()"><i class="ri-delete-bin-2-line"></i>
                                </button>
                                <a href="{{ create_url }}" class="btn btn-danger"><i
                                        class="ri-add-line align-bottom me-1"></i> Create {{ title }}</a>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card-body bg-light-subtle border border-dashed border-start-0 border-end-0">
                    {% if filter_form %}
                        {% component filter_form %}
                    {% endif %}
                </div>
                
                <div class="card-body">
                    <div>
                        <div class="table-responsive table-card">
                            {% if table %} 
                                {% component table %}
                            {% endif %}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

    '''


@dataclasses.dataclass
class ListPage(Page):
    body: ListPageBody = None


@dataclasses.dataclass
class FormPageBody(AutoTemplateStringComponent):
    form: FormComponent

    template = '''
    {% load laces %}
    <div class="row justify-content-center">
        <div class="col-xxl-9">
            <div class="card">
                <div class="card-body">
                    {% if form %} 
                        {% component form %}
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    '''


@dataclasses.dataclass
class FormPage(Page):
    body: FormPageBody = None
