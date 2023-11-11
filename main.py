import requests
import datetime as dt
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv("local.env")

SENDER = os.getenv("SENDER")
RECEIVER = os.getenv("RECEIVER")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ACCOUNT_SID = ("ACCOUNT_SID")
AUTH_TOKEN = ("AUTH_TOKEN")
TODAY = dt.date.today()
YESTERDAY = TODAY - dt.timedelta(days=1)
TWO_DAYS_AGO = TODAY - dt.timedelta(days=2)

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}

news_parameters = {
    "apiKey": NEWS_API_KEY,
    "q": COMPANY_NAME,
    "from": TWO_DAYS_AGO,
    "to": YESTERDAY,
    "language": "en",
}


def check_stock(dates, data):
    close_yesterday = data[dates[0]]["4. close"]
    close_two_days_ago = data[dates[1]]["4. close"]
    calculate_stock_value(close_yesterday, close_two_days_ago)


def calculate_stock_value(close_yesterday, close_two_days_ago):
    dif_value = round(float(close_yesterday) - float(close_two_days_ago))
    dif_percentage = round(dif_value / float(close_two_days_ago) * 100)

    if dif_percentage >= 1:
        print(f"stock has increased {dif_percentage}%")
        get_news("pos", dif_percentage)
    elif dif_percentage <= -5:
        print(f"stock has decreased {dif_percentage}%")
        get_news("neg", dif_percentage)
    else:
        print(f"not enough change {dif_percentage}%")


def get_news(neg_or_pos, dif_percentage):
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()['articles'][:3]

    if neg_or_pos == "pos":
        icon = "🔺"
    else:
        icon = "🔻"

    news_articles = [f"Headline: {article['title']}\nBrief: {article['description']}" for article in news_data]

    for article in news_articles:
         client = Client(ACCOUNT_SID, AUTH_TOKEN)
         message = client.messages \
             .create(
             body=f"{STOCK}: {icon} {dif_percentage}%\n{article}",
             from_=SENDER,
             to=RECEIVER,
         )
         print(message.status)


stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()['Time Series (Daily)']
stock_dates = list(stock_data)[:2]
check_stock(stock_dates, stock_data)
