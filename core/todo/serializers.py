from rest_framework import serializers

from django.utils import timezone

from .models import Habit, Todo

class TodoSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'difficulty', 'user', 'is_completed', 'created_at', 'executed_at', 'deadline', 'is_expired']
        read_only_fields = ['id', 'user', 'created_at', 'executed_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def get_is_expired(self, obj):
        return obj.deadline and obj.deadline < timezone.now().date()

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'title', 'description', 'difficulty', 'user', 'streak']
        read_only_fields = ['id', 'user', 'streak']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
        