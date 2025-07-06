from django.urls import path
from .views import (
    DreamView, LikeDreamView, DreamListView, PublicDreamListView, DreamStepListCreateView,
    DreamStepRetrieveUpdateDestroyView, DreamStepExecuteView, DreamStepGenerateView, DreamStepDumbCreateView
)

app_name = 'dream'

urlpatterns = [
    # Dreams
    path('dreams/', DreamListView.as_view(), name='dreams'),
    path('dreams/public/', PublicDreamListView.as_view(), name='public_dreams'),
    path('dreams/<int:id>/', DreamView.as_view(), name='dream'),
    path('dreams/<int:id>/like/', LikeDreamView.as_view(), name='like_dream'),

    # DreamSteps
    path('dreams/<int:dream_id>/steps/', DreamStepListCreateView.as_view(), name='dream_steps'),
    path('dreams/<int:dream_id>/steps/<int:id>/', DreamStepRetrieveUpdateDestroyView.as_view(), name='dream_step'),
    path('dreams/<int:dream_id>/steps/<int:id>/execute/', DreamStepExecuteView.as_view(), name='dream_step_execute'),
    path('dreams/<int:dream_id>/steps/generate/', DreamStepGenerateView.as_view(), name='dream_step_generate'),
    path('dreams/<int:dream_id>/steps/dumb_create/', DreamStepDumbCreateView.as_view(), name='dream_step_dumb_create'),
]