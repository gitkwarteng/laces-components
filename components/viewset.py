from functools import cached_property
from typing import Any

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict, modelform_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import path, reverse
import json

from .views import BaseListPage, BaseFormPage


def action(methods=None, detail=False, url_path=None, url_name=None):
    """
    Decorator to mark a method as a custom action.

    Args:
        methods: List of HTTP methods (e.g., ['get', 'post'])
        detail: Whether this is a detail action (requires pk) or list action
        url_path: Custom URL path (defaults to method name)
        url_name: Custom URL name (defaults to method name)

    Example:
        @action(methods=['get'], detail=True)
        def publish(self, request, pk):
            obj = self.get_object(pk)
            obj.published = True
            obj.save()
            return JsonResponse({'status': 'published'})
    """
    if methods is None:
        methods = ['get']

    def decorator(func):
        func.is_custom_action = True
        func.action_methods = [m.upper() for m in methods]
        func.action_detail = detail
        func.action_url_path = url_path or func.__name__.replace('_', '-')
        func.action_url_name = url_name or func.__name__
        return func

    return decorator


@method_decorator(csrf_exempt, name='dispatch')
class ModelViewSet(View):
    """
    A ViewSet-like class for handling CRUD operations on Django models.
    Supports forms, pagination, context data, and content negotiation.

    Usage:
        class BookViewSet(ModelViewSet):
            model = Book
            fields = ['title', 'author', 'isbn', 'published_date']
            form_class = BookForm  # Optional: custom form
            paginate_by = 10
            template_list = 'books/list.html'
            template_detail = 'books/detail.html'
            template_form = 'books/form.html'

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['custom_data'] = 'value'
                return context
    """

    model = None
    fields = '__all__'
    lookup_field = 'pk'

    # Form configuration
    form_class = None  # Custom form class
    filter_form_class = None  # Custom form class
    filter_fields = '__all__'
    filter_form_method = 'get'
    filter_form_action = ''

    # Pagination
    paginate_by = None  # Number of items per page
    page_kwarg = 'page'

    # Template names
    template_list = None
    template_detail = None
    template_form = None

    # URL naming
    base_name = None

    # Success URLs
    success_url = None

    @classmethod
    def as_urls(cls, prefix='', base_name=None):
        """Generate URL patterns for all CRUD operations."""
        if base_name is None:
            base_name = cls.get_base_name()

        prefix = prefix.strip('/') + '/' if prefix else ''

        urls = [
            path(f'{prefix}', cls.as_view(), name=f'{base_name}-list'),
            path(f'{prefix}create/', cls.as_view(), name=f'{base_name}-create'),
            path(f'{prefix}<int:pk>/', cls.as_view(), name=f'{base_name}-detail'),
            path(f'{prefix}<int:pk>/edit/', cls.as_view(), name=f'{base_name}-edit'),
            path(f'{prefix}<int:pk>/delete/', cls.as_view(), name=f'{base_name}-delete'),
        ]

        # Add custom action URLs
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, 'is_custom_action'):
                url_path = attr.action_url_path
                url_name = f"{base_name}-{attr.action_url_name}"
                if attr.action_detail:
                    urls.append(path(f'{prefix}<int:pk>/{url_path}/', cls.as_view(), name=url_name))
                else:
                    urls.append(path(f'{prefix}{url_path}/', cls.as_view(), name=url_name))

        return urls

    @classmethod
    def get_base_name(cls) -> Any:
        return cls.base_name or cls.model.__name__.lower()

    def accepts_html(self, request):
        """Check if client accepts HTML response."""
        accept = request.META.get('HTTP_ACCEPT', '')
        return 'text/html' in accept or 'application/xhtml+xml' in accept

    def get_form_class(self):
        """Return the form class to use."""
        if self.form_class:
            return self.form_class

        # Auto-generate ModelForm
        fields = self.fields if self.fields != '__all__' else None
        return modelform_factory(self.model, fields=fields)

    def get_form_kwargs(self):
        kwargs = {
            'data': self.request.GET or self.request.POST or None,
        }
        if self.object:
            kwargs['instance'] = self.object

        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form."""
        form_kwargs = self.get_form_kwargs()
        if self.form_class:
            return self.form_class(**form_kwargs)
        # Auto-generate form from model fields
        fields = self.fields if self.fields != '__all__' else None
        form_class = modelform_factory(self.model, fields=fields)
        return form_class(**form_kwargs)

    def get_queryset(self):
        """Return the queryset. Override to add filtering."""
        return self.model.objects.all()

    def filter_queryset(self, queryset=None, form=None):
        """Filter the queryset based on request parameters."""
        # Add any default filtering here
        return queryset

    def get_paginate_by(self):
        """Get the number of items to paginate by."""
        return self.paginate_by

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset."""
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get(self.page_kwarg, 1)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return {
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'object_list': page_obj.object_list,
        }

    def get_context_data(self, **kwargs):
        """
        Get context data for templates.
        Override this method to add custom context for all actions.
        """
        context = {
            'view': self,
            'model_name': self.model.__name__,
            'model_name_plural': f"{self.model.__name__}s",
        }
        context.update(kwargs)
        return context

    def get_list_context_data(self, **kwargs):
        """Get context data specifically for list action."""
        return self.get_context_data(**kwargs)

    def get_detail_context_data(self, **kwargs):
        """Get context data specifically for detail/retrieve action."""
        return self.get_context_data(**kwargs)

    def get_create_context_data(self, **kwargs):
        """Get context data specifically for create action."""
        return self.get_context_data(**kwargs)

    def get_edit_context_data(self, **kwargs):
        """Get context data specifically for edit/update action."""
        return self.get_context_data(**kwargs)

    def get_delete_context_data(self, **kwargs):
        """Get context data specifically for delete action."""
        return self.get_context_data(**kwargs)

    def get_success_url(self, obj=None):
        """Return the URL to redirect to after successful form submission."""
        if self.success_url:
            return self.success_url

        # Try to get detail URL
        base_name = self.get_base_name()
        app_name = self.model._meta.app_label
        try:
            if obj:
                return reverse(f'{app_name}:{base_name}-detail', kwargs={'pk': obj.pk})
            return reverse(f'{app_name}:{base_name}-list')
        except:
            return self.request.path

    def serialize(self, obj):
        """Convert model instance to dictionary."""
        if self.fields == '__all__':
            return model_to_dict(obj)
        return model_to_dict(obj, fields=self.fields)

    def get_request_data(self, request):
        """Extract data from request (JSON or form data)."""
        if request.content_type == 'application/json':
            try:
                return json.loads(request.body)
            except json.JSONDecodeError:
                return None
        return None

    def error_response(self, request, message, status):
        """Return error in appropriate format."""
        if self.accepts_html(request):
            return HttpResponse(f'<h1>Error {status}</h1><p>{message}</p>', status=status)
        return JsonResponse({'error': message}, status=status)

    def render_to_response(self, context, template=None):
        """Unified response rendering method."""
        if template:
            return render(self.request, template, context)
        
        # Determine which render method to use based on context
        if 'object_list' in context:
            template = self.template_list
        elif 'form' in context:
            template = self.template_form
        elif 'object' in context and 'form' not in context:
            if context.get('action') == 'delete':
                template = self.template_delete
            else:
                template = self.template_detail
        else:
            template = self.template_detail
        
        return render(self.request, template, context)

    def get_object(self, pk):
        """Get a single object by pk. Raises ObjectDoesNotExist if not found."""
        self.object = self.get_queryset().get(**{self.lookup_field: pk})
        return self.object

    def get_custom_actions(self):
        """Return list of custom actions defined with @action decorator."""
        actions = []
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if callable(attr) and hasattr(attr, 'is_custom_action'):
                actions.append({
                    'method': getattr(self, attr_name),
                    'methods': attr.action_methods,
                    'detail': attr.action_detail,
                    'url_path': attr.action_url_path,
                    'url_name': attr.action_url_name,
                })
        return actions

    def dispatch(self, request, *args, **kwargs):
        """Route requests to appropriate handler methods."""
        if not self.model:
            return self.error_response(request, 'Model not specified', 500)

        self.request = request
        self.args = args
        self.kwargs = kwargs

        pk = kwargs.get(self.lookup_field)
        path_info = request.path_info

        # Check for custom actions first
        custom_actions = self.get_custom_actions()
        for action_info in custom_actions:
            if action_info['url_path'] in path_info:
                # Check if request method is allowed for this action
                if request.method in action_info['methods']:
                    # Check if it's a detail action that requires pk
                    if action_info['detail'] and not pk:
                        return self.error_response(request, 'ID required for this action', 400)

                    # Call the custom action method
                    if action_info['detail']:
                        return action_info['method'](request, pk)
                    else:
                        return action_info['method'](request)
                else:
                    return self.error_response(request, f"Method {request.method} not allowed", 405)

        # Standard CRUD operations
        if request.method == 'GET':
            if pk:
                if 'edit' in path_info:
                    return self.edit(request, pk)
                elif 'delete' in path_info:
                    return self.delete_confirm(request, pk)
                return self.retrieve(request, pk)
            elif 'create' in path_info:
                return self.create_form(request)
            return self.list(request)
        elif request.method == 'POST':
            if pk:
                if 'delete' in path_info:
                    return self.destroy(request, pk)
                return self.update(request, pk)
            return self.create(request)
        elif request.method == 'PUT':
            if pk:
                return self.update(request, pk)
            return self.error_response(request, 'ID required for update', 400)
        elif request.method == 'PATCH':
            if pk:
                return self.partial_update(request, pk)
            return self.error_response(request, 'ID required for update', 400)
        elif request.method == 'DELETE':
            if pk:
                return self.destroy(request, pk)
            return self.error_response(request, 'ID required for delete', 400)

        return self.error_response(request, 'Method not allowed', 405)

    def list(self, request):
        """GET request without ID - return all objects."""
        queryset = self.get_queryset()
        self.form_class = self.filter_form_class

        form = self.get_form()
        queryset = self.filter_queryset(queryset, form)
        context = {}

        # Handle pagination
        paginate_by = self.get_paginate_by()
        if paginate_by:
            pagination_data = self.paginate_queryset(queryset, paginate_by)
            context.update(pagination_data)
            objects = pagination_data['object_list']
        else:
            context['object_list'] = queryset
            objects = queryset

        # Get action-specific context
        context = self.get_list_context_data(**context)

        if self.accepts_html(request):
            return self.render_to_response(context, self.template_list)

        # JSON response
        data = [self.serialize(obj) for obj in objects]
        response = {'results': data, 'count': queryset.count()}

        if paginate_by:
            response['page'] = context['page_obj'].number
            response['total_pages'] = context['paginator'].num_pages

        return JsonResponse(response, safe=False)

    def retrieve(self, request, pk):
        """GET request with ID - return single object."""
        try:
            obj = self.get_object(pk)
            context = self.get_detail_context_data(object=obj)

            if self.accepts_html(request):
                return self.render_to_response(context, self.template_detail)

            return JsonResponse(self.serialize(obj))
        except ObjectDoesNotExist:
            return self.error_response(request, 'Object not found', 404)

    def create_form(self, request):
        """Show create form (HTML only)."""
        form = self.get_form()
        context = self.get_create_context_data(form=form, action='create')
        return self.render_to_response(context, self.template_form)

    def create(self, request):
        """POST request - create new object."""
        json_data = self.get_request_data(request)

        if json_data:
            try:
                if self.fields != '__all__':
                    json_data = {k: v for k, v in json_data.items() if k in self.fields}
                obj = self.model.objects.create(**json_data)
                return JsonResponse(self.serialize(obj), status=201)
            except Exception as e:
                return self.error_response(request, str(e), 400)
        else:
            form = self.get_form()
            if form.is_valid():
                obj = form.save()
                if self.accepts_html(request):
                    return redirect(self.get_success_url(obj))
                return JsonResponse(self.serialize(obj), status=201)
            else:
                if self.accepts_html(request):
                    context = self.get_create_context_data(form=form, action='create')
                    return self.render_to_response(context, self.template_form)
                return JsonResponse({'errors': form.errors}, status=400)

    def edit(self, request, pk):
        """Show edit form (HTML only)."""
        try:
            obj = self.get_object(pk)
            form = self.get_form()
            context = self.get_edit_context_data(form=form, object=obj, action='edit')
            return self.render_to_response(context, self.template_form)
        except ObjectDoesNotExist:
            return self.error_response(request, 'Object not found', 404)

    def update(self, request, pk):
        """PUT/POST request - update object."""
        try:
            obj = self.get_object(pk)
        except ObjectDoesNotExist:
            return self.error_response(request, 'Object not found', 404)

        json_data = self.get_request_data(request)

        if json_data:
            try:
                if self.fields != '__all__':
                    json_data = {k: v for k, v in json_data.items() if k in self.fields}
                for key, value in json_data.items():
                    setattr(obj, key, value)
                obj.save()
                return JsonResponse(self.serialize(obj))
            except Exception as e:
                return self.error_response(request, str(e), 400)
        else:
            form = self.get_form()
            if form.is_valid():
                obj = form.save()
                if self.accepts_html(request):
                    return redirect(self.get_success_url(obj))
                return JsonResponse(self.serialize(obj))
            else:
                if self.accepts_html(request):
                    context = self.get_edit_context_data(form=form, object=obj, action='edit')
                    return self.render_to_response(context, self.template_form)
                return JsonResponse({'errors': form.errors}, status=400)

    def partial_update(self, request, pk):
        """PATCH request - partial update."""
        return self.update(request, pk)

    def delete_confirm(self, request, pk):
        """Show delete confirmation (HTML only)."""
        try:
            obj = self.get_object(pk)
            context = self.get_delete_context_data(object=obj, action='delete')
            return self.render_to_response(context)
        except ObjectDoesNotExist:
            return self.error_response(request, 'Object not found', 404)

    def destroy(self, request, pk):
        """DELETE request - delete object."""
        try:
            obj = self.get_object(pk)
            obj.delete()

            if self.accepts_html(request):
                base_name = self.base_name or self.model.__name__.lower()
                try:
                    return redirect(reverse(f'{base_name}-list'))
                except:
                    return HttpResponse('<h1>Success</h1><p>Object deleted successfully</p>')

            return HttpResponse(status=204)
        except ObjectDoesNotExist:
            return self.error_response(request, 'Object not found', 404)


