from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView

from models import Article, Category, SingleImage


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


class HomeView(TemplateView):
    template_name = 'articles/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # get 4 random latest articles of each category
        categories = Category.objects.all()
        cat_latest = []
        sel_articles = []
        for cat in categories:
            try:
                article = cat.get_latest_articles()
                next_a = 1
                while article[0].id in sel_articles:
                    next_a += 1
                    article = cat.get_latest_articles(next_a)[next_a-1:next_a]
                if article[0].id not in sel_articles:
                    sel_articles.append(article[0].id)
                    cat_latest.append((cat.id, cat.slug, cat.name, article))
            except:
                pass

        context['categories_latest'] = cat_latest[:6]

        # get few latest articles
        latest = Article.objects.filter(status__is_live=True)
        context['latest_articles'] = latest.order_by('-publish_date')[:5]

        # get featured  articles
        latest = Article.objects.filter(status__is_live=True, featured=True)
        context['featured_articles'] = latest.order_by('-publish_date')[:5]

        # get few latest images
        latest = SingleImage.objects.order_by('-publish_date')[:2]
        context['latest_images'] = latest

        return context
