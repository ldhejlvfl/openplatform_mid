from nba_api.stats.endpoints import ScoreboardV2, BoxScoreTraditionalV2
from datetime import datetime, timedelta
import pytz
import csv
import os
import time
import random

def get_player_stats(game_id):
    # 隨機設置延遲時間，避免過於頻繁地調用API，減少被封鎖風險
    time.sleep(random.uniform(1, 3))  
    try:
        boxscore = BoxScoreTraditionalV2(game_id=game_id)
        players = boxscore.player_stats.get_dict()["data"]
        headers = boxscore.player_stats.get_dict()["headers"]
        return headers, players
    except Exception as e:
        print(f"錯誤：無法獲取 {game_id} 的球員統計數據: {e}")
        return None, None

def save_game_csv(folder_path, game_id, home_name, visitor_name, home_pts, visitor_pts, headers, players):
    filename = f"{visitor_name}_vs_{home_name}.csv"
    file_path = os.path.join(folder_path, filename)

    with open(file_path, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        # 寫入比數作為標題
        writer.writerow([f"【{visitor_name} {visitor_pts} - {home_pts} {home_name}】", f"GameID: {game_id}"])
        writer.writerow([])  # 空行
        # 寫入表頭與內容
        writer.writerow(headers)
        for row in players:
            writer.writerow(row)

    print(f"saved：{file_path}")

def get_and_save_games(date_obj):
    date_str_display = date_obj.strftime('%m/%d/%Y')
    folder_name = date_obj.strftime('%Y%m%d')
    print(f"\n嘗試抓取美國時間 {date_str_display} 的比賽...")

    folder_path = os.path.join("game_stats", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    try:
        scoreboard = ScoreboardV2(game_date=date_str_display, timeout=120)
        games = scoreboard.get_normalized_dict()["GameHeader"]
        
        if not games:  # 檢查今天是否有比賽
            print(f"今天 {date_str_display} 沒有比賽")
            return False

        linescores = scoreboard.get_normalized_dict()["LineScore"]

        success = False

        for game in games:
            game_id = game['GAME_ID']
            home_team = game['HOME_TEAM_ID']
            visitor_team = game['VISITOR_TEAM_ID']

            try:
                home_score = next(item for item in linescores if item['TEAM_ID'] == home_team)
                visitor_score = next(item for item in linescores if item['TEAM_ID'] == visitor_team)

                home_name = home_score['TEAM_ABBREVIATION']
                visitor_name = visitor_score['TEAM_ABBREVIATION']
                home_pts = home_score['PTS']
                visitor_pts = visitor_score['PTS']

                # 檢查比數是否為 None，表示比賽尚未結束
                if home_pts is None or visitor_pts is None:
                    print(f"比賽 {visitor_name} vs {home_name} 尚未結束，跳過")
                    continue  # 跳過這場比賽

                print(f"{visitor_name} {visitor_pts} - {home_pts} {home_name}")

                headers, players = get_player_stats(game_id)
                if headers and players:
                    save_game_csv(folder_path, game_id, home_name, visitor_name, home_pts, visitor_pts, headers, players)
                    success = True

            except StopIteration:
                continue
    except Exception as e:
        print(f"錯誤：無法獲取 {date_str_display} 的比賽資料: {e}")
        return False

    return success

# 判斷今天或昨天
us_eastern = pytz.timezone("US/Eastern")
today_us = datetime.now(us_eastern)
yesterday_us = today_us - timedelta(days=1)

success = get_and_save_games(today_us)
if not success:
    print("今天沒有比賽結果，改抓昨天")
    time.sleep(30) # 在api requests間睡30秒
    get_and_save_games(yesterday_us)
