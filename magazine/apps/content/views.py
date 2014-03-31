from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from models import Article, Category


class CategoryView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        return super(CategoryView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.model.objects.filter(categories__slug=self.kwargs['category'])
