import json
import os
from plyer import storagepath

# json = {"max_key":int, "data": {"key": {"front": str, "back": str}}}

class Data:
    def __init__(self, filename="storage.json"):
        self.filename = filename
        self.current_data = self.load_data()["data"]
        self.max_key = int(self.load_data()["max_key"])
        print(type(self.max_key), self.max_key+1)

    def load_data(self):
        # Если файл существует, загружаем из него данные
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"max_key": None, "data": []}  # Если файл пустой или поврежден
        return {"max_key": None, "data": []}  # Если файла еще нет

    def save_text(self, front_input, back_input):
        self.max_key += 1
        self.current_data[str(self.max_key)] = {"front": front_input, "back": back_input}
        print(f"Saved data, front: {front_input}, back: {back_input}, idx: {self.max_key}")
        self.json_update()

        # except empty str
        #     return "Data not given, cannot save"

    def json_update(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump({"max_key": self.max_key, "data":self.current_data}, f, ensure_ascii=False, indent=4)

    def edit_card(self):
        self.json_update()

    def delete_card(self, idx):
        del self.current_data[idx]
        self.json_update()

    def import_json(self):
        pass

    def save_json_to_downloads(self):
        filename = "flashcards.json"
        downloads_dir = storagepath.get_downloads_dir()
        target_path = os.path.join(downloads_dir, filename)
        data_to_save = {"max_key": self.max_key, "data":self.current_data}
        print("Сохранено в {target_path}")

        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
