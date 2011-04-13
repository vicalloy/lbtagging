from django.db import models

from lbtagging.managers import TaggableManager
from lbtagging.models import (TaggedItemBase, GenericTaggedItemBase, TaggedItem,
    TagBase, Tag)


class Food(models.Model):
    name = models.CharField(max_length=50)

    tags = TaggableManager()
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class Pet(models.Model):
    name = models.CharField(max_length=50)

    tags = TaggableManager()
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class HousePet(Pet):
    trained = models.BooleanField()


# Test direct-tagging with custom through model

class TaggedFood(TaggedItemBase):
    count_field = 'count1'
    content_object = models.ForeignKey('DirectFood')

class TaggedPet(TaggedItemBase):
    count_field = 'count2'
    content_object = models.ForeignKey('DirectPet')

class DirectFood(models.Model):
    name = models.CharField(max_length=50)

    tags = TaggableManager(through="TaggedFood")
    tags_txt = models.CharField(max_length=1000)

    def delete(self):
        super(DirectFood, self).delete()

class DirectPet(models.Model):
    name = models.CharField(max_length=50)

    tags = TaggableManager(through=TaggedPet)
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class DirectHousePet(DirectPet):
    trained = models.BooleanField()


# Test custom through model to model with custom PK

class TaggedCustomPKFood(TaggedItemBase):
    count_field = 'count3'
    content_object = models.ForeignKey('CustomPKFood')

class TaggedCustomPKPet(TaggedItemBase):
    count_field = 'count4'
    content_object = models.ForeignKey('CustomPKPet')

class CustomPKFood(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    tags = TaggableManager(through=TaggedCustomPKFood)
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class CustomPKPet(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    tags = TaggableManager(through=TaggedCustomPKPet)
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class CustomPKHousePet(CustomPKPet):
    trained = models.BooleanField()

# Test custom through model to a custom tag model

class OfficialTag(TagBase):
    official = models.BooleanField()

class OfficialThroughModel(GenericTaggedItemBase):
    count_field = 'count5'
    tag = models.ForeignKey(OfficialTag, related_name="tagged_items")

class OfficialFood(models.Model):
    name = models.CharField(max_length=50)

    tags = TaggableManager(through=OfficialThroughModel)
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class OfficialPet(models.Model):
    name = models.CharField(max_length=50)

    tags = TaggableManager(through=OfficialThroughModel)
    tags_txt = models.CharField(max_length=1000)

    def __unicode__(self):
        return self.name

class OfficialHousePet(OfficialPet):
    trained = models.BooleanField()


class Media(models.Model):
    tags = TaggableManager()
    tags_txt = models.CharField(max_length=1000)

    class Meta:
        abstract = True

class Photo(Media):
    pass

class Movie(Media):
    pass


class ArticleTag(Tag):
    class Meta:
        proxy = True

    def slugify(self, tag, i=None):
        slug = "category-%s" % tag.lower()

        if i is not None:
            slug += "-%d" % i
        return slug

class ArticleTaggedItem(TaggedItem):
    class Meta:
        proxy = True

    @classmethod
    def tag_model(self):
        return ArticleTag

class Article(models.Model):
    title = models.CharField(max_length=100)

    tags = TaggableManager(through=ArticleTaggedItem)
    tags_txt = models.CharField(max_length=1000)
