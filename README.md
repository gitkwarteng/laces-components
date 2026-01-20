# Django Components

Reusable Django components for building web applications with ViewSets, Forms, Tables, and Pages.

## Installation

```bash
pip install -e .
```

## Quick Start

1. Add to your Django `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... other apps
    'components',
]
```

2. Create a simple ViewSet:
```python
from django.db import models
from components.viewset import ModelViewSet

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    published_date = models.DateField()

class BookViewSet(ModelViewSet):
    model = Book
    fields = ['title', 'author', 'isbn', 'published_date']
    template_list = 'books/list.html'
    template_detail = 'books/detail.html'
    template_form = 'books/form.html'
```

3. Add URLs:
```python
from django.urls import path, include
from .views import BookViewSet

urlpatterns = [
    path('books/', include(BookViewSet.as_urls())),
]
```

## Components Overview

### ModelViewSet

A powerful ViewSet-like class for handling CRUD operations with automatic URL generation, form handling, and content negotiation.

#### Basic Usage

```python
from components.viewset import ModelViewSet

class ProductViewSet(ModelViewSet):
    model = Product
    fields = ['name', 'price', 'description', 'category']
    paginate_by = 20
    
    # Optional: Custom form class
    form_class = ProductForm
    
    # Optional: Custom templates
    template_list = 'products/list.html'
    template_detail = 'products/detail.html'
    template_form = 'products/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
```

#### Custom Actions

Add custom actions using the `@action` decorator:

```python
from components.viewset import ModelViewSet, action
from django.http import JsonResponse

class BookViewSet(ModelViewSet):
    model = Book
    
    @action(methods=['post'], detail=True)
    def publish(self, request, pk):
        book = self.get_object(pk)
        book.published = True
        book.save()
        return JsonResponse({'status': 'published'})
    
    @action(methods=['get'], detail=False)
    def bestsellers(self, request):
        books = self.get_queryset().filter(bestseller=True)
        data = [self.serialize(book) for book in books]
        return JsonResponse({'results': data})
```

#### URL Generation

Automatically generates URLs for all CRUD operations:

```python
# In urls.py
from .views import BookViewSet

urlpatterns = [
    path('books/', include(BookViewSet.as_urls(prefix='books', base_name='book'))),
]

# Generated URLs:
# /books/ - List view (GET)
# /books/create/ - Create form (GET) / Create action (POST)
# /books/<pk>/ - Detail view (GET)
# /books/<pk>/edit/ - Edit form (GET) / Update action (POST)
# /books/<pk>/delete/ - Delete confirmation (GET) / Delete action (POST)
# /books/<pk>/publish/ - Custom action (if defined)
```

#### Content Negotiation

Supports both HTML and JSON responses automatically:

```python
# HTML request (browser)
GET /books/ → Returns rendered HTML template

# JSON request (API)
GET /books/ 
Headers: Accept: application/json
→ Returns: {"results": [...], "count": 10}

# Create via JSON
POST /books/
Content-Type: application/json
{"title": "New Book", "author": "Author Name"}
→ Returns: {"id": 1, "title": "New Book", "author": "Author Name"}
```

### PageModelViewSet

Extends ModelViewSet with built-in page component rendering:

```python
from components.viewset import PageModelViewSet

class ProductPageViewSet(PageModelViewSet):
    model = Product
    fields = ['name', 'price', 'description']
    title = "Product Management"
    sub_title = "Manage your products"
    
    def get_page_summary_data(self):
        return {
            'Active Products': self.get_queryset().filter(active=True).count(),
            'Total Revenue': self.get_queryset().aggregate(total=Sum('price'))['total']
        }
```

### Form Components

#### FormComponent

Renders Bootstrap-styled forms with automatic field handling:

```python
from components.form import FormComponent, FormButton
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

# In your view
form_component = FormComponent(
    form=ContactForm(),
    method='post',
    action='/contact/',
    submit_button=FormButton(
        text='Send Message',
        button_type='submit',
        classes='btn-primary'
    ),
    cancel_button=FormButton(
        text='Cancel',
        button_type='link',
        url='/'
    )
)
```

#### FormButton

