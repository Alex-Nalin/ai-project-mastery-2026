# The buggy code
session_expiry = datetime.utcnow() + timedelta(hours=24)
session_data["expires_at"] = session_expiry.timestamp()

# The validation code  
if session_data["expires_at"] < time.time():
    # Session expired
    return None
