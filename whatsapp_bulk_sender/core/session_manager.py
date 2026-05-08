import json
import os

class SessionManager:
    def __init__(self, session_file="logs/current_session.json"):
        self.session_file = session_file
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)

    def save_session(self, leads, excel_path):
        """
        Saves the current state of leads and the file path.
        """
        try:
            data = {
                'excel_path': excel_path,
                'leads': leads
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def load_session(self):
        """
        Loads the last saved session.
        Returns (excel_path, leads) or (None, None) if no session.
        """
        if not os.path.exists(self.session_file):
            return None, None
            
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('excel_path'), data.get('leads')
        except Exception as e:
            print(f"Error loading session: {e}")
            return None, None

    def clear_session(self):
        """
        Deletes the saved session file.
        """
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except Exception as e:
                print(f"Error clearing session: {e}")