Customizable form buttons:

```python
from components.form import FormButton

# Submit button
submit_btn = FormButton(
    text='Save Changes',
    button_type='submit',
    classes='btn-success btn-lg',
    icon='ri-save-line'
)

# Link button
cancel_btn = FormButton(
    text='Go Back',
    button_type='link',
    url='/dashboard/',
    classes='btn-secondary',
    icon='ri-arrow-left-line'
)
```

### Table Components

#### TableComponent

Powerful data table with pagination, sorting, and editing:

```python
from components.table.table import TableComponent
from components.table.columns import TextColumn, DateColumn, ActionColumn

# Define columns
columns = [
    TextColumn(name='title', header='Book Title'),
    TextColumn(name='author', header='Author'),
    DateColumn(name='published_date', header='Published'),
    ActionColumn(name='actions', header='Actions')
]

# Create table
table = TableComponent(
    data=Book.objects.all(),
    columns=columns,
    model=Book,
    editable=True,
    numbered=True,
    page_size=25
)
```

#### Table Columns

Various column types for different data:

```python
from components.table.columns import (
    TextColumn, DateColumn, NumberColumn, 
    BooleanColumn, ActionColumn, DeleteButtonColumn
)

columns = [
    TextColumn(name='name', header='Product Name', sortable=True),
    NumberColumn(name='price', header='Price', format='${:.2f}'),
    BooleanColumn(name='active', header='Active'),
    DateColumn(name='created_at', header='Created', format='%Y-%m-%d'),
    ActionColumn(name='actions', header='Actions'),
    DeleteButtonColumn(name='delete', header='')
]
```

### Page Components

#### Page Structure

Build complete pages with consistent layout:

```python
from components.page import Page, Heading, Breadcrumb, ListPageBody
from components.card import SummaryCardList, SummaryCard

# Create breadcrumbs
breadcrumbs = [
    Breadcrumb(title='Dashboard', url='/dashboard/'),
    Breadcrumb(title='Products', url='', active=True)
]

# Create heading
heading = Heading(
    title='Product Management',
    breadcrumbs=breadcrumbs
)

# Create summary cards
summary = SummaryCardList(cards=[
    SummaryCard(title='Total Products', value=150),
    SummaryCard(title='Active Products', value=120),
    SummaryCard(title='Revenue', value='$45,230', value_prefix='$')
])

# Create page body
body = ListPageBody(
    title='Products',
    create_url='/products/create/',
    table=table_component,
    summary=summary,
    filter_form=filter_form
)

# Complete page
page = Page(heading=heading, body=body)
```

#### Page Views

Use built-in page views for common patterns:

```python
from components.views import ListPageView, CreateUpdatePageView

class ProductListView(ListPageView):
    model = Product
    title = 'Product Management'
    columns = [
        TextColumn(name='name', header='Name'),
        NumberColumn(name='price', header='Price')
    ]
    
class ProductFormView(CreateUpdatePageView):
    model = Product
    form_class = ProductForm
    title = 'Add Product'
```

### Menu Components

Build navigation menus:

```python
from components.menu import Menu, LevelOneMenuItem, LevelTwoMenuItem, MenuSection

menu_items = [
    MenuSection(title='Main'),
    LevelOneMenuItem(
        label='Dashboard',
        url_name='dashboard',
        icon='ri-dashboard-line'
    ),
    LevelOneMenuItem(
        label='Products',
        icon='ri-product-hunt-line',
        submenus=[
            LevelTwoMenuItem(label='All Products', url_name='product-list'),
            LevelTwoMenuItem(label='Add Product', url_name='product-create'),
            LevelTwoMenuItem(label='Categories', url_name='category-list')
        ]
    )
]

menu = Menu(items=menu_items)
```

### Card Components

Summary and info cards:

```python
from components.card import SummaryCard, SummaryCardList

# Individual card
card = SummaryCard(
    title='Total Sales',
    value=1250,
    value_prefix='$',
    feather_icon='dollar-sign',
    footer='<span class="text-success">+12% from last month</span>'
)

# Card list
cards = SummaryCardList(
    cards=[
        SummaryCard(title='Users', value=1500),
        SummaryCard(title='Orders', value=350),
        SummaryCard(title='Revenue', value=25000, value_prefix='$')
    ],
    card_class='col-xl-4 col-md-6'
)
```

