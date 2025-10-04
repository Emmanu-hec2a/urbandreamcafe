# utils.py
import json
from pywebpush import webpush
from .models import PushSubscription

VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgfWfJbjUWsfxd1GxLRwsiVoMo/T5nbZTZKKpa1WUnNA+hRANCAAT9nGX9yf5vW6dwFkKkn6s8rTsIGKiHBwSrGubbo98BtVVfrkwkSMp3v1S9koIv6JigRJ9vLRYFU0b5Zzk3mfdB"
VAPID_CLAIMS = {"sub": "mailto:petniqueke@gmail.com"}

def send_push_to_all(title, body, url="/"):
    subscriptions = PushSubscription.objects.all()
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": sub.keys
                },
                data=json.dumps({"title": title, "body": body, "url": url}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except Exception as e:
            print("Push failed for subscription:", sub.endpoint, e)
