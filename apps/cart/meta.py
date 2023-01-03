from db.models import Cart, CartItem

main_model = Cart

secondary_model = CartItem


def get_app_model():
    return main_model


def get_secondary_model():
    return secondary_model
