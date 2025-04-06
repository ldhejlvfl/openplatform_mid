import requests
import csv

# API URL 與參數
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
params = {
    "Authorization": "CWA-94A74475-F826-4F56-A8E4-4E36E642C516"
}

# 元素轉中文
element_map = {
    "Wx": "天氣現象",
    "PoP": "降雨機率",
    "MinT": "最低氣溫",
    "MaxT": "最高氣溫",
    "CI": "舒適度"
}

# 縣市北到南排序
city_order = [
    "基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣",
    "宜蘭縣", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣",
    "嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣",
    "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"
]

# 取得資料
response = requests.get(url, params=params)
data = response.json()

# 收集資料
raw_data = []
locations = data['records']['location']
for location in locations:
    location_name = location['locationName']
    for weather in location['weatherElement']:
        element_name = element_map.get(weather['elementName'], weather['elementName'])
        for time_data in weather['time'][:2]:
            start = "'" + time_data['startTime']  # 加上 ' 避免 Excel 自動轉格式
            end = "'" + time_data['endTime']
            value = time_data['parameter']['parameterName']
            raw_data.append([location_name, element_name, start, end, value])

# 排序
sorted_data = sorted(
    raw_data,
    key=lambda x: city_order.index(x[0]) if x[0] in city_order else 999
)

# 寫入 CSV
with open('api.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["地點", "氣象項目", "開始時間", "結束時間", "數值"])
    writer.writerows(sorted_data)

print("已將資料存入api.csv")
