class SaveableItemMixin:
    def save(self, *args, **kwargs):
        raise NotImplementedError("Must override save method")


class ApplicableItemMixin:
    def apply_to_user(self, user):
        raise NotImplementedError("Must override apply_to_user method")