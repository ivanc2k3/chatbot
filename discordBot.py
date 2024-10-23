import discord
from discord import File
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_KEY")
# Discord 頻道 ID，這裡是你希望圖片上傳的頻道
CHANNEL_ID = 1298618769782083696  # 替換為你的頻道 ID

# 定義一個 Discord 客戶端
intents = discord.Intents.default()
intents.messages = True  # 確保我們能發送消息
client = discord.Client(intents=intents)

async def upload_image_to_discord(image_path):
    """上傳圖片到 Discord 並返回圖片的 URL"""
    await client.wait_until_ready()
    
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Cannot find channel")
        return None

    try:
        # 上傳圖片
        with open(image_path, "rb") as f:
            file = File(f)
            message = await channel.send(file=file)
        
        # 獲取圖片的 URL
        if message.attachments:
            image_url = message.attachments[0].url
            print(f"Image uploaded successfully: {image_url}")
            return image_url
        else:
            print("Failed to upload image")
            return None
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

# 當 Bot 成功登入時執行
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # 上傳圖片示例
    image_url = await upload_image_to_discord("./img/1111.png")
    if image_url:
        print(f"Uploaded Image URL: {image_url}")

    # 關閉客戶端
    # await client.close()

# 運行客戶端
client.run(DISCORD_BOT_TOKEN)
