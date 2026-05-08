import time
import random
import urllib.parse
import threading
import csv
import os
import datetime
import winreg
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from core.ai_reply_module import AIReplyModule

class WhatsAppSender:
    def __init__(self, ui_callback=None, log_callback=None):
        self.driver = None
        self.ui_callback = ui_callback
        self.log_callback = log_callback
        
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False
        
        self.total_sent_session = 0
        self.daily_limit_warning = 150 # Reduced default for safety
        
        # Anti-ban behavior state
        self.behavior_counter = 0
        
        # Ensure log dir exists
        os.makedirs("logs", exist_ok=True)
        self.log_file = "logs/send_log.csv"
        self._init_log_file()
        
    def _init_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Phone", "Status", "Details"])

    def log_event(self, phone, status, details=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, phone, status, details])
        
        if self.log_callback:
            self.log_callback(f"[{timestamp}] {phone}: {status} - {details}")

    def _get_chrome_version(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return int(version.split('.')[0])
        except Exception:
            pass
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
            version, _ = winreg.QueryValueEx(key, "version")
            return int(version.split('.')[0])
        except Exception:
            pass
        return 147  # Fallback

    def initialize_driver(self):
        try:
            if self.driver is None:
                self.log_event("SYSTEM", "INFO", "Initializing Chrome Driver...")
                options = uc.ChromeOptions()
                
                # Setup user data dir for session persistence (Feature 2)
                profile_dir = os.path.abspath(os.path.join(os.getcwd(), "chrome_profile"))
                options.add_argument(f"--user-data-dir={profile_dir}")
                
                # Dynamically get installed Chrome version
                chrome_version = self._get_chrome_version()
                self.log_event("SYSTEM", "INFO", f"Detected Chrome Version: {chrome_version}")
                
                self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=chrome_version)
                self.driver.get("https://web.whatsapp.com")
                self.log_event("SYSTEM", "INFO", "Please scan QR code if not logged in. Session will be saved for future use.")
                
                # Wait for main screen to load (indicating successful login)
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, "pane-side"))
                )
                self.log_event("SYSTEM", "INFO", "WhatsApp Web loaded successfully.")
                return True
        except Exception as e:
            self.log_event("SYSTEM", "ERROR", f"Driver init failed: {str(e)}")
            return False

    def send_messages(self, leads, message_generator, settings):
        """
        Runs in a separate thread.
        settings dict: {
            'min_delay': 10,
            'max_delay': 30,
            'break_after': 25,
            'break_min': 120,
            'break_max': 300
        }
        """
        self.is_running = True
        self.stop_requested = False
        
        if not self.initialize_driver():
            if self.ui_callback:
                self.ui_callback("SYSTEM_ERROR", "Failed to initialize browser.")
            self.is_running = False
            return

        messages_since_break = 0
        
        # Initialize AI module if key is provided
        ai_api_key = settings.get('gemini_api_key', '')
        ai_context = settings.get('bot_context', '')
        ai_module = AIReplyModule(ai_api_key, ai_context) if ai_api_key else None
        
        if ai_module and ai_module.is_configured:
            self.log_event("SYSTEM", "INFO", "Smart Reply Engine activated.")
        
        for lead in leads:
            while self.is_paused and not self.stop_requested:
                time.sleep(1)
                
            if self.stop_requested:
                self.log_event("SYSTEM", "INFO", "Sending stopped by user.")
                break
                
            # Check for incoming replies
            if ai_module and ai_module.is_configured:
                self._check_and_reply_unread(ai_module)
                
            if lead.get('status') in ['Sent', 'Failed']:
                continue # Skip already sent or previously failed messages
                
            phone = lead.get('phone')
            if not phone:
                self.log_event("UNKNOWN", "Failed", "No phone number")
                if self.ui_callback: self.ui_callback(lead.get('id'), "Failed")
                continue

            # Check daily limit
            daily_limit = settings.get('daily_limit', self.daily_limit_warning)
            if self.total_sent_session >= daily_limit:
                self.log_event("SYSTEM", "WARNING", f"Daily limit of {daily_limit} reached. Stopping.")
                if self.ui_callback: self.ui_callback("LIMIT_REACHED", "Limit reached.")
                break

            # Generate message
            message = message_generator.generate_message(lead)
            # Send message
            success = self._send_single_message(phone, message)
            
            if success:
                self.total_sent_session += 1
                messages_since_break += 1
                lead['status'] = 'Sent'
                self.log_event(phone, "Sent", "Message delivered")
                if self.ui_callback: self.ui_callback(lead.get('id'), "Sent")
                
                # Check for break
                if messages_since_break >= settings.get('break_after', 25):
                    break_dur = random.randint(settings.get('break_min', 120), settings.get('break_max', 300))
                    self.log_event("SYSTEM", "INFO", f"Taking a break for {break_dur} seconds...")
                    self._sleep_with_interrupt(break_dur)
                    messages_since_break = 0
                else:
                    # Normal delay
                    delay = random.randint(settings.get('min_delay', 10), settings.get('max_delay', 30))
                    self._sleep_with_interrupt(delay)
                    
            else:
                lead['status'] = 'Failed'
                self.log_event(phone, "Failed", "Could not send message")
                if self.ui_callback: self.ui_callback(lead.get('id'), "Failed")

        self.is_running = False
        if self.ui_callback: self.ui_callback("COMPLETED", "All tasks finished.")

    def _send_single_message(self, phone, message):
        # We navigate to the chat without pre-filling text to allow for human-like typing simulation
        url = f"https://web.whatsapp.com/send?phone={phone}"
        try:
            self.driver.get(url)
            
            start_time = time.time()
            timeout = 45 
            
            # 1. Wait for message box to appear
            msg_box = None
            while time.time() - start_time < timeout:
                if self.stop_requested: return False
                
                # Check for invalid number
                invalid_selectors = [
                    (By.XPATH, '//div[contains(text(), "invalid")]'),
                    (By.XPATH, '//div[contains(text(), "ফোন নম্বরটি")]'),
                    (By.XPATH, "//*[contains(text(), 'Phone number shared via url is invalid')]")
                ]
                for selector in invalid_selectors:
                    try:
                        inv = self.driver.find_element(*selector)
                        if inv.is_displayed():
                            self.log_event(phone, "Failed", "Invalid phone number")
                            return False
                    except: pass

                try:
                    msg_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                    if msg_box.is_displayed():
                        break
                except:
                    pass
                time.sleep(1)

            if not msg_box:
                return False

            # 2. Random Behavioral Simulation (Move mouse, maybe scroll)
            self._simulate_human_behavior()

            # 3. Simulate Typing
            time.sleep(random.uniform(1.0, 2.5))
            self._type_human_like(msg_box, message)
            
            # 4. Find and click Send
            time.sleep(random.uniform(0.5, 1.5))
            send_selectors = [
                (By.XPATH, '//span[@data-icon="send"]'),
                (By.XPATH, '//button[@aria-label="Send"]'),
                (By.CSS_SELECTOR, "button[aria-label='Send']")
            ]
            
            for selector in send_selectors:
                try:
                    btn = self.driver.find_element(*selector)
                    if btn.is_displayed():
                        # JS Click for reliability
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(random.uniform(2.0, 4.0))
                        return True
                except: pass

            # Fallback to Enter
            msg_box.send_keys(Keys.ENTER)
            time.sleep(3)
            return True
                
        except Exception as e:
            self.log_event(phone, "Error", str(e))
            return False

    def _type_human_like(self, element, text):
        """Types text character by character with random delays."""
        for char in text:
            element.send_keys(char)
            # Random delay between 0.05 and 0.2 seconds per char
            time.sleep(random.uniform(0.02, 0.12))
        time.sleep(random.uniform(0.5, 1.0))

    def _simulate_human_behavior(self):
        """Occasionally performs random actions to look like a human."""
        self.behavior_counter += 1
        
        # Every 5 messages, do something 'human'
        if self.behavior_counter % 5 == 0:
            try:
                # Scroll the sidebar slightly
                sidebar = self.driver.find_element(By.ID, "pane-side")
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 200;", sidebar)
                time.sleep(random.uniform(1.0, 2.0))
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop - 100;", sidebar)
            except: pass
            
        # Every 10 messages, take a slightly longer 'thinking' pause
        if self.behavior_counter % 10 == 0:
            self.log_event("SYSTEM", "INFO", "Simulating natural user pause...")
            time.sleep(random.uniform(10, 25))

    def _sleep_with_interrupt(self, duration):
        """Sleeps for duration but can be interrupted by stop_requested or paused. Resilient to system sleep."""
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.stop_requested:
                break
            while self.is_paused and not self.stop_requested:
                time.sleep(0.5)
                # Extend the start time so pause duration doesn't count against sleep duration
                start_time += 0.5
            time.sleep(0.5)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.stop_requested = True
        self.is_paused = False # Unpause to allow exit

    def _check_and_reply_unread(self, ai_module):
        """Scans the chat list for unread messages and sends an AI reply."""
        try:
            # Find elements with unread message badge
            unread_badges = self.driver.find_elements(By.XPATH, '//span[@aria-label and contains(@aria-label, "unread message")]')
            
            for badge in unread_badges:
                try:
                    # Click the chat to open it
                    self.driver.execute_script("arguments[0].click();", badge)
                    time.sleep(2)
                    
                    # Get the incoming messages
                    messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]//span[@dir="ltr"]')
                    if messages:
                        last_message = messages[-1].text
                        self.log_event("AI_SYSTEM", "INFO", f"Received: {last_message}")
                        
                        # Generate AI reply
                        reply_text = ai_module.generate_smart_reply(last_message)
                        
                        if reply_text:
                            # Find text box and send
                            msg_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                            self._type_human_like(msg_box, reply_text)
                            msg_box.send_keys(Keys.ENTER)
                            self.log_event("AI_SYSTEM", "INFO", "Smart reply sent.")
                            time.sleep(2)
                except Exception as e:
                    print(f"Error handling unread chat: {e}")
                    
        except Exception as e:
            pass # Ignore if no unread messages or sidebar not found

    def add_to_group(self, group_name, phone_list):
        """
        Batch adds a list of phones to a specific WhatsApp Group.
        Requires the user to be an admin of the group.
        """
        self.is_running = True
        self.stop_requested = False
        
        if not self.initialize_driver():
            if self.ui_callback:
                self.ui_callback("SYSTEM_ERROR", "Failed to initialize browser.")
            self.is_running = False
            return
            
        try:
            self.log_event("SYSTEM", "INFO", f"Searching for group: {group_name}")
            # Focus search box and search for group
            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            search_box.clear()
            self._type_human_like(search_box, group_name)
            time.sleep(2)
            
            # Click the group
            group_element = self.driver.find_element(By.XPATH, f'//span[@title="{group_name}"]')
            group_element.click()
            time.sleep(2)
            
            # Click group header to open info
            header = self.driver.find_element(By.XPATH, '//header//div[@role="button"]')
            header.click()
            time.sleep(2)
            
            # Click Add participant
            add_participant_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Add participant")]'))
            )
            add_participant_btn.click()
            time.sleep(2)
            
            # Type each number and select
            participant_search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
            )
            
            added_count = 0
            for phone in phone_list:
                if self.stop_requested: break
                
                participant_search.clear()
                self._type_human_like(participant_search, phone)
                time.sleep(1.5)
                
                try:
                    # Select the first result
                    result = self.driver.find_element(By.XPATH, '//div[@role="button"]//span[@title]')
                    result.click()
                    self.log_event(phone, "Group Add", f"Queued for {group_name}")
                    added_count += 1
                except:
                    self.log_event(phone, "Group Add Failed", "Contact not found or not in address book")
                
                time.sleep(1)
                
            # Click confirm button to add all selected
            if added_count > 0:
                confirm_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="checkmark-light"]')
                confirm_btn.click()
                time.sleep(1)
                
                # Sometimes there's a second confirmation modal
                try:
                    final_confirm = self.driver.find_element(By.XPATH, '//button//div[contains(text(), "Add")]')
                    final_confirm.click()
                except: pass
                
                self.log_event("SYSTEM", "INFO", f"Successfully added {added_count} participants to {group_name}")
            
        except Exception as e:
            self.log_event("SYSTEM", "ERROR", f"Group add failed: {e}")
            
        self.is_running = False
        if self.ui_callback:
            self.ui_callback("COMPLETED", "Group addition process finished.")

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

