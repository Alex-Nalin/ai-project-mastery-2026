import hashlib
import json

def generate_idempotency_key(data: dict) -> str:
    """Generate a unique key for deduplication."""
    # Only use fields that define uniqueness
    key_fields = {
        'email': data.get('email'),
        'subject': data.get('subject'),
        'received_date': data.get('received_date')
    }
    return hashlib.sha256(
        json.dumps(key_fields, sort_keys=True).encode()
    ).hexdigest()
