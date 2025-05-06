from rest_framework import serializers

class BaseImageValidator:
    MAX_SIZE = 10 * 1024 * 1024 # 10MB
    ALLOWED_CONTENT_TYPES: list[str] = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

    @classmethod
    def validate_images(cls, images):
        for image in images:
            if image.size > cls.MAX_SIZE:
                raise serializers.ValidationError({'images': f'Image size must be less than 10MB. Got {image.size / (1024 * 1024):.2f}MB'})
            if image.content_type not in cls.ALLOWED_CONTENT_TYPES:
                raise serializers.ValidationError({'images': f'File must be an image. Got {image.content_type}'})

    # def _is_valid_images(self, images):
    #     return all(image.size < self.MAX_SIZE and image.content_type in self.ALLOWED_CONTENT_TYPES for image in images)


class ImageValidator(BaseImageValidator):
    pass


