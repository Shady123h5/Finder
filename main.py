import os
import re
import asyncio
from typing import Any
import aiohttp
import discord
from flask import Flask, Response
from threading import Thread
import logging

logging.getLogger('werkzeug').setLevel(logging.ERROR)

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in secrets")

CHANNEL_CONFIGS: dict[int, str | None] = {
    1455072323437723790: os.environ.get("WEBHOOK_1"),
    1456736104786165854: os.environ.get("WEBHOOK_2"),
    1457457266654711852: os.environ.get("WEBHOOK_3"),
    1457456266610872480: os.environ.get("WEBHOOK_4"),
    1457456645134221365: os.environ.get("WEBHOOK_5"),
    1457686769905434701: os.environ.get("WEBHOOK_6"),
    1452605821744840714: os.environ.get("WEBHOOK_7"),
    1458848495619543040: os.environ.get("WEBHOOK_7"),
    1465376509555376218: os.environ.get("WEBHOOK_8"),
}

for channel_id, webhook in CHANNEL_CONFIGS.items():
    if not webhook:
        raise ValueError(
            f"Webhook for channel {channel_id} not found in secrets")

MATH_TO_ASCII: dict[str, str] = {
    '𝐀': 'A',
    '𝐁': 'B',
    '𝐂': 'C',
    '𝐃': 'D',
    '𝐄': 'E',
    '𝐅': 'F',
    '𝐆': 'G',
    '𝐇': 'H',
    '𝐈': 'I',
    '𝐉': 'J',
    '𝐊': 'K',
    '𝐋': 'L',
    '𝐌': 'M',
    '𝐍': 'N',
    '𝐎': 'O',
    '𝐏': 'P',
    '𝐐': 'Q',
    '𝐑': 'R',
    '𝐒': 'S',
    '𝐓': 'T',
    '𝐔': 'U',
    '𝐕': 'V',
    '𝐖': 'W',
    '𝐗': 'X',
    '𝐘': 'Y',
    '𝐙': 'Z',
    '𝐚': 'a',
    '𝐛': 'b',
    '𝐜': 'c',
    '𝐝': 'd',
    '𝐞': 'e',
    '𝐟': 'f',
    '𝐠': 'g',
    '𝐡': 'h',
    '𝐢': 'i',
    '𝐣': 'j',
    '𝐤': 'k',
    '𝐥': 'l',
    '𝐦': 'm',
    '𝐧': 'n',
    '𝐨': 'o',
    '𝐩': 'p',
    '𝐪': 'q',
    '𝐫': 'r',
    '𝐬': 's',
    '𝐭': 't',
    '𝐮': 'u',
    '𝐯': 'v',
    '𝐰': 'w',
    '𝐱': 'x',
    '𝐲': 'y',
    '𝐳': 'z',
}

REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"Denkai", re.IGNORECASE), "Kyron"),
    (re.compile(r"Thanh?Lamdwcute", re.IGNORECASE), "xvshady and _gg"),
]


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    for special, normal in MATH_TO_ASCII.items():
        text = text.replace(special, normal)
    return text


def advanced_replace(text: str) -> str:
    if not isinstance(text, str):
        return text
    result = normalize_text(text)
    for pattern, replacement in REPLACEMENTS:
        result = pattern.sub(replacement, result)
    return result


def replace_in_dict(d: Any) -> None:
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str):
                d[k] = advanced_replace(v)
            elif isinstance(v, (dict, list)):
                replace_in_dict(v)
    elif isinstance(d, list):
        for i, item in enumerate(d):
            if isinstance(item, str):
                d[i] = advanced_replace(item)
            elif isinstance(item, (dict, list)):
                replace_in_dict(item)


app = Flask(__name__)


@app.route('/')
def home() -> Response:
    return Response("Bot is running", status=200, mimetype='text/plain')


@app.route('/health')
def health() -> Response:
    return Response("OK", status=200, mimetype='text/plain')


def run_flask() -> None:
    app.run(host='0.0.0.0', port=8080, threaded=True)


def keep_alive() -> None:
    Thread(target=run_flask, daemon=True).start()


class MyClient(discord.Client):

    def __init__(self) -> None:
        super().__init__()
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
        await super().close()

    async def on_ready(self) -> None:
        if self.user:
            print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Watching {len(CHANNEL_CONFIGS)} channels')

    async def on_message(self, message: discord.Message) -> None:
        # Debug print for every message received
        print(f"Received message in channel {message.channel.id} from {message.author} (Bot: {message.author.bot})")
        
        # Check for both int and string match just in case
        target_channel = message.channel.id
        if target_channel not in CHANNEL_CONFIGS:
            # Try to find a match if the IDs were copied slightly wrong
            for config_id in CHANNEL_CONFIGS.keys():
                if str(config_id) in str(target_channel) or str(target_channel) in str(config_id):
                    print(f"DEBUG: Found partial channel ID match: {target_channel} vs config {config_id}")
                    target_channel = config_id
                    break
            else:
                return
        
        if not self.session:
            return

        webhook_url = CHANNEL_CONFIGS[target_channel]
        if not webhook_url:
            return

        content = advanced_replace(message.content) if message.content else ""

        payload: dict[str, Any] = {
            "content": content,
            "username": "Kyron notifier",
            "avatar_url": str(message.author.display_avatar.url)
        }

        # Remove specific link handling and big button for professional webhooks
        # Simply pass through the original message structure with name/avatar replacements
        
        # Combine embeds
        final_embeds = []
        if message.embeds:
            for embed in message.embeds:
                embed_dict: dict[str, Any] = embed.to_dict()
                
                # Make embed more professional
                if "color" not in embed_dict:
                    embed_dict["color"] = 0x2b2d31 # Dark professional color
                
                # Footer icon link
                icon_url = "https://7772c203-dbb6-4da9-a38c-8a330b69e346-00-1ievmmz7y5kbf.picard.replit.dev/static/standard-1_1769351762261.gif"
                
                embed_dict["footer"] = {
                    "text": "Kyron Notifier • Made by xvshady and _gg",
                    "icon_url": icon_url
                }
                
                replace_in_dict(embed_dict)
                final_embeds.append(embed_dict)
        
        if final_embeds:
            payload["embeds"] = final_embeds[:10]
        
        # Clean up payload if no embeds and no content
        if not payload.get("content") and not payload.get("embeds"):
            return

        try:
            async with self.session.post(webhook_url, json=payload) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    print(f'Webhook error {resp.status}: {text}')
        except Exception as e:
            print(f'Error forwarding: {e}')


async def main() -> None:
    client = MyClient()
    while True:
        try:
            async with client:
                await client.start(TOKEN)
        except Exception as e:
            print(f'Reconnecting in 5s: {e}')
            await asyncio.sleep(5)


if __name__ == "__main__":
    if not os.environ.get("GITHUB_ACTIONS"):
        keep_alive()
    
    # Check for all required webhooks if in GitHub Actions to avoid runtime errors
    if os.environ.get("GITHUB_ACTIONS"):
        for channel_id, webhook in CHANNEL_CONFIGS.items():
            if not webhook:
                print(f"Warning: Webhook for channel {channel_id} not found in environment secrets.")

    asyncio.run(main())
