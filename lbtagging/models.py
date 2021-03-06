import django
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models, IntegrityError, transaction
from django.template.defaultfilters import slugify as default_slugify
from django.utils.translation import ugettext_lazy as _, ugettext

import urllib

class TagBase(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), unique=True, max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = self.slugify(self.name)
            if django.VERSION >= (1, 2):
                from django.db import router
                using = kwargs.get("using") or router.db_for_write(
                    type(self), instance=self)
                # Make sure we write to the same db for all attempted writes,
                # with a multi-master setup, theoretically we could try to
                # write and rollback on different DBs
                kwargs["using"] = using
                trans_kwargs = {"using": using}
            else:
                trans_kwargs = {}
            i = 0
            while True:
                i += 1
                try:
                    sid = transaction.savepoint(**trans_kwargs)
                    res = super(TagBase, self).save(*args, **kwargs)
                    transaction.savepoint_commit(sid, **trans_kwargs)
                    return res
                except IntegrityError:
                    transaction.savepoint_rollback(sid, **trans_kwargs)
                    self.slug = self.slugify(self.name, i)
        else:
            return super(TagBase, self).save(*args, **kwargs)

    def slugify(self, tag, i=None):
        #slug = default_slugify(tag)
        #slug = urllib.unquote(tag.encode('utf-8'))
        slug = tag
        if i is not None:
            slug += "_%d" % i
        return slug

class Tag(TagBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class ItemBase(models.Model):

    def __unicode__(self):
        return ugettext("%(object)s tagged with %(tag)s") % {
            "object": self.content_object,
            "tag": self.tag
        }

    class Meta:
        abstract = True

    @classmethod
    def tag_model(cls):
        return cls._meta.get_field_by_name("tag")[0].rel.to

    @classmethod
    def tag_relname(cls):
        return cls._meta.get_field_by_name('tag')[0].rel.related_name

    @classmethod
    def lookup_kwargs(cls, instance):
        return {
            'content_object': instance
        }

    @classmethod
    def bulk_lookup_kwargs(cls, instances):
        return {
            "content_object__in": instances,
        }


class TaggedItemBase(ItemBase):
    if django.VERSION < (1, 2):
        tag = models.ForeignKey(Tag, related_name="%(class)s_items")
    else:
        tag = models.ForeignKey(Tag, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        abstract = True

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class GenericTaggedItemBase(ItemBase):
    object_id = models.IntegerField(verbose_name=_('Object id'), db_index=True)
    if django.VERSION < (1, 2):
        content_type = models.ForeignKey(
            ContentType,
            verbose_name=_('Content type'),
            related_name="%(class)s_tagged_items"
        )
    else:
        content_type = models.ForeignKey(
            ContentType,
            verbose_name=_('Content type'),
            related_name="%(app_label)s_%(class)s_tagged_items"
        )
    content_object = GenericForeignKey()

    class Meta:
        abstract=True

    @classmethod
    def lookup_kwargs(cls, instance):
        return {
            'object_id': instance.pk,
            'content_type': ContentType.objects.get_for_model(instance)
        }

    @classmethod
    def bulk_lookup_kwargs(cls, instances):
        # TODO: instances[0], can we assume there are instances.
        return {
            "object_id__in": [instance.pk for instance in instances],
            "content_type": ContentType.objects.get_for_model(instances[0]),
        }

    @classmethod
    def tags_for(cls, model, instance=None):
        ct = ContentType.objects.get_for_model(model)
        kwargs = {
            "%s__content_type" % cls.tag_relname(): ct
        }
        if instance is not None:
            kwargs["%s__object_id" % cls.tag_relname()] = instance.pk
        return cls.tag_model().objects.filter(**kwargs).distinct()


class TaggedItem(GenericTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")

class TagUsedCount(models.Model):
    """
    use SQL to reset recent_count:
    update tb set recent_count = recent_count_bak, recent_count_bak=0
    """
    tag = models.ForeignKey(Tag)
    count = models.IntegerField(verbose_name=_('Used Count'), default=0)
    recent_count = models.IntegerField(verbose_name=_('Recent Used Count'), default=0)
    recent_count_bak = models.IntegerField(verbose_name=_('Recent Used Count'), default=0)
    tagged_table = models.CharField(verbose_name=_('Tagged Table'), max_length=32, blank=True, default='')
    updated_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s|%s|%s" % (self.tag.name, self.tagged_table, self.count)

"""
class TagRelate(models.Model):
    tag1 = models.ForeignKey(Tag, related_name='first_relatedtags')
    tag2 = models.ForeignKey(Tag, related_name='sec_relatedtags')
    count_field = models.CharField(verbose_name=_('Count Field'), max_length=8, default='count1')
    count = models.IntegerField(verbose_name=_('Used Count'), default=0)

    def save(self, *args, **kwargs):
        if self.tag1.name > self.tag2.name:
            self.tag1, self.tag2 = self.tag2, self.tag1
        super(TagRelate, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s,%s|%s|%s" % (self.tag1.name, self.tag2.name, self.count_field, self.count)
"""
