import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchWindowException, NoSuchElementException
from colorama import Fore
from exceptions import TimeOutException, NotFoundException, LoginException, BrowserClosedException
import time
import argparse
import asyncio
import sys

# "New Chat" icon on WhatsApp home screen
EN_NEW_CHAT_ELEMENT = [By.XPATH, "//button[@role='button' and @aria-label='New chat']", "//button[@role='button' and @aria-label='Yeni sohbet']"]

# Progress bar while uploading WhatsApp
LOADING_BAR = [By.TAG_NAME, "progress"]

# QR code on WhatsApp login screen
LOGIN_QR_CODE_ELEMENT = [By.CSS_SELECTOR, "canvas[aria-label=\'Scan this QR code to link a device!\']"]

# Log in with phone number button on WhatsApp login screen
EN_LOGIN_WITH_PHONE_ELEMENT = [By.XPATH, "//div[@role='button' and contains(normalize-space(.), 'Log in with phone number')]", "//div[@role='button' and contains(normalize-space(.), 'Telefon numarası kullanarak giriş yapın')]"]

# After pressing the button above, the phone number entry input appears.
EN_LOGIN_TYPE_PHONE_NUMBER_ELEMENT = [By.CSS_SELECTOR, "input[aria-label=\'Type your phone number.\']", "input[aria-label=\'Telefon numaranızı yazın.\']"]

# "Next" button on the number entry screen
EN_LOGIN_NEXT_BUTTON_ELEMENT = [By.XPATH, "//div[text()=\'Next\']", "//div[text()=\'İleri\']"]

# Wait element for the login code
EN_LOGIN_CODE_WAIT_ELEMENT = [By.CSS_SELECTOR, "div[aria-label=\'Enter code on phone:\'] span", "div[aria-label=\'Kodu telefonunuza girin:\'] span"]

# Login code element, contains the code
LOGIN_CODE_ELEMENT = [By.CSS_SELECTOR, "div[data-link-code]"]

# Search input on WhatsApp main screen
SEND_MESSAGE_PHONE_INPUT_ELEMENT = [By.XPATH, "//div[@contenteditable='true' and @role='textbox' and @aria-label='Search name or number']", "//div[@contenteditable='true' and @role='textbox' and @aria-label='Bir ad veya numara aratın']"]

# Message writing input on WhatsApp chat screen
EN_SEND_MESSAGE_TEXT_INPUT_ELEMENT = [By.CSS_SELECTOR, "div[aria-placeholder=\'Type a message\']", "div[aria-placeholder=\'Bir mesaj yazın\']"]

# The element that appears if the number is not found in the number search section
IS_PHONE_FOUND_ELEMENT = [By.XPATH, "//*[contains(text(), \'No results found for\')]", "//*[contains(text(), \'için sonuç bulunamadı\')]"]

# Add media button next to the message input in chat
ATTACH_BUTTON_ELEMENT = [By.XPATH, "//button[@type='button' and @title='Attach' and @data-tab='10']", "//button[@title=\'Ekle\' and @type=\'button\' and @aria-label=\'Ekle\']"]

# After clicking the media add button, click the "Images and Videos" button in the list that appears.
PHOTO_INPUT_ELEMENT = [By.XPATH, "//li[.//span[text()=\'Photos & videos\']]//input[@type=\'file\']", "//li[.//span[text()=\'Fotoğraflar ve Videolar\']]//input[@type=\'file\']"] 

# Input that appears after adding media
CAPTION_TEXTBOX_ELEMENT = [By.XPATH, "//div[@role=\'textbox\' and @aria-placeholder=\'Add a caption\']", "//div[@role=\'textbox\' and @aria-placeholder=\'Başlık ekleyin\']"] # For the with image messages

