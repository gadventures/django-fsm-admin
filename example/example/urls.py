from django.contrib import admin

try:
    from django.conf.urls import patterns, include, url

    admin.autodiscover()

    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'example.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        url(r'^admin/', include(admin.site.urls)),
    )
except ImportError:
    from django.urls import path
    urlpatterns = [
        path('admin/', admin.site.urls)
    ]
