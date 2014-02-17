from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('articles.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots\.txt$', RedirectView.as_view(url='/static/robots.txt')),
    url(r'^sitemaps\.xml$', RedirectView.as_view(url='/static/sitemaps.xml')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


"""
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from articles.models import Article 
info_dict = {
    'queryset': Article.objects.filter(status_id=2),
    'date_field': 'publish_date',
}
sitemaps = {
    #'flatpages': FlatPageSitemap,
    'blog': GenericSitemap(info_dict, priority=0.6),
}
urlpatterns += patterns('',
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', 
        {'sitemaps': sitemaps})
)
"""
