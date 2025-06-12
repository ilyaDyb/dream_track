from rest_framework import serializers
from typing import List

class BaseImageValidator:
    MAX_SIZE = 10 * 1024 * 1024 # 10MB in bytes
    ALLOWED_CONTENT_TYPES: List[str] = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

    @classmethod
    def validate_images(cls, images):
        if images is None:
            raise serializers.ValidationError({'images': 'No images provided.'})
        if hasattr(images, '__iter__'):
            for image in images:
                cls._is_valid_image(image)
        else:
            cls._is_valid_image(images)
    
    @classmethod
    def _is_valid_image(cls, image):
        if image.size > cls.MAX_SIZE:
            max_size_mb = cls.MAX_SIZE / (1024 * 1024)
            raise serializers.ValidationError({'images': f'Image size must be less than {max_size_mb:.2f}MB. Got {image.size / (1024 * 1024):.2f}MB'})
        if image.content_type not in cls.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError({'images': f'File must be an image of type {", ".join(cls.ALLOWED_CONTENT_TYPES)}. Got {image.content_type}'})
    
    # def _is_valid_images(self, images):
    #     return all(image.size < self.MAX_SIZE and image.content_type in self.ALLOWED_CONTENT_TYPES for image in images)


class ImageValidator(BaseImageValidator):
    pass


