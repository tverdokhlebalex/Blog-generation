import openai
import requests

from io import BytesIO
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

openai.api_key = "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"
newsapi_key = "83d1b597e3044c72ab71e8d40cfba829"

# Получаем новости на заданную тему
url = f"https://newsapi.org/v2/everything?q=your_topic&apiKey={newsapi_key}"
response = requests.get(url)
news_json = json.loads(response.text)
articles = [(article['title'], article['description']) for article in news_json['articles']]

# Генерируем тексты на основе полученных новостей
text = ""
for article in articles:
    prompt = f"Write an article about {article[0]}. {article[1]}"
    response = openai.Completion.create(
        model="davinci",
        prompt=prompt,
        temperature=0.7,
        max_tokens=60,
        n=1,
        stop=None
    )

    text += response.choices[0].text

# Сохраняем сгенерированные тексты в файлы на Google Drive
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "/Users/useruser/Downloads/robotic-gist-269909-33c71b462cad.json")

from googleapiclient.discovery import build

service = build('drive', 'v3', credentials=credentials)

folder_id = "1Qg3TT4VQ8JMIk7HJF9BLbGmwmLz568V_"
for i in range(len(articles)):
    title = articles[i][0].replace(" \", \"_")
    text = text[i]
    file_metadata = {
        'name': f"{title}.txt",
        'parents': [folder_id]
    }
    media = MediaFileUpload(BytesIO(text.encode()), mimetype='text/plain')
    file = service.files().create(body=file_metadata, media_body=media,
                                  fields='id').execute()
    print(F' "{title}" has been created ID: {file.get("id")} ')
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open("blog-creator").sheet1

    data_to_append = [[article[0], article[1], "date_to_publish", "Unpublished"] for article in articles]

    sheet.insert_rows(data_to_append, row=2)

