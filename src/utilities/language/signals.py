from django.dispatch import Signal

language_changed = Signal(providing_args=['language'])
user_language_changed = Signal(providing_args=['user', 'language'])