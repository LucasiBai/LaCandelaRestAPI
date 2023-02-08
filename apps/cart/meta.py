from db.models import Cart

main_model = Cart

secondary_model = Cart.get_cart_item_model()


def get_app_model():
    return main_model


def get_secondary_model():
    return secondary_model
