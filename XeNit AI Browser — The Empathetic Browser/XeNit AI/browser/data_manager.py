import json
import os
from datetime import datetime

class DataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.init_managers()
        return cls._instance

    def init_managers(self):
        self.base_dir = os.path.join(os.path.expanduser("~"), ".xenit_browser")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        self.history_file = os.path.join(self.base_dir, "history.json")
        self.bookmarks_file = os.path.join(self.base_dir, "bookmarks.json")
        
        self.history = self.load_json(self.history_file)
        self.bookmarks = self.load_json(self.bookmarks_file)

    def load_json(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_json(self, data, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")

    def add_history_item(self, title, url):
        # Avoid duplicates for the very last item or spam
        if self.history and self.history[0]['url'] == url:
            return
            
        item = {
            "title": title,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        self.history.insert(0, item)
        # Keep only last 1000 items
        if len(self.history) > 1000:
            self.history = self.history[:1000]
        self.save_json(self.history, self.history_file)

    def add_bookmark(self, title, url):
        item = {"title": title, "url": url}
        self.bookmarks.append(item)
        self.save_json(self.bookmarks, self.bookmarks_file)
        
    def get_history(self):
        return self.history
        
    def get_bookmarks(self):
        return self.bookmarks
