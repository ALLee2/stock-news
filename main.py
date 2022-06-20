import requests
import smtplib
# from twilio.rest import Client
import os

STOCK = "AMZN"
COMPANY_NAME = "Amazon Inc"

AV_ENDPOINT = "https://www.alphavantage.co/query"
AV_API_KEY = os.environ["AV_API_KEY"]
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
# TWILIO_SID = "YOUR TWILIO ACCOUNT SID"
# TWILIO_AUTH_TOKEN = "YOUR TWILIO AUTH TOKEN"
my_email = os.environ["my_email"]
my_password = os.environ["my_password"]
to_addrs = os.environ["to_addrs"]

alpha_vintage_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": AV_API_KEY,
}

stock_response = requests.get(url=AV_ENDPOINT, params=alpha_vintage_params)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]
stock_data_list = [value for (key, value) in stock_data.items()]
yesterday_close = stock_data_list[0]["4. close"]
previous_day_close = stock_data_list[1]["4. close"]
change = float(yesterday_close) - float(previous_day_close)
up_down = None
if change > 0:
    up_down = "🔺"
else:
    up_down = "🔻"
percent_change = round((float(yesterday_close) - float(previous_day_close)) / float(yesterday_close) * 100, 2)

if abs(percent_change) > 1:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]
    three_articles = news_data[:3]
    formatted_articles = [f"{STOCK}: {up_down}{percent_change}%\n" \
                          f"Headline: {article['title']}. \n" \
                          f"Brief: {article['description']}" for article in three_articles]
    # client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    # for article in formatted_articles:
    #     message = client.messages.create(
    #         body=article,
    #         from_=VIRTUAL_TWILIO_NUMBER,
    #         to=VERIFIED_NUMBER
    for article in three_articles:
        connection = smtplib.SMTP("smtp.gmail.com")
        connection.starttls()
        connection.login(user=my_email, password=my_password)
        connection.sendmail(from_addr=my_email,
                            to_addrs=os.environ["to_addrs"],
                            msg=f"Subject:{STOCK}: {up_down}{percent_change}%\n\n"
                                f"Headline: {article['title']}.\n"
                                f"Brief: {article['description']}".encode('ascii', 'ignore')
                            )
