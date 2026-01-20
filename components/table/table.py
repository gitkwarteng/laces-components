import dataclasses
from typing import Optional, Any, List, Dict

from django.core.paginator import Paginator
from django.db.models import QuerySet, Model

from ..enums import UpdateAction
from ..exceptions import CommonException
from ..base import TemplateStringComponent
from .columns import DeleteButtonColumn, AddRowButtonColumn, BaseColumn



@dataclasses.dataclass(frozen=False)
class TableComponent(TemplateStringComponent):
    data: Any
    columns: List[BaseColumn]
    model: Optional[Model] = None
    editable: bool = False
    class_names = 'table border-translucent table-striped align-middle table-nowrap'
    numbered:bool = False

    pk_field:str = 'pk'
    page_field: str = 'page'

    page_size: int = 25

    template:str = '''
        {% load laces i18n %}

        <table class="{{ class_names }}" data-csrf="{{ csrf_token }}">
                
            <thead>
            <tr>
                {% if numbered %}
                    <th class="text-left" data-sort="id" scope="col" >
                        SN
                    </th>
                {% endif %}
                {% for col in columns %}
                    <th class="text-{{ col.align|default:'left' }} {% if col.sortable %}sort{% endif %}" data-sort="{{ col.name }}" scope="col" >
                        <a href="#">{{ col.header|default:''|upper }}</a>
                    </th>
                {% endfor %}
            </tr>
            </thead>
                
            
            <tbody class="list" id="list-table-body">
                {% if editable %}
                    {% if editable and add_column %}
                        <tr class="new-row">
                            {% component add_column with row=row %}
                        </tr>
                    {% endif %}
                {% endif %}
                
                {% for row in rows %}
                    <tr class="{% if editable %}hover-actions-trigger btn-reveal-trigger position-static {% endif %}" id="row-{{ row.id }}">
                        {% if numbered %}
                        <td><h6 class="align-middle row-number">{{ forloop.counter }}</h6></td>
                        {% endif %}
                        {% for column in columns %}
                            {% component column with row=row %}
                        {% endfor %}
                        {% if editable and delete_column %}
                            {% component delete_column with row=row %}
                        {% endif %}
                    </tr>
                {% endfor %}
                
                {basket_total}
               
            </tbody>
        </table>
            
        {table_pagination}
    '''

    header_template: str = '''
        <thead>
            <tr>
                {% if numbered %}
                    <th class="text-left" data-sort="id" scope="col" >
                        SN
                    </th>
                {% endif %}
                {% for col in columns %}
                    <th class="text-{{ col.align|default:'left' }} {% if col.sortable %}sort{% endif %}" data-sort="{{ col.name }}" scope="col" >
                        <a href="#">{{ col.header|default:''|upper }}</a>
                    </th>
                {% endfor %}
            </tr>
        </thead>
    '''

    rows_template: str = '''
        {% load laces %}
        {% if editable %}
            {% if editable and add_column %}
                <tr>{% component add_column with row=row %}</tr>
            {% endif %}
        {% endif %}
        {% for row in rows %}
            <tr class="{% if editable %}hover-actions-trigger btn-reveal-trigger position-static{% endif %}" id="row-{{ row.id }}">
                {% if numbered %}
                    <td><h6 class="align-middle row-number">{{ forloop.counter }}</h6></td>
                {% endif %}
                {% for column in columns %}
                    {% component column with row=row %}
                {% endfor %}
                {% if editable and delete_column %}
                    {% component delete_column with row=row %}
                {% endif %}
            </tr>
        {% endfor %}
    '''

    row_template: str = '''
        {% load laces %}
        
        <tr id="row-{% if updated %}{{row.id}}{% else %}{{row.id}}{% endif %}" 
        class="{% if editable %}hover-actions-trigger btn-reveal-trigger position-static{% endif %}"
        {% if updated %}hx-swap-oob="true"{% endif %} >
            {% if numbered %}
                <td><h6 class="align-middle row-number">{{ counter }}</h6></td>
            {% endif %}
            {% for column in columns %}
                {% component column with row=row %}
            {% endfor %}
            {% if editable and delete_column %}
                {% component delete_column with row=row %}
            {% endif %}
        </tr>
    '''

    total_template = ''

    pagination_template = ''

    # pagination_template = '''
    #     {% load django_tables2 %}
    #     {% if page and paginator.num_pages > 1 %}
    #         <nav aria-label="Table navigation" class="py-3">
    #             <ul class="pagination justify-content-center">
    #                 {% if page.has_previous %}
    #                     {% block pagination.previous %}
    #                         <li class="previous page-item">
    #                             <a href="#" hx-get="{% querystring page_field=page.previous_page_number without "w" %}"
    #                                     {% include 'phoenix/include/htmx_attrs.html' %} class="page-link">
    #                                 <span aria-hidden="true"><i class="fa fa-chevron-left fs-9"></i></span>
    #                             </a>
    #                         </li>
    #                     {% endblock pagination.previous %}
    #                 {% endif %}
    #                 {% if page.has_previous or page.has_next %}
    #                     {% block pagination.range %}
    #                         {% for p in page|table_page_range:paginator %}
    #                             <li class="page-item{% if page.number == p %} active{% endif %}">
    #                                 <a class="page-link" {% if p != '...' %}href="#"
    #                                    hx-get="{% querystring page_field=p without "w" %}"{% endif %}
    #                                         {% include 'phoenix/include/htmx_attrs.html' %} >
    #                                     {{ p }}
    #                                 </a>
    #                             </li>
    #                         {% endfor %}
    #                     {% endblock pagination.range %}
    #                 {% endif %}
    #                 {% if page.has_next %}
    #                     {% block pagination.next %}
    #                         <li class="next page-item">
    #                             <a href="#" hx-get="{% querystring page_field=page.next_page_number without "w" %}"
    #                                     {% include 'phoenix/include/htmx_attrs.html' %} class="page-link">
    #                                 <span aria-hidden="true"><i class="fa fa-chevron-right fs-9"></i></span>
    #                             </a>
    #                         </li>
    #                     {% endblock pagination.next %}
    #                 {% endif %}
    #             </ul>
    #         </nav>
    #     {% endif %}
    # '''

    def get_model(self):
        if self.model:
            return self.model
        elif isinstance(self.data, QuerySet):
            return self.data.model
        return None

    def paginate(self, paginator_class=Paginator, per_page=None, page=1, *args, **kwargs):
        """
        Paginates the table using a paginator and creates a ``page`` property
        containing information for the current page.

        Arguments:
            paginator_class (`~django.core.paginator.Paginator`): A paginator class to
                paginate the results.

            per_page (int): Number of records to display on each page.
            page (int): Page to display.

        Extra arguments are passed to the paginator.

        Pagination exceptions (`~django.core.paginator.EmptyPage` and
        `~django.core.paginator.PageNotAnInteger`) may be raised from this
        method and should be handled by the caller.
        """

        per_page = per_page or self.page_size
        self.paginator = paginator_class(self.data, per_page, *args, **kwargs)
        self.page = self.paginator.page(page)

        return self

    def get_page(self, request):
        return request.GET.get('page', 1)

    def get_columns(self):
        if not self.columns:
            raise ValueError("Columns are required")

        base_columns = self.columns

        return base_columns

    def get_context_data(self, parent_context=None):
        request = parent_context.get('request')
        self.paginate(page=self.get_page(request))

        delete_column = None
        add_column = None
        if self.editable:
            delete_column = DeleteButtonColumn(key='id', editable=False, sortable=False)
            add_column = AddRowButtonColumn(key='id', editable=False, sortable=False)

        return {
            "columns": self.get_columns(),
            "rows": self.data,
            "editable": self.editable,
            "class_names": self.class_names,
            "numbered": self.numbered,
            "delete_column": delete_column,
            "add_column": add_column,
            "page": self.page,
            "paginator": self.paginator,
            "page_field": self.page_field,
        }

    def get_template(self, fragments=''):

        templates = {
            '':self.template,
            'header': self.header_template,
            'rows': self.rows_template,
            'row': self.row_template,
            'total': self.total_template,
            'pagination': self.pagination_template,
        }
        if not fragments:
            return self.template.replace('{basket_total}', self.total_template).replace('{table_pagination}', self.pagination_template)

        return "\n".join([templates.get(fragment, '') for fragment in fragments.split(',')])

    def get_row(self, row_id):
        return self.model.objects.get(**{self.pk_field:row_id})

    def add_row(self, data, **kwargs):
        return self.model.objects.create(**data)

    def delete_row(self, row_id):
        self.model.objects.filter(**{self.pk_field:row_id}).delete()
        return ''

    def update_field(self, *, row_id, field, value, column, data=None, **kwargs):
        obj = self.get_row(row_id)
        obj.update(**{field: value})
        return obj


    def update_row(self, *, row_id, data, **kwargs):
        obj = self.get_row(row_id)
        obj.update(**data)
        return obj

    def get_column(self, name):
        return filter(lambda c: c.name == name, self.columns)

    def _delete_action(self, request, row_id):

        fragments = 'total' if self.total_template else ''

        try:
            self.delete_row(
                row_id=row_id
            )

            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragments
                }
            ), None
        except (ValueError, CommonException) as ex:
            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragments
                }
            ), ex.__str__()

    def _cell_action(self, request, row_id, field, **kwargs):

        if not field:
            raise ValueError("Field is required")

        # Get column by field name
        column = self.get_column(field)

        try:
            value = column.get_value_from_data(row_id, request.POST)

            obj = self.update_field(
                row_id=row_id, field=column.key, value=value,
                column=column, data=request.POST, **kwargs
            )

            return column.render_html(
                parent_context={
                    'request': request,
                    'row': obj,
                    'render_mode': 'partial'
                }
            ), None

        except (ValueError, CommonException) as ex:
            return column.render_html(
                parent_context={
                    'request': request,
                    'row': self.get_row(row_id),
                    'render_mode': 'partial'
                }
            ), ex.__str__()

    def _row_action(self, request, row_id, **kwargs):
        fragments = 'row,total' if self.total_template else 'row'

        try:
            obj = self.update_row(
                row_id=row_id, data=request.POST,
                **kwargs
            )

            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragments,
                    'row': obj,
                    'updated': True
                }
            ), None
        except (ValueError, CommonException) as ex:
            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragments,
                    'row': self.get_row(row_id),
                    'updated': True
                }
            ), ex.__str__()

    def _add_action(self, request, **kwargs):
        fragments = 'row,total' if self.total_template else 'row'

        try:
            obj, created = self.add_row(data=request.POST, **kwargs)

            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragments,
                    'row': obj,
                    'updated': not created
                }
            ), None
        except (ValueError, CommonException) as ex:
            return "", ex.__str__()

    def _basket_action(self, request, table, **kwargs):
        fragment = request.POST.get('fragment', '')

        try:
            table.update_basket(data=request.POST, **kwargs)

            self.basket.refresh_from_db()

            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragment,
                    'updated': True
                }
            ), None
        except (ValueError, CommonException) as ex:
            return self.render_html(
                parent_context={
                    'request': request,
                    'fragments': fragment,
                    'updated': False
                }
            ), ex.__str__()

    def update(self, request, **kwargs):
        action = UpdateAction(request.POST.get('action', ''))
        row_id = request.POST.get('id', '')
        field = request.POST.get('field', '')

        if action.is_delete:
            return self._delete_action(request=request, row_id=row_id)
        elif action.is_cell:
            return self._cell_action(request=request, row_id=row_id, field=field, **kwargs)
        elif action.is_row:
            return self._row_action(request=request,row_id=row_id, **kwargs)
        elif action.is_add:
            return self._add_action(request=request, **kwargs)
        elif action.is_basket:
            return self._basket_action(request=request, **kwargs)
        else:
            raise ValueError(f"Action {action} not found")
