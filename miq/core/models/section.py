
from django.utils.safestring import mark_safe
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from ..mixins import RendererMixin

from .mixins import BaseModelMixin


class SectionType(models.TextChoices):
    # Text types
    TXT = 'TXT', _('Text')
    MD = 'MD', _('Markdown')

    # Media Types
    IMG = 'IMG', _('Image')
    HGAL = 'HGAL', _('Horizontal gallery')
    VGAL = 'VGAL', _('Vertical gallery')
    SQGRID = 'SQGRID', _('Square grid')

    # Mixed Types
    JUMB = 'JUMB', _('Jumbotron')
    SLIDER = 'SLIDER', _('Slider')

    # Embed
    EMBED = 'EMBED', _('Embed')


RENDERER_TEMPLATES = {
    SectionType.HGAL: 'miq/components/img-gallery-horizontal.html',
    SectionType.TXT: '',
}


class SectionAbstract(BaseModelMixin):
    class Meta:
        abstract = True

    title = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    url = models.URLField(
        null=True, blank=True,
        help_text=_('Call to action or link url'))


# SECTION

class SectionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('images')


class Section(RendererMixin, SectionAbstract):

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        ordering = ('created', 'position')

    def __str__(self):
        return f'{self.pk}-{self.type}'

    # From Abstract: title, text, url

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE,
        related_name='sections')

    # Used to group sections
    source = models.SlugField(
        max_length=100, db_index=True,
        null=True, blank=True)

    type = models.CharField(
        max_length=15, choices=SectionType.choices,
        default=SectionType.TXT
    )

    html = models.TextField(blank=True, null=True)
    nodes = models.JSONField(blank=True, null=True)
    images = models.ManyToManyField(
        'core.Image',
        blank=True,
        through='SectionImage',
        related_name='sections')

    position = models.PositiveIntegerField(default=1)

    objects = SectionManager()

    @property
    def image(self):
        if self.images.exists():
            return self.images.order_by('position').first()

    def render(self):
        # DONOT USE: EXPERIMENTAL CODE

        html = mark_safe(self.html)
        try:
            return self._render(
                RENDERER_TEMPLATES.get(self.type, '<div></div>'),
                context={
                    'section': self, 'images': self.images.all,
                    'type': self.type
                }
            )
        except Exception:
            return html


class SectionImage(SectionAbstract):

    # From Abstract: title, text, url

    section = models.ForeignKey('core.Section', on_delete=models.CASCADE)
    img = models.ForeignKey(
        'core.Image', on_delete=models.CASCADE, related_name='meta')


# PROXIES


class JumbotronSection(Section):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = SectionType.JUMB
        super().save(*args, **kwargs)


class ImageSection(Section):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = SectionType.IMG
        super().save(*args, **kwargs)


class MarkdownSection(Section):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = SectionType.MD
        super().save(*args, **kwargs)


class TextSection(Section):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = SectionType.TXT
        super().save(*args, **kwargs)
