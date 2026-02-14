import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, storage_file="xenit_memory.json"):
        # Ensure we look in the project root, not the CWD
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.storage_file = os.path.join(base_dir, storage_file)
        self.memory = {
            "preferences": {
                "theme": "dark", # Default
                "auto_summarize": False
            },
            "contacts": {}, # Name -> Phone mapping
            "history_stats": {}, # Site visit counts
            "context_log": [], # Recent "Why I opened this"
            "user_facts": [], # "I like tech news", etc.
            "user_profile": {} # Structured data for forms (Name, Email, etc.)
        }
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.memory = json.load(f)
            except Exception as e:
                print(f"XeNit Memory Load Error: {e}")

    def save_memory(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"XeNit Memory Save Error: {e}")

    def set_preference(self, key, value):
        self.memory["preferences"][key] = value
        self.save_memory()

    def get_preference(self, key, default=None):
        return self.memory["preferences"].get(key, default)

    def log_visit(self, url, title):
        # Simple frequency tracking
        domain = url.split('/')[2] if '//' in url else url
        if domain not in self.memory["history_stats"]:
            self.memory["history_stats"][domain] = 0
        self.memory["history_stats"][domain] += 1
        self.save_memory()

    def add_user_fact(self, fact):
        """Remembers things like 'User likes dark mode' or 'User is looking for a laptop'"""
        if fact not in self.memory["user_facts"]:
            self.memory["user_facts"].append(fact)
            self.save_memory()
            
    def get_relevant_facts(self):
        return self.memory["user_facts"]

    def update_profile(self, data):
        """Updates user profile with structured data (e.g. from JSON)"""
        if isinstance(data, dict):
            self.memory["user_profile"].update(data)
            self.save_memory()
            
    def get_profile(self):
        return self.memory.get("user_profile", {})

    def add_contact(self, name, phone):
        self.memory["contacts"][name.lower()] = phone
        self.save_memory()

    def get_contact(self, name):
        return self.memory["contacts"].get(name.lower())

    def get_contacts(self):
        return self.memory.get("contacts", {})
