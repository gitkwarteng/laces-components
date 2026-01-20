import dataclasses
from typing import List, Optional

from .base import AutoTemplateStringComponent


@dataclasses.dataclass
class SummaryCard(AutoTemplateStringComponent):
    title: str
    url: Optional[str] = None
    value: Optional[str | int] = ''
    value_prefix: Optional[str] = ''
    value_suffix: Optional[str] = ''
    footer: Optional[str] = '''
    <span class="badge bg-warning me-1">2,258</span> <span class="text-muted">Total</span>
    '''
    feather_icon: Optional[str] = 'file-text'
    icon_class: Optional[str] = 'text-success icon-dual-success'

    template = '''
    <div class="card card-animate rounded">
        <div class="card-body">
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">
                    <p class="text-uppercase fw-medium text-muted mb-0">{{ title }} </p>
                </div>
                <div class="flex-shrink-0">
                    <h5 class="text-success fs-14 mb-0">
                        <i class="ri-arrow-right-up-line fs-13 align-middle"></i> +89.24 %
                    </h5>
                </div>
            </div>
            <div class="d-flex align-items-end justify-content-between mt-4">
                <div>
                    <h4 class="fs-22 fw-semibold ff-secondary mb-4">
                        {{value_prefix}}<span class="counter-value" data-target="{{value}}">0</span>{{ value_suffix}}
                    </h4>
                    {{ footer|safe }}
                </div>
                <div class="avatar-sm flex-shrink-0">
                    <span class="avatar-title bg-light rounded fs-3">
                        <i data-feather="{{feather_icon}}" class="text-success icon-dual-success"></i>
                    </span>
                </div>
            </div>
        </div>
    </div>
    '''

@dataclasses.dataclass
class SummaryCardList(AutoTemplateStringComponent):
    cards: List[SummaryCard] = dataclasses.field(default_factory=list)
    card_class: Optional[str] = 'col-xl-3 col-md-6'

    template = '''
    {% load laces %}
    <div class="row">
        {% for card in cards %}
            <div class="{{ card_class }}">
                {% component card with ignore=True %}
            </div>
        {% endfor %}
    </div>
    '''