class PageModelViewSet(BaseListPage, BaseFormPage, ModelViewSet):
    """
    ModelViewSet with Page component rendering support.
    Combines ModelViewSet with ListPageView and CreateUpdatePageView features.
    Conforms to ComponentViewMixin, TableComponentViewMixin, and FormComponentViewMixin.
    """

    form_element_class = 'form-inline'

    show_field_labels = True

    form_class = None

    def get_form_class(self):
        """Return the form class to use."""
        if self.form_class:
            return self.form_class

        # Auto-generate ModelForm
        fields = self.fields if self.fields != '__all__' else None
        return modelform_factory(self.model, fields=fields)

    def get_form_kwargs(self):
        kwargs = {
            'data': self.request.GET or self.request.POST or None,
        }
        if self.object:
            kwargs['instance'] = self.object

        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form."""
        form_kwargs = self.get_form_kwargs()
        if self.form_class:
            return self.form_class(**form_kwargs)
        # Auto-generate form from model fields
        fields = self.fields if self.fields != '__all__' else None
        form_class = modelform_factory(self.model, fields=fields)
        return form_class(**form_kwargs)

    def list(self, request):
        self.show_field_labels = False
        self.form_method = self.filter_form_method
        return  super().list(request)

    def get_page_title(self):
        return self.title or self.model._meta.verbose_name_plural.title()

    def get_page_sub_title(self):
        return self.sub_title or 'Items'

    @cached_property
    def is_form_view(self):
        return self.lookup_field in self.kwargs or 'create' in self.request.path_info or 'edit' in self.request.path_info

    def get_page_breadcrumbs(self):
        breadcrumbs = super(BaseFormPage, self).get_page_breadcrumbs()
        if self.is_form_view:
            breadcrumbs += self.get_form_page_breadcrumbs()
        else:
            breadcrumbs += self.get_list_page_breadcrumbs()
        
        return breadcrumbs

    def get_page_body(self):
        
        if self.is_form_view:
            return self.get_form_page_body()
        else:
            return self.get_list_page_body()

    def get_form_action(self):
        return self.form_action if self.is_form_view else self.filter_form_action

    def get_form_button(self):
        if self.is_form_view:
            return self.get_submit_form_button()
        else:
            return self.get_filter_form_button()

    def get_cancel_button(self):
        if self.is_form_view:
            return super(BaseListPage, self).get_cancel_button()
        return None