## Mixins

### ComponentViewMixin

Base mixin for component-based views:

```python
from components.mixins import ComponentViewMixin
from django.views.generic import TemplateView

class DashboardView(ComponentViewMixin, TemplateView):
    component_class = Page
    template_name = 'dashboard.html'
    
    def get_component_kwargs(self):
        return {
            'heading': self.get_heading(),
            'body': self.get_body()
        }
```

### TableComponentViewMixin

Adds table functionality to views:

```python
from components.mixins import TableComponentViewMixin

class ProductView(TableComponentViewMixin, ListView):
    model = Product
    columns = [
        TextColumn(name='name', header='Name'),
        NumberColumn(name='price', header='Price')
    ]
    editable = True
    numbered = True
```

### FormComponentViewMixin

Adds form component functionality:

```python
from components.mixins import FormComponentViewMixin

class ContactView(FormComponentViewMixin, FormView):
    form_class = ContactForm
    template_name = 'contact.html'
    
    def get_form_button(self):
        return FormButton(
            text='Send Message',
            button_type='submit',
            classes='btn-primary'
        )
```

## Advanced Usage

### Custom Components

Create your own components by extending base classes:

```python
from components.base import AutoTemplateStringComponent
import dataclasses

@dataclasses.dataclass
class AlertComponent(AutoTemplateStringComponent):
    message: str
    alert_type: str = 'info'
    dismissible: bool = True
    
    template = '''
    <div class="alert alert-{{ alert_type }}{% if dismissible %} alert-dismissible{% endif %}" role="alert">
        {{ message }}
        {% if dismissible %}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        {% endif %}
    </div>
    '''
```

### Filtering and Search

Implement filtering in ViewSets:

```python
class ProductViewSet(ModelViewSet):
    model = Product
    filter_fields = ['category', 'active']
    
    def filter_queryset(self, queryset, form=None):
        queryset = super().filter_queryset(queryset, form)
        
        # Custom filtering logic
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
            
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset
```

### Custom Templates

Override default templates:

```html
<!-- books/list.html -->
{% extends 'base.html' %}
{% load laces %}

{% block content %}
    {% component page %}
{% endblock %}

<!-- books/form.html -->
{% extends 'base.html' %}
{% load laces %}

{% block content %}
    <div class="container">
        {% component form %}
    </div>
{% endblock %}
```

## Configuration

### Settings

Configure default behavior in Django settings:

```python
# settings.py
COMPONENTS = {
    'DEFAULT_PAGE_SIZE': 25,
    'DEFAULT_FORM_CLASSES': 'form needs-validation',
    'DEFAULT_TABLE_CLASSES': 'table table-striped',
    'ENABLE_HTMX': True,
}
```

### Template Tags

Load the laces template tags in your templates:

```html
{% load laces %}

<!-- Render any component -->
{% component my_component %}

<!-- Render with additional context -->
{% component table_component with extra_data=value %}
```

## Examples

### Complete CRUD Example

```python
# models.py
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# forms.py
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'published']

# views.py
class ArticleViewSet(PageModelViewSet):
    model = Article
    form_class = ArticleForm
    title = "Article Management"
    paginate_by = 15
    
    columns = [
        TextColumn(name='title', header='Title'),
        TextColumn(name='author__username', header='Author'),
        BooleanColumn(name='published', header='Published'),
        DateColumn(name='created_at', header='Created')
    ]
    
    @action(methods=['post'], detail=True)
    def toggle_published(self, request, pk):
        article = self.get_object(pk)
        article.published = not article.published
        article.save()
        return JsonResponse({'published': article.published})

# urls.py
urlpatterns = [
    path('articles/', include(ArticleViewSet.as_urls())),
]
```

This creates a complete CRUD interface with list, create, edit, delete, and custom toggle functionality.

## Requirements

- Django >= 3.2
- django-widget-tweaks
- laces (for component rendering)

## License

MIT License
