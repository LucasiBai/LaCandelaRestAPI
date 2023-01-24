from db.models import Order, OrderProduct

main_model = Order

secondary_model = OrderProduct


def get_app_model():
    return main_model


def get_secondary_model():
    return secondary_model
