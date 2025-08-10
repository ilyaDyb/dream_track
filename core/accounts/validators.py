from django.core.exceptions import ValidationError

import json


def validate_trade_offer(value):
    # try:
    #     json.dumps(value)
    # except Exception:
    #     raise ValidationError("Trade offer must be serializable")
    if not isinstance(value, dict):
        raise ValidationError("Trade offer must be a dictionary")
    
    for key in value:
        if key not in ['coins', 'items_ids']:
            raise ValidationError(f"Invalid key in trade offer: {key}")
    
    if 'coins' in value and (not isinstance(value['coins'], int) or value['coins'] < 0):
        raise ValidationError("Coins must be a positive integer")
    
    if 'items_ids' in value:
        if not isinstance(value['items_ids'], list):
            raise ValidationError("Items IDs must be a list")
        if not all(isinstance(item_id, int) for item_id in value['items_ids']):
            raise ValidationError("All item IDs must be integers")