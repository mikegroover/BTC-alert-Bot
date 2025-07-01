
import requests
import time
import os

# Load API key from environment variable
api_key = os.getenv("BREVO_API_KEY")

# Email config
sender = {"name": "BTC Alert Bot", "email": "michael.groover8225@gmail.com"}
to = [{"email": "michael.groover8225@gmail.com", "name": "Michael"}]
subject = "BTC Bullish Signal 📈"

# Function to check BTC price using CoinGecko API
def get_btc_price():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = res.json()
        return data["bitcoin"]["usd"]
    except Exception as e:
        print(f"Error fetching BTC price: {e}")
        return None

# Simulated confidence level generator (you can replace this with real logic)
def get_confidence_level():
    import random
    return random.randint(70, 90)

# Main loop
while True:
    price = get_btc_price()
    confidence = get_confidence_level()

    if price is not None and confidence >= 80:
        text_content = f"""BTC Bullish Signal 📈
Confidence: {confidence}%
Current Price: ${price}
Take Action Now!
"""
        payload = {
            "sender": sender,
            "to": to,
            "subject": subject,
            "textContent": text_content
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            if response.status_code == 201:
                print(f"📩 BTC alert sent: ${price} @ {confidence}%")
            else:
                print(f"❌ Email failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

    # Wait 60 seconds before checking again
    time.sleep(60)
