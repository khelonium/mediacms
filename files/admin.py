from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import (
    Category,
    EncodeProfile,
    Encoding,
    Language,
    Media,
    Subtitle,
    Tag,
    Technique,
    TechniqueMedia,
)


class MediaAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = [
        "title",
        "user",
        "add_date",
        "media_type",
        "duration",
        "state",
        "is_reviewed",
        "encoding_status",
        "featured",
    ]
    list_filter = ["state", "is_reviewed", "encoding_status", "featured", "category"]
    ordering = ("-add_date",)
    readonly_fields = ("user", "tags", "category", "channel")


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "user", "add_date", "is_global", "media_count"]
    list_filter = ["is_global"]
    ordering = ("-add_date",)
    readonly_fields = ("user", "media_count")


class TagAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "user", "media_count"]
    readonly_fields = ("user", "media_count")


class EncodeProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "extension", "resolution", "codec", "description", "active")
    list_filter = ["extension", "resolution", "codec", "active"]
    search_fields = ["name", "extension", "resolution", "codec", "description"]
    list_per_page = 100
    fields = ("name", "extension", "resolution", "codec", "description", "active")


class LanguageAdmin(admin.ModelAdmin):
    pass


class SubtitleAdmin(admin.ModelAdmin):
    pass


class EncodingAdmin(admin.ModelAdmin):
    pass


admin.site.register(EncodeProfile, EncodeProfileAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Encoding, EncodingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Subtitle, SubtitleAdmin)
admin.site.register(Language, LanguageAdmin)


class TechniqueAdmin(MPTTModelAdmin):
    list_display = ["title", "slug", "status", "parent"]
    list_filter = ["status"]
    search_fields = ["title", "slug"]
    mptt_level_indent = 20


class TechniqueMediaAdmin(admin.ModelAdmin):
    list_display = ["technique", "media", "added_by", "add_date"]
    list_filter = ["technique"]
    search_fields = ["technique__slug", "technique__title", "media__title"]
    readonly_fields = ("added_by", "media")
    raw_id_fields = ("technique",)


admin.site.register(Technique, TechniqueAdmin)
admin.site.register(TechniqueMedia, TechniqueMediaAdmin)
