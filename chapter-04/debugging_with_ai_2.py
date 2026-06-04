from datetime import datetime, timezone

session_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
session_data["expires_at"] = session_expiry.timestamp()
