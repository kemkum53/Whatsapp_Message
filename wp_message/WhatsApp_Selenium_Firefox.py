import os
import shutil
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchWindowException, NoSuchElementException
from colorama import Fore
from exceptions import TimeOutException, NotFoundException, LoginException, BrowserClosedException
import time
import argparse
import asyncio
import sys

'''Still work in progress'''

class WhatsApp_Selenium:
    def __init__(self, firefox_data_dir:str='./firefox-data'):
        self.hide_browser = True
        self.browser_open = False
        self.firefox_data_dir = firefox_data_dir
        self.driver = None
        
    def start_browser(self):
        try:
            '''Start browser and open WhatsApp Web.'''
            if not os.path.exists(self.firefox_data_dir):
                os.mkdir(self.firefox_data_dir)
            
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_preference('intl.accept_languages', 'en-US')
            firefox_options.add_argument('-profile')
            firefox_options.add_argument(self.firefox_data_dir)
            
            # Set visibility
            if self.hide_browser:
                firefox_options.add_argument('--headless')
            
            # Start Firefox
            self.driver = webdriver.Firefox(options=firefox_options)
            self.driver.get('https://web.whatsapp.com')
        except Exception as e:
            print(str(e))

    def close_browser(self):
        '''Close browser'''
        if self.driver:
            self.driver.quit()  

    def wait_qr(self):
        '''Check qr code is visible'''
        try:
            canvas_element = self.driver.find_element(By.CSS_SELECTOR, 'canvas[aria-label=\'Scan this QR code to link a device!\']')
            if canvas_element.is_displayed():
                return False
            else:
                return True
        except:
            return True

    def wait_chat_screen(self) -> bool:
        '''Wait for chat screen to load
            For while loop
            -> True (Chat screen not loaded)
            -> False (Chat screen loaded)'''
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'div[aria-label=\'New chat\']')
            return False
        except:
            return True

    async def wait_element(self, by:By, search_value:str, time_limit:int, ex_code:int):
        '''Wait for element to load with timer'''
        counter = 0
        while counter < time_limit:
            try:
                counter += 1
                element = self.driver.find_element(by, search_value)
                if element is not None:
                    return element
            except:
                time.sleep(1)
                
        raise TimeOutException('Element dosen\'t found...', ex_code) 

    async def session_status(self):
        '''Check active sessions
            -> False (not logged in)
            -> True (logged in)'''
        try:
            # Check data folder
            if not os.path.exists(self.firefox_data_dir):
                return False
            chat = await self.wait_element(By.CSS_SELECTOR, 'div[aria-label=\'New chat\']', 5, 1010)
            return True
        except TimeOutException as e:
            return False
        except Exception as e:
            raise e

    async def wait_loader(self):
        '''Wait for first loading page'''
        while True:
            try:
                loading_bar = self.driver.find_element(By.TAG_NAME, 'progress')
                time.sleep(1)
            except:
                break

    #region Main functions 
    async def login_via_numbber(self, number:str):
        try:
            self.start_browser() # Open browser
            
            print(f'{Fore.BLUE}[INF]{Fore.RESET} Waiting for page to load...')
            await self.wait_loader()
            
            print(f'{Fore.BLUE}[INF]{Fore.RESET} Checking login status...')
            if await self.session_status():
                print(f'{Fore.YELLOW}[WAR]{Fore.RESET} Already logged in.')
                return
            
            print(f'{Fore.BLUE}[INF]{Fore.RESET} Logging in with phone number...')
            # Wait for qr
            qr_code_counter = 0
            while self.wait_qr():
                qr_code_counter += 1
                time.sleep(1)
                if qr_code_counter >= 10:
                    raise TimeOutException('Page cannot loaded. Please try again...', 1001)                
            
            # Find and click 'Link with phone number' area
            button = await self.wait_element(By.XPATH, '//span[text()=\'Link with phone number\']', 5, 1002)
            button.click()
            time.sleep(1)
            
            # Find phone number input
            input_field = await self.wait_element(By.CSS_SELECTOR, 'input[aria-label=\'Type your phone number.\']', 5, 1003)
            input_field.send_keys(number)  # Fill with number
            
            # Click 'Next' button
            next_button = await self.wait_element(By.XPATH, '//div[text()=\'Next\']', 5, 1004)
            next_button.click()
            
            print(f'{Fore.BLUE}[INF]{Fore.RESET} Watigin for login code...')
            # Wait for code spans
            code_counter = 0
            while True:
                code_counter += 1
                try:
                    spans = await self.wait_element(By.CSS_SELECTOR, 'div[aria-label=\'Enter code on phone:\'] span', 1, 1005)
                    link_code_element = self.driver.find_element(By.CSS_SELECTOR, 'div[data-link-code]')
                    break
                except:
                    time.sleep(1)
                finally:
                    if code_counter >= 5:
                        raise TimeOutException('Code not found...', 1006)
            
            # If code spans found get the code
            link_code = link_code_element.get_attribute('data-link-code')
            link_code_parts = link_code.split(',')
            formatted_code = ''.join(link_code_parts[:4]) + '-' + ''.join(link_code_parts[4:])
            
            code_counter = 3 * 60 # Set timer 3mins
            print(f'{Fore.GREEN}To log in, please enter this code via WhatsApp:{Fore.RESET} {Fore.BLUE + formatted_code + Fore.RESET}')
            while True:
                mins, secs = divmod(code_counter, 60)
                timer = f'{mins:02d}:{secs:02d}'
                print(f'Remaining Time: {Fore.RED + timer + Fore.RESET}', end='\r')
                time.sleep(1)
                code_counter -= 1
                if code_counter <= 0:
                    raise TimeOutException('Code expired.', 1006)
                elif not self.wait_chat_screen():
                    print(Fore.GREEN + '[INF]' + Fore.RESET + f' - Loggin success.')
                    break
        except WebDriverException as e:
            raise BrowserClosedException(1000)
        except Exception as e:
            print(str(e))
        finally:
            self.close_browser()

    def logout(self):
        '''Logout function, Clear cache and close session'''
        try:
            # Delete data_dir
            if os.path.exists(self.firefox_data_dir):
                shutil.rmtree(self.firefox_data_dir)
            print(Fore.GREEN + '[SUC]' + Fore.RESET + f'Logged out.')
        except Exception as e:
            print(str(e))
    
    async def send_message(self, numbers:list, message:str):
        try:
            self.start_browser() # Open browser
            
            print(f'{Fore.BLUE}[INF]{Fore.RESET} Waiting for page to load...')
            await self.wait_loader()
            
            if not await self.session_status():
                print(f'{Fore.RED}[ERR]{Fore.RESET} Please login first.')
                return
            
            # Wait loading page
            new_chat_button = await self.wait_element(By.CSS_SELECTOR, 'div[aria-label=\'New chat\']', 5, 1011)
            time.sleep(1)
            new_chat_button.click()
            time.sleep(1)
            
            for number in numbers:
                number_input_field = await self.wait_element(By.CSS_SELECTOR, 'div[contenteditable=\'true\']', 5, 1012)
                for char in number:
                    number_input_field.send_keys(char)
                number_input_field.send_keys(Keys.ENTER)
                time.sleep(1)
                
                message_input_field = await self.wait_element(By.XPATH, '//div[@contenteditable="true" and @aria-placeholder="Type a message"]', 5, 1013)
                for char in message:
                    message_input_field.send_keys(char)
                message_input_field.send_keys(Keys.ENTER)
                time.sleep(1)
                
                print(Fore.GREEN + '[SUC]' + Fore.RESET + f'Message sended to: {number}')
                time.sleep(1)
        except WebDriverException as e:
            raise BrowserClosedException(1010)
        except Exception as e:
            print(e)
        finally:
            self.close_browser()
            
    async def is_logged_in(self):
        try:
            self.start_browser() # Open browser
            print(f'{Fore.BLUE}[INF]{Fore.RESET} Waiting for page to load...')
            await self.wait_loader()
            
            if not await self.session_status():
                print(f'{Fore.BLUE}[INF]{Fore.RESET} {Fore.RED}Not logged in.{Fore.RESET}')
            else:
                print(f'{Fore.BLUE}[INF]{Fore.RESET} {Fore.GREEN}Already logged in.{Fore.RESET}')
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
        parser = argparse.ArgumentParser(description="Send WhatsApp messages using Selenium.")
        parser.add_argument('--logout', action='store_true', help="Logout from WhatsApp Web and clear session")
        parser.add_argument('--login', type=str, help="Login with phone number. Please write phone number without country code")
        parser.add_argument('--session', action='store_true', help="Check active session")
        parser.add_argument('--show', action='store_true', help="Show browser")
        parser.add_argument('--numbers', nargs='+', required=False, help="List of phone numbers to send the message to")
        parser.add_argument('--message', type=str, required=False, help="Message to be sent")
        args = parser.parse_args()
        
        bot = WhatsApp_Selenium()
        
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            return
        
        if args.show:
            bot.hide_browser = False
            
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
            print(args.numbers)
            print(args.message)
            await bot.send_message(args.numbers, args.message)
            bot.close_browser()
            
    except:
        parser.print_help()
        return

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())