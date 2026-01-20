# Django Components

Reusable Django components for building web applications with ViewSets, Forms, Tables, and Pages.

## Installation

```bash
pip install -e /path/to/laces-components
```

Or from the gps-welfare project root:

```bash
pip install -e laces-components
```

## Usage

```python
from components.viewset import ModelViewSet, PageModelViewSet
from components.mixins import ComponentViewMixin, TableComponentViewMixin
from components.page import ListPage, FormPage
```

## Components

- **ViewSet**: ModelViewSet and PageModelViewSet for CRUD operations
- **Mixins**: ComponentViewMixin, TableComponentViewMixin, FormComponentViewMixin
- **Page Components**: ListPage, FormPage, Page
- **Form Components**: FormComponent, FormButton
- **Table Components**: TableComponent, BaseColumn
- **Card Components**: SummaryCard, SummaryCardList
