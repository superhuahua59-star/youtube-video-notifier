import requests
import smtplib
from email.mime.text import MIMEText
import os

API_KEY = os.environ['YOUTUBE_API_KEY']
# 这里改成了 CHANNEL_IDS
CHANNEL_IDS_STR = os.environ['CHANNEL_IDS']
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

# 将逗号分隔的字符串拆分成列表
CHANNEL_IDS = CHANNEL_IDS_STR.split(',')

def get_latest_video(channel_id):
    # 增加 maxResults=1 让请求更小更快
    url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&order=date&part=snippet&maxResults=1'
    response = requests.get(url).json()
    # 增加防错处理，防止频道没有视频或者API请求出错导致程序崩溃
    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]['id']['videoId']
    return None

def send_email(video_id, channel_id):
    msg = MIMEText(f'New video uploaded by channel: {channel_id}\n\nWatch here: https://www.youtube.com/watch?v={video_id}')
    msg['Subject'] = 'New YouTube Video Alert'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    # 修改为了 QQ 邮箱的 SMTP 服务器
    with smtplib.SMTP('smtp.qq.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == '__main__':
    # 循环遍历每一个频道
    for channel_id in CHANNEL_IDS:
        channel_id = channel_id.strip() # 去除可能带有的空格
        if not channel_id: continue

        print(f"正在检查频道: {channel_id}")
        latest_video_id = get_latest_video(channel_id)
        
        # 如果没获取到视频，跳过当前频道
        if not latest_video_id:
            continue

        # 每个频道使用独立的 txt 文件记录，防止冲突
        file_name = f'latest_video_{channel_id}.txt'
        
        try:
            with open(file_name, 'r') as f:
                last_video_id = f.read().strip()
        except FileNotFoundError:
            last_video_id = ''

        if latest_video_id != last_video_id:
            send_email(latest_video_id, channel_id)
            with open(file_name, 'w') as f:
                f.write(latest_video_id)
            print(f"频道 {channel_id} 发现新视频，已发送邮件！")
        else:
            print(f"频道 {channel_id} 暂无新视频。")
