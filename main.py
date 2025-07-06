import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

# Email setup using Brevo SMTP
def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = "michael.groover8225@gmail.com"
    msg["To"] = "michael.groover8225@gmail.com"

    server = smtplib.SMTP("smtp-relay.sendinblue.com", 587)
    server.starttls()
    server.login("michael.groover8225@gmail.com", os.getenv("BREVO_API_KEY"))
    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    server.quit()

# Global variables
prices = []
last_signal = None

def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    res = requests.get(url)
    return res.json()["bitcoin"]["usd"]

def calculate_rsi(data, period=14):
    delta = np.diff(data)
    gain = np.maximum(delta, 0)
    loss = np.maximum(-delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

while True:
    try:
        price = get_btc_price()
        prices.append(price)
        if len(prices) > 100:
            prices.pop(0)

        if len(prices) >= 20:
            df = pd.DataFrame(prices, columns=["close"])
            df["MA5"] = df["close"].rolling(window=5).mean()
            df["MA20"] = df["close"].rolling(window=20).mean()
            df["RSI"] = calculate_rsi(df["close"].values)

            current_ma5 = df["MA5"].iloc[-1]
            current_ma20 = df["MA20"].iloc[-1]
            current_rsi = df["RSI"].iloc[-1]
            signal = None

            if current_ma5 > current_ma20 and current_rsi < 70:
                signal = "BUY"
            elif current_ma5 < current_ma20 and current_rsi > 30:
                signal = "SELL"
            elif current_rsi > 80 or current_rsi < 20:
                signal = "STOP"

            if signal and signal != last_signal:
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                message = f"🚨 NEW SIGNAL: {signal}\nPrice: ${price:,.2f}\nRSI: {current_rsi:.2f}\nTime: {timestamp}"
                send_email(f"{signal} Signal Triggered", message)
                print(message)
                last_signal = signal

        time.sleep(300)  # Wait 5 minutes

    except Exception as e:
        print("Error:", e)
        time.sleep(300)
