import httpx
from datetime import datetime
from loguru import logger

async def send_discord_message(embed: dict):
    payload = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://discord.com/api/webhooks/1402811131613020312/sNRHWlMzQM3KQ3Z4522g07AFfOEdCS36i-SleW4NEKByVX0oxWSHxeHSSAXOMl8C_nx-",
            json=payload,
            headers=headers
        )
        return response.status_code, response.text


def healthcheck_update_blob(heading: str, description: str, color: int) -> dict:
    embedMessageRibbon = color
    embed = {
        "title": heading,
        "description": description,
        "color": embedMessageRibbon,
        "footer": {
            "text": "Alert: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    }
    return embed


if __name__ == "__main__":
    embed = healthcheck_update_blob()
    payload = {"embeds": [embed]}
    response = httpx.post("https://discord.com/api/webhooks/1402811131613020312/sNRHWlMzQM3KQ3Z4522g07AFfOEdCS36i-SleW4NEKByVX0oxWSHxeHSSAXOMl8C_nx-", json=payload)