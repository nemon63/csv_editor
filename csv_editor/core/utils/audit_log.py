import json
from datetime import datetime
from pathlib import Path

class AuditLogger:
    def __init__(self, log_file="audit.log"):
        self.log_file = Path(log_file)
        self.entries = []
        
        if self.log_file.exists():
            self._load_entries()

    def _load_entries(self):
        with open(self.log_file, 'r', encoding='utf-8') as f:
            self.entries = json.load(f)

    def log(self, action, details=None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        self.entries.append(entry)
        self._save()

    def _save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, indent=2)

    def get_logs(self, filter_action=None):
        if filter_action:
            return [e for e in self.entries if e['action'] == filter_action]
        return self.entries
