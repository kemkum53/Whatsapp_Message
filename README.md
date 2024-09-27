# Whatspp Message

This library can send message using WhatsApp via chromium web browser

## Help
```bash
usage: WhatsApp_Selenium.py [-h] [--logout] [--login LOGIN] [--session] [--hide] [--numbers NUMBERS [NUMBERS ...]] [--message MESSAGE]

Send WhatsApp messages using Selenium (Chrome).

options:
  -h, --help            show this help message and exit
  --logout              Logout from WhatsApp Web and clear session
  --login LOGIN         Login with phone number. Please write phone number without country code
  --session             Check active session
  --hide                Hide browser. [WAR] Do not use when logging in!!
  --numbers NUMBERS [NUMBERS ...]
                        List of phone numbers to send the message to
  --message MESSAGE     Message to be sent
```

## Usage
### Login
```bash
python3 WhatsApp_Selenium.py --login {phone_number}
```
### Send Message
```bash
python3 WhatsApp_Selenium.py --numbers {phone_number_1} {phone_number_2} --message "Test message" --hide
```


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## TODO List
- Develop in a way that does not require a GUI.
- Message with using excel table


## Change Log
###  2024-27-09
- **Created** - Repository cereated.

## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kemal-kondak%C3%A7%C4%B1-b62173157/)