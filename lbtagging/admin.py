from django.contrib import admin

from lbtagging.models import Tag, TaggedItem, TagUsedCount

class TaggedItemInline(admin.StackedInline):
    model = TaggedItem

class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [
        TaggedItemInline
    ]


admin.site.register(Tag, TagAdmin)
admin.site.register(TagUsedCount)
