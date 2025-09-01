import pandas as pd
import os
import asyncio
import json
from telethon import TelegramClient

ACCOUNTS_FILE = "data/accounts.csv"

class AccountManager:
    def __init__(self, csv_file=ACCOUNTS_FILE):
        self.csv_file = csv_file
        if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
            df = pd.DataFrame(columns=["name", "path", "status"])
            df.to_csv(csv_file, index=False)
        self.df = pd.read_csv(csv_file)

    def save(self):
        self.df.to_csv(self.csv_file, index=False)

    def add_account(self, path):
        account_num = len(self.df) + 1
        name = f"Account #{account_num}"
        new_row = pd.DataFrame([{
            "name": name,
            "path": path,
            "status": ""
        }])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save()
        return name

    async def _check_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Telethon создаёт .session автоматически по имени файла
            session_path = os.path.splitext(path)[0]
            client = TelegramClient(session_path, data["app_id"], data["app_hash"])
            await client.start()
            me = await client.get_me()
            await client.disconnect()
            return True, me.first_name
        except Exception as e:
            return False, str(e)

    async def _check_tdata(self, path):
        if not os.path.exists(path):
            return False, "TData папка не найдена"
        # Заглушка: проверка TData через TDLib можно добавить здесь
        return True, "TData OK"

    def check_account(self, index):
        account = self.df.iloc[index]
        path = account["path"]

        if path.endswith(".json"):
            ok, msg = asyncio.run(self._check_json(path))
        else:
            ok, msg = asyncio.run(self._check_tdata(path))

        self.df.at[index, "status"] = "ok" if ok else "fail"
        self.save()
        return ok, msg

    def check_all(self):
        results = []
        for i in range(len(self.df)):
            ok, msg = self.check_account(i)
            results.append((self.df.at[i, "name"], ok, msg))
        return results

    def get_accounts(self):
        return self.df.copy()
