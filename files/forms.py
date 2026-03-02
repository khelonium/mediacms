from django import forms

from .methods import get_next_state, is_mediacms_editor
from .models import Media


class MultipleSelect(forms.CheckboxSelectMultiple):
    input_type = "checkbox"


class MediaForm(forms.ModelForm):
    new_tags = forms.CharField(label="Tags", help_text="a comma separated list of new tags.", required=False)

    class Meta:
        model = Media
        fields = (
            "title",
            "category",
            "new_tags",
            "add_date",
            "uploaded_poster",
            "description",
            "state",
            "featured",
            "thumbnail_time",
            "is_reviewed",
            "allow_download",
        )
        widgets = {
            "tags": MultipleSelect(),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(MediaForm, self).__init__(*args, **kwargs)
        if self.instance.media_type != "video":
            self.fields.pop("thumbnail_time")
        if not is_mediacms_editor(user):
            self.fields.pop("featured")
            self.fields.pop("is_reviewed")
        self.fields["new_tags"].initial = ", ".join([tag.title for tag in self.instance.tags.all()])

    def clean_uploaded_poster(self):
        image = self.cleaned_data.get("uploaded_poster", False)
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5mb )")
            return image

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        state = data.get("state")
        if state != self.initial["state"]:
            self.instance.state = get_next_state(self.user, self.initial["state"], self.instance.state)

        media = super(MediaForm, self).save(*args, **kwargs)
        return media
