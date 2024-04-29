import functions_framework
import openai
from openai import OpenAI
from slack_sdk import WebClient
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import warnings
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

keys = json.load(open("api_keys.json"))

def news_to_text(url):
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.text, "html.parser")

    # Get title
    title = soup.find("title").get_text()

    # Get paragraph
    article_body = soup.find_all("p")
    article_text = ' '.join([paragraph.get_text() for paragraph in article_body])

    # Remove backslash and any empty spaces
    article_text_cleaned = re.sub(r"\\|(\s+)", " ", article_text)

    return title.strip(), article_text_cleaned.strip()

def date_format(timestamp):
    datetime_obj = datetime.utcfromtimestamp(float(timestamp))
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

def summarization(text, title):
    client = OpenAI(
        api_key=keys["openai_api_key"]
    )

    prompt = """\
    Based on the title given, I would like you to analyze an online news article that is senior-related, \
    extracting the top three keywords and providing a summarization of the content. \
    The summary should be concise, three to five sentences long, \
    and presented in JSON format with the keywords and summary included like below: \
    {"keywords": [keyword1, keyword2, keyword3], "summary": your summary here}.\
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"The title of this article: {title}. " + prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        output = response.choices[0].message.content

    except openai.BadRequestError:
        output = None

    #
    try:
        output_json = json.loads(output)

    except json.decoder.JSONDecodeError:
        output_json = {"keywords": '', "summary": ''}

    return output_json

def update_table():
    gc = gspread.service_account(filename='gs_exporter.json')
    sh = gc.open_by_url(keys["gc_url"])
    ws = sh.worksheet(keys["gc_sheet"])

    articles_df_prev = pd.DataFrame(ws.get_all_values())
    new_header = articles_df_prev.iloc[0]
    articles_df_prev = articles_df_prev[1:]
    articles_df_prev.columns = new_header

    client = WebClient(token=keys["slack_bot_token"])
    result = client.conversations_history(channel=keys["channel_id"])
    conversation_history = result["messages"]

    slack_info = []
    for i in range(len(conversation_history)):
        try:
            link = conversation_history[i]["attachments"][0]["original_url"]
            user = conversation_history[i]["user"]
            timestamp = conversation_history[i]["ts"]
            slack_info.append([link, user, timestamp])
        except KeyError:
            pass

    articles_df = pd.DataFrame(slack_info, columns=["url_link", "user_id", "timestamp"])

    # Find the most recent datetime to filter
    ts_latest = articles_df_prev.sort_values(by="datetime", ascending=False)["datetime"].iloc[0]
    articles_df["datetime"] = articles_df["timestamp"].apply(date_format)
    articles_df_new = articles_df[articles_df["datetime"] > ts_latest]

    if not articles_df_new.empty:

        users_list = client.users_list()["members"]
        users_dict = pd.DataFrame(users_list)[["id", "real_name"]].set_index("id").to_dict()["real_name"]
        articles_df_new["user_name"] = articles_df_new["user_id"].map(users_dict)

        articles_df_new[["title", "text"]] = \
            articles_df_new.apply(lambda x: pd.Series(news_to_text(x["url_link"])), axis=1)

        articles_df_new[["keywords", "summary"]] = articles_df_new.apply(
            lambda x: pd.Series(summarization(x["text"], x["title"])), axis=1
        )

        articles_df_new[["tag_1", "tag_2", "tag_3"]] = articles_df_new["keywords"].apply(pd.Series)

        articles_df_new = \
            articles_df_new[["datetime", "user_name", "title", "tag_1", "tag_2", "tag_3", "summary", "url_link"]]

        articles_df_final = pd.concat([articles_df_prev, articles_df_new], axis=0)
        articles_df_final.sort_values(by="datetime", ascending=False, inplace=True)

        set_with_dataframe(ws, articles_df_final)

@functions_framework.http
def trigger_http(request):
    st = datetime.now()
    update_table()
    return f"Table is updated in {(datetime.now() - st).seconds} seconds"

