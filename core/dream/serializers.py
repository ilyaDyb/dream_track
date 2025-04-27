from rest_framework import serializers
from core.dream.models import Dream, DreamImage
from core.dream.services import DreamService  # Подключаем сервис

class DreamCUDSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    is_preview_flags = serializers.ListField(
        child=serializers.BooleanField(), write_only=True, required=False
    )
    keep_image_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Dream
        fields = ('title', 'description', 'category', 'price', 'is_private', 'images', 'is_preview_flags', 'keep_image_ids')

    def create(self, validated_data):
        DreamService.validate_dream_data(validated_data)
        user = self.context['request'].user
        return DreamService.create_dream_with_images(user, validated_data)

    def update(self, instance, validated_data):
        DreamService.validate_dream_data(validated_data)
        return DreamService.update_dream_with_images(instance, validated_data)

    def validate(self, data):
        if 'title' in data and len(data['title']) < 3:
            raise serializers.ValidationError({'title': 'Title must be at least 3 characters long'})
        
        if 'price' in data and data['price'] < 0:
            raise serializers.ValidationError({'price': 'Price cannot be negative'})
        
        if 'images' in data and len(data['images']) > 5:
            raise serializers.ValidationError({'images': 'Maximum 5 images allowed per dream'})
        
        return data


class DreamSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Dream
        fields = '__all__'

    def get_images(self, obj):
        return DreamImageSerializer(obj.images.all(), many=True).data


class DreamImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DreamImage
        fields = ['id', 'image', 'is_preview']
