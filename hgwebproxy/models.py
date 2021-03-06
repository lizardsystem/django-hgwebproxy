import re
import os

from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site

from hgwebproxy.api import create_repository, delete_repository, is_template, \
                            get_last_changeset
from hgwebproxy import settings as hgwebproxy_settings

def validate_slug(value):
    """
    Checks the repository slug
    """
    if not value.isalnum():
        raise ValidationError(_('%s is not a valid name') % value)

def validate_location(value):
    """
    TODO:
    Checks the repository location to make sure it exists and is writable.
    """
    if re.match("[\w\d]+://", value):
        raise ValidationError(_("Remote repository locations are not supported"))

    if not os.path.exists(os.path.join(value, '.hg')):
        if not os.path.exists(value):
            parent_dir = os.path.normpath(os.path.join(value, ".."))
            if not os.path.exists(parent_dir):
                raise ValidationError(_("This path does not exist."))
            perm_check_path = parent_dir
        else:
            perm_check_path = value

        if not os.access(perm_check_path, os.W_OK):
            raise ValidationError(_("You don't have sufficient permissions to create a repository at this path."))

def validate_archive(value):
    """
    TODO: Validate archive declaration to the form "zip, bz2, gz"
    """
    pass

def validate_style(value):
    """
    TODO: Validate style setting, it must be an existing style in mercurial
          and also in the Project
    """
    if not is_template(value):
        raise ValidationError(_("'%s' is not an available style." % value))

class Repository(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True,
        help_text=_('Would be the unique url of the repo. Characters in slug must be alphanumeric with no special symbols or hyphens'))
    owner = models.ForeignKey(User)
    ascendent = models.ForeignKey('self', null=True, related_name='descendents',
        editable=False)
    location = models.CharField(max_length=200,
        help_text=_('The absolute path to the repository. If the repository does not exist it will be created.'))
    description = models.TextField(blank=True)

    allow_archive = models.CharField(max_length=100, blank=True,
        help_text=_("Same as in hgrc config, as: zip, bz2, gz"))
    allow_push_ssl = models.BooleanField(default=False, help_text=_("You must set your webserver to handle secure http connection"))
    is_private = models.BooleanField(default=False,
        help_text=_('Private repositories It can only be seen by the owner and allowed users'))
    style = models.CharField(max_length=256, blank=True, default=hgwebproxy_settings.DEFAULT_STYLE,
        help_text=_('The hgweb style'), )

    readers = models.ManyToManyField(User,
        related_name="repository_readable_set", blank=True, null=True)
    writers = models.ManyToManyField(User,
        related_name="repository_writeable_set", blank=True, null=True)
    reader_groups = models.ManyToManyField(Group,
        related_name="repository_readable_set", blank=True, null=True)
    writer_groups = models.ManyToManyField(Group,
        related_name="repository_writeable_set", blank=True, null=True)

    def __unicode__(self):
        return u"%s's %s" % (self.owner.username, self.name)

    class Meta:
        verbose_name = _('repository')
        verbose_name_plural = _('repositories')
        ordering = ['name', ]

    #TODO: This could be a little bit more ... nicer?
    def can_browse(self, user):
        return user.is_superuser or \
            user == self.owner or \
            not not self.readers.filter(pk=user.id) or \
            not not self.writers.filter(pk=user.id) or \
            not not self.reader_groups.filter(pk__in=[group.id for group in user.groups.all()]) or \
            not not self.writer_groups.filter(pk__in=[group.id for group in user.groups.all()])

    def can_pull(self, user):
        return user.is_superuser or \
            user == self.owner or \
            not not self.readers.filter(pk=user.id) or \
            not not self.writers.filter(pk=user.id) or \
            not not self.reader_groups.filter(pk__in=[group.id for group in user.groups.all()]) or \
            not not self.writer_groups.filter(pk__in=[group.id for group in user.groups.all()])

    def can_push(self, user):
        return user.is_superuser or \
            user == self.owner or \
            not not self.writers.filter(pk=user.id) or \
            not not self.writer_groups.filter(pk__in=[group.id for group in user.groups.all()])

    @permalink
    def get_absolute_url(self):
        return ('repo_detail', (), {
            'username': self.owner.username,
            'pattern': self.slug + "/",
        })

    @property
    def get_clone_url(self):
        current_site = Site.objects.get_current()
        return 'http://%s%s' % (current_site.domain, self.get_absolute_url())

    @property
    def lastchange(self):
        try:
            return get_last_changeset(self.location)['date']
        except: # TODO: Catch specific exceptions here
            pass
        return _(u'n/a')

    def fork(self, new_name):
        # TODO: implement forking
        pass

    def save(self, *args, **kwargs):
        if not self.id:
            create_repository(self.location)
        super(Repository, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.id:
            delete_repository(self.location)
        super(Repository, self).delete(*args, **kwargs)

