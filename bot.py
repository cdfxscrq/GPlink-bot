import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_KEY = os.environ.get('API_KEY', 'f46adc62a4b4b6841da8ff9ebabb29cfe369c03e')

bot = Client(
    "gplink_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        f"**Hi {message.from_user.first_name}!**\n\n"
        "I'm GPlink bot. Just send me a link and get a short link."
    )

@bot.on_message(filters.regex(r"https?://[^\s]+") & filters.private)
async def link_handler(client: Client, message: Message):
    match = message.matches[0] if message.matches else None
    if not match:
        await message.reply_text("No valid link found in your message.")
        return
    link = match.group(0)
    try:
        short_link = await get_shortlink(link)
        await message.reply_text(
            f'Here is your [short link]({short_link})',
            disable_web_page_preview=True,
            quote=True
        )
    except Exception as e:
        await message.reply_text(f'Error: {e}', quote=True)

async def get_shortlink(link: str) -> str:
    url = "https://gplinks.in/api"
    params = {"api": API_KEY, "url": link}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"API request failed with status {response.status}")
            data = await response.json()
            if "shortenedUrl" in data:
                return data["shortenedUrl"]
            elif "shortenedUrl" in data.get("data", {}):
                return data["data"]["shortenedUrl"]
            elif "shortenedUrl" in data.get("shortenedUrl", {}):
                return data["shortenedUrl"]["shortenedUrl"]
            else:
                raise Exception(f"API error: {data.get('message', 'Unknown error')}")

if __name__ == "__main__":
    bot.run()
