from django.db import transaction

from rest_framework import serializers, status

from core.dream import integrations
from core.dream.models import Dream, DreamImage
from core.dream.validators import BaseImageValidator
from core.todo.models import Todo

class DreamService:

    @staticmethod
    def create_or_delete_like(dream, user):
        if dream.likes.filter(user=user).exists():
            dream.likes.remove(user)
            return 'Like removed', status.HTTP_200_OK
        else:
            dream.likes.add(user)
            return 'Like added', status.HTTP_200_OK

    @classmethod
    def create_dream_with_images(cls, user, validated_data):
        images, is_preview_flags = cls._extract_images_and_flags(validated_data)
        if len(images) == 0:
            raise serializers.ValidationError({'images': 'At least one image is required'})
        if len(images) == 1:
            is_preview_flags = [True]

        BaseImageValidator.validate_images(images)

        with transaction.atomic():
            dream = Dream.objects.create(user=user, **validated_data)
            cls._create_images(dream, images, is_preview_flags)
        return dream

    @classmethod
    def update_dream_with_images(cls, instance, validated_data):
        images, is_preview_flags, keep_image_ids = cls._extract_images_flags_and_keep_ids(validated_data)

        BaseImageValidator.validate_images(images)

        with transaction.atomic():
            cls._update_fields(instance, validated_data)
            cls._sync_images(instance, images, is_preview_flags, keep_image_ids)
        return instance

    @staticmethod
    def validate_dream_data(data):
        if 'is_preview_flags' in data:
            if data['is_preview_flags'].count(True) != 1:
                raise serializers.ValidationError({'is_preview_flags': 'Exactly one image must be marked as preview.'})
        if 'images' in data:
            if len(data['images']) > 5:
                raise serializers.ValidationError({'images': 'Maximum 5 images allowed per dream.'})
            if len(data['images']) != len(data.get('is_preview_flags', [])):
                raise serializers.ValidationError({'images': 'Number of images must match number of is_preview_flags.'})
            BaseImageValidator.validate_images(data['images'])

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

    @classmethod
    def _create_images(cls, dream, images, is_preview_flags):
        for idx, image in enumerate(images):
            is_preview = (idx < len(is_preview_flags)) and is_preview_flags[idx] if is_preview_flags else (idx == 0)
            DreamImage.objects.create(dream=dream, image=image, is_preview=is_preview)
        cls._ensure_single_preview(dream)

    @classmethod
    def _ensure_single_preview(cls, dream):
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

class DreamStepService:
    def __init__(self, dream: Dream) -> None:
        self.dream = dream

    def generate_steps(self):
        return integrations.AIIntegration.generate_dream_steps(self.dream.title)

    def dumb_create_steps(self, steps) -> bool:
        with transaction.atomic():
            for step_data in steps:
                Todo.objects.create(
                    user=self.dream.user,
                    title=step_data.get('title', ''),
                    description=step_data.get('description', ''),
                    difficulty=step_data.get('difficulty', 1),
                    is_dream_step=True,
                    dream=self.dream
                )
            return True

    @staticmethod
    def execute_dream_step(todo: Todo):
        todo.execute_task()
        percentage_achieved = todo._get_percentage_achieved()
        if percentage_achieved == 100:
            todo.dream.is_completed = True
            todo.dream.save()
        return percentage_achieved
