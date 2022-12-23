from django.contrib.auth import get_user_model

main_model = get_user_model()


def get_app_model():
    return main_model
