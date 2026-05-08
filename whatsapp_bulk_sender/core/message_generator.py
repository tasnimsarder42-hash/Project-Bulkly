import json
import random
import os
import sys

class MessageGenerator:
    def __init__(self, templates_path="data/message_templates.json"):
        self.templates_path = self._resource_path(templates_path)
        self.templates = self._load_templates()
        
    def _resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
        
    def _load_templates(self):
        if not os.path.exists(self.templates_path):
            # Fallback if json not found
            return {}
        with open(self.templates_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_message(self, lead, company_name=None, contact_info=None, address=None, theme="Default"):
        """
        Generates a unique message for a given lead.
        lead dict requires: 'country', 'experience', 'experience_year'
        """
        if not self.templates or 'themes' not in self.templates:
            return "Template file not found or invalid format. Please check data/message_templates.json"
            
        # Get theme templates, fallback to Default
        theme_templates = self.templates['themes'].get(theme, self.templates['themes'].get('Default', {}))
        
        if not theme_templates:
            return "No templates found for the selected theme."
            
        # Use provided company name or default
        if not company_name:
            company_name = "সোনালী সৌরভ মাইগ্রেশন এ্যান্ড ভিসা"
            
        if not contact_info:
            contact_info = "01624-283260, 01619-949990"
            
        if not address:
            address = "গ-১৩১/১, যুবরাজ ভিলা (২য় তলা), বাড্ডা লিঙ্ক রোড (প্রাণ সেন্টারের বিপরীতে), ঢাকা-১২১২"

        country = lead.get('country', '').strip()
        experience = lead.get('experience', '').strip()
        exp_year = lead.get('experience_year', '').strip()
        
        # Fallbacks for empty values
        display_country = country if country else "বিদেশে"
        display_experience = experience if experience else "দক্ষ কর্মী"
        # We can also use "অভিজ্ঞ পেশাদার" randomly if blank
        if not experience:
            display_experience = random.choice(["দক্ষ কর্মী", "অভিজ্ঞ পেশাদার"])
            
        # Select random parts based on the selected theme
        greetings_list = theme_templates.get('greetings', ["আসসালামু আলাইকুম,"])
        greeting = random.choice(greetings_list)
        
        # Replace company name in intro templates if needed
        intro_templates = theme_templates.get('intros', ["আমি সোনালী সৌরভ মাইগ্রেশন থেকে বলছি।"])
        raw_intro = random.choice(intro_templates)
        intro = raw_intro.replace("সোনালী সৌরভ মাইগ্রেশন এ্যান্ড ভিসা", company_name).replace("সোনালী সৌরভ মাইগ্রেশন", company_name)
        
        hook_templates_list = theme_templates.get('hooks', ["{country}-এ কাজের সুযোগ রয়েছে।"])
        hook_template = random.choice(hook_templates_list)
        hook = hook_template.replace('{country}', display_country).replace('{experience}', display_experience)
        
        doc_q_list = theme_templates.get('document_questions', ["আপনার কাগজপত্র কি রেডি?"])
        doc_q = random.choice(doc_q_list)
        
        proc_info_list = theme_templates.get('process_infos', ["আমাদের প্রসেস স্বচ্ছ।"])
        proc_info = random.choice(proc_info_list)
        
        cta_list = theme_templates.get('ctas', ["আজই যোগাযোগ করুন।"])
        cta = random.choice(cta_list)
        
        closing_list = theme_templates.get('closings', ["ধন্যবাদ"])
        closing = random.choice(closing_list)
        
        # Build company info
        contact_str = f"যোগাযোগ: {contact_info}" if contact_info else ""
        address_str = f"ঠিকানা: {address}" if address else ""
        
        # Optional: Add experience year sentence if available
        exp_sentence = ""
        if exp_year:
            exp_sentence = f"আপনার {exp_year} বছরের অভিজ্ঞতা সত্যিই প্রশংসনীয়। "
        
        # Construct final message
        message = f"{greeting}\n\n{intro}\n{hook}\n{exp_sentence}\n{doc_q}\n\n{proc_info}\n{cta}\n\n{company_name}\n{contact_str}\n{address_str}\n\n{closing}"
        
        # Clean up multiple newlines that might occur if some fields are empty
        while "\n\n\n" in message:
            message = message.replace("\n\n\n", "\n\n")

        return message

if __name__ == "__main__":
    # Self-test block to verify output variety
    print("--- Running Message Generator Test ---")
    
    # Needs to locate json properly when run directly
    generator = MessageGenerator(templates_path="../data/message_templates.json")
    if not generator.templates:
        # Try local if running from project root
        generator = MessageGenerator(templates_path="data/message_templates.json")
    
    test_leads = [
        {"country": "Qatar", "experience": "Plumber", "experience_year": "5+"},
        {"country": "Serbia", "experience": "Forklift Operator", "experience_year": "10+"},
        {"country": "", "experience": "Rajmistri", "experience_year": ""},
        {"country": "Oman", "experience": "", "experience_year": "2+"},
        {"country": "", "experience": "", "experience_year": ""}
    ]
    
    for i, lead in enumerate(test_leads, 1):
        print(f"\n--- Test Message {i} ---")
        msg = generator.generate_message(lead)
        print(msg)