class WhatsApp_Selenium:
    def __init__(self, chrome_data_dir:str=f"{os.getenv('LOCALAPPDATA')}\\Google\\Chrome\\User Data\\Profile 1"):
        self.hide_browser = False
        self.browser_open = False
        self.chrome_data_dir = chrome_data_dir
        self.driver = None

    def start_browser(self):
        """Start browser and open WhatsApp Web."""
        if not os.path.exists(self.chrome_data_dir):
            os.mkdir(self.chrome_data_dir)
        chrome_options = Options()
        
        chrome_options.add_argument(f"--user-data-dir={self.chrome_data_dir}")  # Keep session infos
        
        # Set visibility
        if self.hide_browser:
            chrome_options.add_argument("--headless")
        
        # Start chrome
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get("https://web.whatsapp.com")

    def close_browser(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()  

    def wait_qr(self):
        """Check qr code is visible"""
        try:
            canvas_element = self.driver.find_element(LOGIN_QR_CODE_ELEMENT[0], LOGIN_QR_CODE_ELEMENT[1])
            if canvas_element.is_displayed():
                return False
            else:
                return True
        except:
            return True

    def wait_chat_screen(self) -> bool:
        """Wait for chat screen to load
            For while loop
            -> True (Chat screen not loaded)
            -> False (Chat screen loaded)"""
        for elem in EN_NEW_CHAT_ELEMENT[1:]:
            try:
                self.driver.find_element(EN_NEW_CHAT_ELEMENT[0], elem)
                return False
            except:
                continue
        return True

    async def wait_element(self, by:By, search_values:list[str], time_limit:int, ex_code:int):
        """Wait for element to load with timer"""
        counter = 0
        while counter < time_limit:
            counter += 1
            for elem in search_values:
                try:
                    element = self.driver.find_element(by, elem)
                    if element is not None:
                        return element
                except:
                    continue
            time.sleep(1)
                
        raise TimeOutException("Element dosen\'t found...", ex_code) 

    async def session_status(self):
        """Check active sessions
            -> False (not logged in)
            -> True (logged in)"""
        try:
            # Check data folder
            if not os.path.exists(self.chrome_data_dir):
                return False
            chat = await self.wait_element(EN_NEW_CHAT_ELEMENT[0], EN_NEW_CHAT_ELEMENT[1:], 5, 1010)
            return True
        except TimeOutException as e:
            return False
        except Exception as e:
            raise e

    async def wait_loader(self):
        """Wait for first loading page"""
        while True:
            try:
                loading_bar = self.driver.find_element(LOADING_BAR[0], LOADING_BAR[1])
                time.sleep(1)
            except:
                break

    #region Main functions 
    async def login_via_numbber(self, number:str):
        try:
            self.start_browser() # Open browser
            
            print(f"{Fore.BLUE}[INF]{Fore.RESET} Waiting for page to load...")
            await self.wait_loader()
            
            print(f"{Fore.BLUE}[INF]{Fore.RESET} Checking login status...")
            if await self.session_status():
                print(f"{Fore.YELLOW}[WAR]{Fore.RESET} Already logged in.")
                return
            
            print(f"{Fore.BLUE}[INF]{Fore.RESET} Logging in with phone number...")
            # Wait for qr
            qr_code_counter = 0
            while self.wait_qr():
                qr_code_counter += 1
                time.sleep(1)
                if qr_code_counter >= 10:
                    raise TimeOutException("Page cannot loaded. Please try again...", 1001)                
            
            # Find and click 'Link with phone number' area
            button = await self.wait_element(EN_LOGIN_WITH_PHONE_ELEMENT[0], EN_LOGIN_WITH_PHONE_ELEMENT[1:], 5, 1002)
            button.click()
            time.sleep(1)
            
            # Find phone number input
            input_field = await self.wait_element(EN_LOGIN_TYPE_PHONE_NUMBER_ELEMENT[0], EN_LOGIN_TYPE_PHONE_NUMBER_ELEMENT[1:], 5, 1003)
            input_field.send_keys(number)  # Fill with number
            
            # Click 'Next' button
            next_button = await self.wait_element(EN_LOGIN_NEXT_BUTTON_ELEMENT[0], EN_LOGIN_NEXT_BUTTON_ELEMENT[1:], 5, 1004)
            next_button.click()
            
            print(f"{Fore.BLUE}[INF]{Fore.RESET} Watigin for login code...")
            # Wait for code spans
            code_counter = 0
            while True:
                code_counter += 1
                try:
                    spans = await self.wait_element(EN_LOGIN_CODE_WAIT_ELEMENT[0], EN_LOGIN_CODE_WAIT_ELEMENT[1:], 1, 1005)
                    link_code_element = self.driver.find_element(LOGIN_CODE_ELEMENT[0], LOGIN_CODE_ELEMENT[1])
                    break
                except:
                    time.sleep(1)
                finally:
                    if code_counter >= 5:
                        raise TimeOutException("Code not found...", 1006)
            
            # If code spans found get the code
            link_code = link_code_element.get_attribute("data-link-code")
            link_code_parts = link_code.split(",")
            formatted_code = "".join(link_code_parts[:4]) + "-" + "".join(link_code_parts[4:])
            
            code_counter = 3 * 60 # Set timer 3mins
            print(f"{Fore.GREEN}To log in, please enter this code via WhatsApp:{Fore.RESET} {Fore.BLUE + formatted_code + Fore.RESET}")
            while True:
                mins, secs = divmod(code_counter, 60)
                timer = f"{mins:02d}:{secs:02d}"
                print(f"Remaining Time: {Fore.RED + timer + Fore.RESET}", end="\r")
                time.sleep(1)
                code_counter -= 1
                if code_counter <= 0:
                    raise TimeOutException("Code expired.", 1006)
                elif not self.wait_chat_screen():
                    print(Fore.GREEN + "[INF]" + Fore.RESET + f" - Loggin success.")
                    break
        except WebDriverException as e:
            raise BrowserClosedException(1000)
        except Exception as e:
            print(str(e))
        finally:
            self.close_browser()

    def logout(self):
        """Logout function, Clear cache and close session"""
        try:
            #TODO logout with using whatsapp logout
            # Delete data_dir
            if os.path.exists(self.chrome_data_dir):
                shutil.rmtree(self.chrome_data_dir)
            print(Fore.GREEN + "[SUC]" + Fore.RESET + f"Logged out.")
        except Exception as e:
            print(str(e))
    
    async def send_message(self, numbers:list, message:str, media:list=None):
        try:
            self.start_browser() # Open browser

            print(f"{Fore.BLUE}[INF]{Fore.RESET} Waiting for page to load...")
            await self.wait_loader()
            
            if not await self.session_status():
                print(f"{Fore.RED}[ERR]{Fore.RESET} Please login first.")
                return
            
            # Wait loading page
            new_chat_button = await self.wait_element(EN_NEW_CHAT_ELEMENT[0], EN_NEW_CHAT_ELEMENT[1:], 5, 1011)
            time.sleep(1)
            new_chat_button.click()
            time.sleep(1)
            
            print(Fore.BLUE + "[INF]" + Fore.RESET + f"Messages sending...")
            for number in numbers:
                number_input_field = await self.wait_element(SEND_MESSAGE_PHONE_INPUT_ELEMENT[0], SEND_MESSAGE_PHONE_INPUT_ELEMENT[1:], 5, 1012)
                number_input_field.send_keys(number)
                
                try:
                    phone_found = await self.wait_element(IS_PHONE_FOUND_ELEMENT[0], IS_PHONE_FOUND_ELEMENT[1:], 2, 1032)
                    print(Fore.RED + "[ERR]" + Fore.RESET + f"Number not found: {number}")
                    number_input_field.send_keys(Keys.ESCAPE)
                    continue
                except TimeOutException: # If get timeout exception that means number is valid. So continue to process.
                    pass
                except BrowserClosedException as e:
                    raise BrowserClosedException(1010)

                number_input_field.send_keys(Keys.ENTER)
                time.sleep(1)
                
                if media:
                    attach_button = await self.wait_element(ATTACH_BUTTON_ELEMENT[0], ATTACH_BUTTON_ELEMENT[1:], 5, 1033)
                    attach_button.click()
                    await asyncio.sleep(0.5)
                    
                    photo_input = await self.wait_element(PHOTO_INPUT_ELEMENT[0], PHOTO_INPUT_ELEMENT[1:], 5, 1034)
                    photo_input.send_keys("\n".join(media))
                    await asyncio.sleep(0.5)
                    
                    message_input_field = await self.wait_element(CAPTION_TEXTBOX_ELEMENT[0], CAPTION_TEXTBOX_ELEMENT[1:], 5, 1035)
                    message_input_field.send_keys(Keys.ENTER)
                    await asyncio.sleep(0.5)

                message_input_field = await self.wait_element(EN_SEND_MESSAGE_TEXT_INPUT_ELEMENT[0], EN_SEND_MESSAGE_TEXT_INPUT_ELEMENT[1:], 5, 1013)
                message_input_field.send_keys(message)
                time.sleep(1)
                message_input_field.send_keys(Keys.ENTER)
                time.sleep(1)
                
                print(Fore.GREEN + "[SUC]" + Fore.RESET + f"Message sended to: {number}")
                time.sleep(1)
        except WebDriverException as e:
            raise BrowserClosedException(1010)
        except Exception as e:
            print(str(e))
        finally:
            self.close_browser()
            
    async def is_logged_in(self):
        try:
            self.start_browser() # Open browser
            
            print(f"{Fore.BLUE}[INF]{Fore.RESET} Waiting for page to load...")
            await self.wait_loader()
            
            if not await self.session_status():
                print(f"{Fore.BLUE}[INF]{Fore.RESET} {Fore.RED}Not logged in.{Fore.RESET}")
            else:
                print(f"{Fore.BLUE}[INF]{Fore.RESET} {Fore.GREEN}Already logged in.{Fore.RESET}")
        except WebDriverException as e:
            raise BrowserClosedException(1020)
        except Exception as e:
            print(str(e))
        finally:
            self.close_browser()
    
    #TODO message with using excel table
    #endregion
    
async def main():
    try:
        # Argparse to handle command line inputs
        parser = argparse.ArgumentParser(description="Send WhatsApp messages using Selenium (Chrome).")
        parser.add_argument("--logout", action="store_true", help="Logout from WhatsApp Web and clear session")
        parser.add_argument("--login", type=str, help="Login with phone number. Please write phone number without country code")
        parser.add_argument("--session", action="store_true", help="Check active session")
        parser.add_argument("--hide", action="store_true", help=f"Hide browser. {Fore.RED}[WAR] Do not use when logging in!!{Fore.RESET}")
        parser.add_argument("--numbers", nargs="+", required=False, help="List of phone numbers to send the message to")
        parser.add_argument("--message", type=str, required=False, help="Message to be sent")
        parser.add_argument("--media", nargs="+", required=False, help="Paths to media files to be sent")
        args = parser.parse_args()
        
        bot = WhatsApp_Selenium()
        
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            return
        
        if args.hide:
            bot.hide_browser = True
            
        if args.session:
            await bot.is_logged_in()
            return
        
        if args.logout:
            bot.logout()
            return
        
        if args.login:
            await bot.login_via_numbber(args.login)
            return

        if args.numbers and args.message:
            await bot.send_message(args.numbers, args.message, args.media)
    except:
        # parser.print_help()
        return

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())