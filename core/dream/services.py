from django.db import transaction
from rest_framework import serializers
from core.dream.models import Dream, DreamImage

class DreamService:
    @classmethod
    def create_dream_with_images(cls, user, validated_data):
        images, is_preview_flags = cls._extract_images_and_flags(validated_data)

        with transaction.atomic():
            dream = Dream.objects.create(user=user, **validated_data)
            cls._create_images(dream, images, is_preview_flags)
        return dream

    @classmethod
    def update_dream_with_images(cls, instance, validated_data):
        images, is_preview_flags, keep_image_ids = cls._extract_images_flags_and_keep_ids(validated_data)

        with transaction.atomic():
            cls._update_fields(instance, validated_data)
            cls._sync_images(instance, images, is_preview_flags, keep_image_ids)
        return instance

    @classmethod
    def validate_dream_data(cls, data):
        if 'is_preview_flags' in data:
            if data['is_preview_flags'].count(True) != 1:
                raise serializers.ValidationError({'is_preview_flags': 'Exactly one image must be marked as preview.'})

    # ----------------- Private Methods -----------------

    @staticmethod
    def _extract_images_and_flags(validated_data):
        images = validated_data.pop('images', [])
        is_preview_flags = validated_data.pop('is_preview_flags', [])
        return images, is_preview_flags

    @staticmethod
    def _extract_images_flags_and_keep_ids(validated_data):
        images = validated_data.pop('images', [])
        is_preview_flags = validated_data.pop('is_preview_flags', [])
        keep_image_ids = validated_data.pop('keep_image_ids', [])
        return images, is_preview_flags, keep_image_ids

    @staticmethod
    def _update_fields(instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    @classmethod
    def _sync_images(cls, instance, images, is_preview_flags, keep_image_ids):
        instance.images.exclude(id__in=keep_image_ids).delete()
        for idx, image in enumerate(images):
            is_preview = (idx < len(is_preview_flags)) and is_preview_flags[idx] if is_preview_flags else (idx == 0 and not keep_image_ids)
            DreamImage.objects.create(dream=instance, image=image, is_preview=is_preview)
        cls._ensure_single_preview(instance)

    @staticmethod
    def _create_images(dream, images, is_preview_flags):
        if not images:
            raise ValueError('Images must be provided')

        for idx, image in enumerate(images):
            is_preview = (idx < len(is_preview_flags)) and is_preview_flags[idx] if is_preview_flags else (idx == 0)
            DreamImage.objects.create(dream=dream, image=image, is_preview=is_preview)

        DreamService._ensure_single_preview(dream)

    @staticmethod
    def _ensure_single_preview(dream):
        images = dream.images.all()
        if not images.exists():
            return

        preview_images = images.filter(is_preview=True)

        if preview_images.count() == 1:
            return

        images.update(is_preview=False)

        first_image = images.first()
        first_image.is_preview = True
        first_image.save()
