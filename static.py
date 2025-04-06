import requests
from bs4 import BeautifulSoup
import pandas as pd

# Spotify 台灣的每日排行榜
url = "https://kworb.net/spotify/country/tw_daily.html"

# 發送 HTTP 請求，並取得網頁內容
web = requests.get(url)
# 強制設定編碼為 UTF-8
web.encoding = 'utf-8'
soup = BeautifulSoup(web.text, "html.parser")

table = soup.find("table", class_="sortable")
tbody = table.find("tbody")
trs = tbody.find_all("tr")

# 用來存儲資料的空列表
data = []

for tr in trs:
    tds = tr.find_all("td")
    rank = tds[0].text.strip()
    artist_and_song = tds[2].find_all("a")
    artist_name = artist_and_song[0].text.strip()
    song_name = artist_and_song[1].text.strip()
    days = tds[3].text.strip()
    streams = tds[6].text.strip()
    seven_days = tds[8].text.strip()
    seven_days_plus = tds[9].text.strip()
    total = tds[10].text.strip()

    # 將資料加入到列表中
    data.append([rank, artist_name, song_name, days, streams, seven_days, seven_days_plus, total])


# 使用 pandas 將資料存儲到 CSV 文件中
df = pd.DataFrame(data, columns=["排名", "歌手", "歌名", "在榜單天數", "streams", "7day", "7day+", "總播放數"])

df.to_csv("static.csv", index=False, encoding="utf-8")

# print(str(data).encode('utf-8').decode('utf-8'))
print("已將資料存入static.csv")



