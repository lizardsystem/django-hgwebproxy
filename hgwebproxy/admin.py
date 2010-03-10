__docformat__ = "restructedtext"

from django.utils.translation import ugettext as _
from django.contrib import admin
from django import forms

from hgwebproxy.models import Repository

class RepositoryAdminForm(forms.ModelForm):
    """
    TODO: List available themes
    """ 
    class Meta:
        model = Repository

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    prepopulated_fields = {
        'slug': ('name',)
    }
    filter_horizontal = ('readers', 'reader_groups', 'writers', 'writer_groups')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'owner', 'location', 'description')
        }),
        (_('Options'), {
            'classes': ('collapse',),
            'fields': ('style', 'allow_archive', 'is_private'),
        }),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('readers', 'writers', 'reader_groups', 'writer_groups')
        }),
    )
    form = RepositoryAdminForm

admin.site.register(Repository, RepositoryAdmin)
