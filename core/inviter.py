import asyncio
import pandas as pd
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import InviteToChannelRequest
import os
import json

PARTICIPANTS_FILE = "data/participants.csv"
HISTORY_FILE = "data/history.csv"

class Inviter:
    def __init__(self, account_row):
        self.account_row = account_row
        self.client = None

    async def _connect(self):
        if self.account_row["path"].endswith(".json"):
            with open(self.account_row["path"], "r", encoding="utf-8") as f:
                data = json.load(f)
            session_path = os.path.splitext(self.account_row["path"])[0]
            self.client = TelegramClient(session_path, data["app_id"], data["app_hash"])
            await self.client.start()
        else:
            raise ValueError("Неподдерживаемый формат аккаунта")

    async def invite_to_group(self, group_link, history_id, limit=None):
        if not self.client:
            await self._connect()

        if not os.path.exists(PARTICIPANTS_FILE):
            return 0

        df = pd.read_csv(PARTICIPANTS_FILE)
        df = df.query("history_id == @history_id")
        if limit:
            df = df.head(int(limit))

        invited_count = 0
        entity = await self.client.get_entity(group_link)

        for _, user in df.iterrows():
            try:
                await self.client(InviteToChannelRequest(
                    channel=entity,
                    users=[user["user_id"]]
                ))
                invited_count += 1
                # Пауза между приглашениями (5 секунд)
                await asyncio.sleep(5)
            except errors.UserPrivacyRestrictedError:
                print(f"Нельзя пригласить {user['first_name']} из-за приватности")
            except Exception as e:
                print(f"Не удалось пригласить {user['first_name']}: {e}")

        await self.client.disconnect()
        return invited_count

    def invite(self, group_link, history_id, limit=None):
        return asyncio.run(self.invite_to_group(group_link, history_id, limit))

    @staticmethod
    def get_history_records():
        if not os.path.exists(HISTORY_FILE):
            return []
        df = pd.read_csv(HISTORY_FILE)
        return df[["id", "name", "time", "source"]].to_dict("records")
