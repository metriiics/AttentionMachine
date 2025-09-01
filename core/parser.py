import os
import json
import asyncio
import pandas as pd
from telethon import TelegramClient
from threading import Lock

HISTORY_FILE = "data/history.csv"
PARTICIPANTS_FILE = "data/participants.csv"

# Локи для безопасной записи
history_lock = Lock()
participants_lock = Lock()


class HistoryManager:
    def __init__(self):
        # создаем файлы, если их нет
        if not os.path.exists(HISTORY_FILE):
            pd.DataFrame(columns=["id", "name", "quantity", "type", "time", "source"]).to_csv(HISTORY_FILE, index=False)
        if not os.path.exists(PARTICIPANTS_FILE):
            pd.DataFrame(columns=["history_id", "user_id", "username", "first_name"]).to_csv(PARTICIPANTS_FILE, index=False)

    def add_history(self, name, quantity, parse_type, time, source):
        with history_lock:
            df = pd.read_csv(HISTORY_FILE)
            new_id = len(df) + 1
            new_row = pd.DataFrame([{
                "id": new_id,
                "name": name,
                "quantity": quantity,
                "type": parse_type,
                "time": time,
                "source": source
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(HISTORY_FILE, index=False)
            return new_id

    def add_participants(self, history_id, participants):
        if not participants:
            return
        with participants_lock:
            df = pd.read_csv(PARTICIPANTS_FILE)
            rows = []
            for p in participants:
                rows.append({
                    "history_id": history_id,
                    "user_id": p["id"],
                    "username": p.get("username"),
                    "first_name": p.get("first_name")
                })
            df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
            df.to_csv(PARTICIPANTS_FILE, index=False)


class Parser:
    def __init__(self, account_row):
        self.name = account_row["name"]
        self.path = account_row["path"]
        self.status = account_row["status"]
        self.history = HistoryManager()

    async def _parse_group(self, link, limit=None):
        if self.path.endswith(".json"):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)

            session_path = os.path.splitext(self.path)[0]
            client = TelegramClient(session_path, data["app_id"], data["app_hash"])
            await client.start()

            participants = []
            entity = await client.get_entity(link)  # получаем объект группы/канала
            group_name = entity.title  # имя группы/канала

            async for user in client.iter_participants(link, limit=int(limit) if limit else None):
                participants.append({
                    "id": user.id,
                    "first_name": user.first_name,
                    "username": user.username,
                })

            await client.disconnect()
            return participants, group_name

        elif os.path.isdir(self.path):
            return [], "Неизвестно"
        else:
            raise ValueError("Неизвестный формат аккаунта")

    def parse_group(self, link, limit=None, parse_type="Группа", time="00:00"):
        participants, group_name = asyncio.run(self._parse_group(link, limit))
        history_id = self.history.add_history(
            name=group_name,
            quantity=len(participants),
            parse_type=parse_type,
            time=time,
            source=link
        )
        self.history.add_participants(history_id, participants)
        return participants
