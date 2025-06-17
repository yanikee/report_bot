import matplotlib.pyplot as plt
import datetime
import io
import json

import requests



def plot_graph():
  dates = []
  counts = []

  # 非同期でCSVファイルからデータを読み込み
  with open('/home/yanike/report_bot/data/guild_counts.csv', mode='r') as csvfile:
    for line in csvfile:
      row = line.strip().split(',')
      dates.append(datetime.datetime.strptime(row[0], '%Y-%m-%d'))
      counts.append(int(row[1]))

  # グラフを作成
  plt.figure(figsize=(10, 5))
  plt.plot(dates, counts, marker='o', color='b', linestyle='-', label='Guild Count')
  plt.xlabel('Date')
  plt.ylabel('Guild Count')
  plt.title('Report bot! Installations Over Time')
  plt.grid(True)
  plt.xticks(rotation=45)
  plt.tight_layout()

  # メモリ上に画像を保存
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  plt.close()
  img_buffer.seek(0)  # バッファを先頭に移動

  return img_buffer, counts[-1]


def post(webhook_url):
  img_buffer, today_count = plot_graph()

  payload = {
    "username": "Report bot! Info",
    "content": f"Today's guild count: {today_count}"
  }
  files = {
    "favicon": ('guild_count_graph.png', img_buffer),
  }

  res = requests.post(webhook_url, data=payload, files=files)
  #print( res.status_code )
  #print( json.dumps( json.loads(res.content), indent=4, ensure_ascii=False ) )


webhook_url = "https://discord.com/api/webhooks/1293846823177289759/bSnXBZHx1JawRNCKVed7iT7fuN4me3YL8h2x4ku1Lnm2k5l0ipoDsFxoMY4zYdfU4xdJ?wait=true"
post(webhook_url)