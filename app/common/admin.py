class AdminImagePreviewMixin:
    class Media:
        js = ("image_preview/js/admin_image_preview.js",)
        css = {"all": ("image_preview/css/admin_image_preview.css",)}

    preview_max_width = 300
    preview_max_height = 300
    preview_enabled = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if self.preview_enabled:
            for field_name, field in form.base_fields.items():
                if hasattr(field, "widget"):
                    widget_class_name = field.widget.__class__.__name__

                    if widget_class_name in ["ClearableFileInput", "FileInput"]:
                        field.widget.attrs.update(
                            {
                                "data-preview-enabled": "true",
                                "data-preview-max-width": str(self.preview_max_width),
                                "data-preview-max-height": str(self.preview_max_height),
                            }
                        )

        return form

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.get_internal_type() in ["ImageField", "FileField"] and self.preview_enabled:
            if hasattr(formfield, "widget"):
                formfield.widget.attrs.update(
                    {
                        "data-preview-enabled": "true",
                        "data-preview-max-width": str(self.preview_max_width),
                        "data-preview-max-height": str(self.preview_max_height),
                    }
                )

        return formfield


class InlineImagePreviewMixin:
    class Media:
        js = ("image_preview/js/inline_image_preview.js",)
        css = {"all": ("image_preview/css/inline_image_preview.css",)}

    preview_max_width = 250
    preview_max_height = 250
    preview_enabled = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if self.preview_enabled:
            for field_name, field in formset.form.base_fields.items():
                if hasattr(field, "widget"):
                    widget_class_name = field.widget.__class__.__name__

                    if widget_class_name in ["ClearableFileInput", "FileInput"]:
                        field.widget.attrs.update(
                            {
                                "data-inline-preview-enabled": "true",
                                "data-inline-preview-max-width": str(self.preview_max_width),
                                "data-inline-preview-max-height": str(self.preview_max_height),
                            }
                        )

        return formset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.get_internal_type() in ["ImageField"] and self.preview_enabled:
            if hasattr(formfield, "widget"):
                formfield.widget.attrs.update(
                    {
                        "data-inline-preview-enabled": "true",
                        "data-inline-preview-max-width": str(self.preview_max_width),
                        "data-inline-preview-max-height": str(self.preview_max_height),
                    }
                )

        return formfield
