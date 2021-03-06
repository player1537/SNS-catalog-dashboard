from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres import fields as pgfields
from django.db import models

class AutoRepr(object):
    def __repr__(self):
        fields = (
            "{}={!r}".format(field.name, getattr(self, field.name))
            for field in self._meta.get_fields()
        )

        return "{}({})".format(
            self.__class__.__name__,
            ', '.join(fields),
        )

    def __str__(self):
        primary_key = next(
            field
            for field in self._meta.get_fields()
            if hasattr(field, 'primary_key') and field.primary_key
        )

        return "{}({}={!r})".format(
            self.__class__.__name__,
            primary_key.name,
            getattr(self, primary_key.name),
        )

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

# Create your models here.

class BaseConfiguration(AutoRepr, models.Model):
    instrument = models.OneToOneField(
        'catalog.Instrument',
        verbose_name='base configuration for instrument',
        help_text='The instrument this configuration is for',
        on_delete=models.CASCADE,
    )

    parameters = pgfields.JSONField(
        'base configuration parameters',
        help_text=('The parameters that every configuration for this instrument'
                   'will start with'),
        default=dict,
    )

class Configuration(AutoRepr, models.Model):
    description = models.CharField(
        'configuration description/title',
        help_text='The description/title of the configuration',
        max_length=1024,
    )

    created_date = models.DateTimeField(
        'configuration creation date',
        help_text='The date this configuration was created',
        auto_now_add=True,
    )

    modified_date = models.DateTimeField(
        'configuration modification date',
        help_text='The date this configuration was last modified',
        auto_now=True,
    )

    parameters = pgfields.JSONField(
        'configuration parameters',
        help_text='The parameters for the configuration',
        default=dict,
    )

    instrument = models.ForeignKey(
        'catalog.Instrument',
        verbose_name='configuration\'s instrument',
        help_text='The instrument this configuration is for',
        on_delete=models.CASCADE,
        related_name='configurations',
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='configuration\'s creator',
        help_text='The user who created this configuration',
        on_delete=models.SET(get_sentinel_user),
        related_name='configurations',
    )

    def save(self, *args, **kwargs):
        base = self.instrument.baseconfiguration
        self.parameters = base.parameters
        super().save(*args, **kwargs)
