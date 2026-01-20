from django.urls import reverse
from django.views.generic import ListView, UpdateView

from .card import SummaryCardList, SummaryCard
from .form import FormButton
from .mixins import ComponentViewMixin, TableComponentViewMixin, FormComponentViewMixin
from .page import ListPage, Page, FormPage, Heading, Breadcrumb, ListPageBody, FormPageBody


class PageView(ComponentViewMixin):
    component_class = Page
    component_name = 'page'
    title = None
    sub_title = None

    def get_page_title(self):
        return self.title or self.model._meta.verbose_name_plural.title()

    def get_page_sub_title(self):
        return self.sub_title or 'Items'

    def get_page_breadcrumbs(self):
        return [
            Breadcrumb(
                title="Dashboard",
                url=reverse('core:home'),
                active=False
            )
        ]

    def get_page_heading(self):
        return Heading(
            title=self.get_page_title(),
            breadcrumbs=self.get_page_breadcrumbs()
        )

    def get_page_body(self):
        return []

    def get_component_kwargs(self):
        return {
            'heading':self.get_page_heading(),
            'body':self.get_page_body()
        }


class BaseListPage(PageView, TableComponentViewMixin, FormComponentViewMixin):
    component_class = ListPage
    form_element_class = 'form-inline'

    form_class = None
    show_field_labels = False

    def get_page_title(self):
        return self.title or f'{self.model._meta.verbose_name_plural.title()} List'

    def get_page_breadcrumbs(self):
        breadcrumbs = super().get_page_breadcrumbs()
        return breadcrumbs+ self.get_list_page_breadcrumbs()

    def get_list_page_breadcrumbs(self) -> list[Breadcrumb]:
        return [
            Breadcrumb(
                title=self.get_page_title(),
                url='',
                active=True
            )
        ]

    def get_page_summary_data(self):
        """Override in sub classes to provide summary data."""
        return {}

    def get_page_summary(self):
        cards = [
            SummaryCard(
                title='Total',
                value=self.get_queryset().count()
            )
        ]

        for key, value in self.get_page_summary_data().items():
            cards.append(
                SummaryCard(
                    title=key,
                    value=value
                )
            )

        return SummaryCardList(
            cards=cards
        )

    def get_page_table_data(self):
        if self.request.method == 'POST':
            return []

        if not hasattr(self, 'object_list'):
            self.object_list = self.get_queryset()

        return self.object_list

    def get_page_table(self):
        return self.get_table_component()

    def get_page_body(self):
        return self.get_list_page_body()

    def get_list_page_body(self) -> ListPageBody:
        return ListPageBody(
            title=self.get_page_sub_title(),
            create_url=reverse(f'{self.model._meta.app_label}:{self.model._meta.model_name}-create'),
            table=self.get_table_component(),
            summary=self.get_page_summary(),
            filter_form=self.get_filter_form()
        )

    def get_filter_form(self):
        return self.get_form_component()

    def get_form_kwargs(self):
        kwargs = {
            'data': self.request.GET,
        }
        return kwargs

    def get_cancel_button(self):
        return None

    def get_form_button(self):
        return self.get_filter_form_button()

    def get_filter_form_button(self):
        return FormButton(
            text='Search',
            button_type='submit',
            classes='btn btn-primary',
            icon='ri-search-line'
        )


class ListPageView(BaseListPage, ListView):
    pass


class BaseFormPage(PageView, FormComponentViewMixin):
    component_class = FormPage

    creating = False
    object = None
    form_method: str = 'post'

    def get_object(self, queryset=None):
        """
        This parts allows generic.UpdateView to handle creating objects as
        well. The only distinction between an UpdateView and a CreateView
        is that self.object is None. We emulate this behavior.

        """
        self.creating = 'pk' not in self.kwargs

        if self.object:
            return self.object

        return None if self.creating else super().get_object(queryset)

    def get_page_title(self):
        return self.title or f'Add {self.model._meta.verbose_name.title()}'


    def get_page_breadcrumbs(self):
        breadcrumbs = super().get_page_breadcrumbs()
        return breadcrumbs + self.get_form_page_breadcrumbs()

    def get_form_page_breadcrumbs(self) -> list[Breadcrumb]:
        return [
            Breadcrumb(
                title=self.model._meta.verbose_name.title(),
                url=reverse(f'{self.model._meta.app_label}:{self.model.url_base_name}-list'),
                active=False
            ),
            Breadcrumb(
                title=self.get_page_title(),
                url='',
                active=True
            )
        ]

    def get_page_body(self):
        return self.get_form_page_body()

    def get_form_page_body(self) -> FormPageBody:
        return FormPageBody(
            form=self.get_form_component()
        )

    def get_form_button(self):
        return self.get_submit_form_button()

    def get_submit_form_button(self):
        return FormButton(text='Save', button_type='submit', classes='btn-lg btn-success mt-3')


class CreateUpdatePageView(BaseFormPage, UpdateView):
    pass