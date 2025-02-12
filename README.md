# 📩 WhatsApp Message - Automated Messaging via Selenium

This Python library automates **sending WhatsApp messages** using the **Chromium web browser** and **Selenium**.  
It allows bulk messaging, session management, and headless operation for automation purposes.

---

## 🚀 Features
✅ **Send messages via WhatsApp Web**  
✅ **Supports multiple phone numbers**  
✅ **Session management (Login & Logout)**  
✅ **Headless mode for automation**  
✅ **Planned Excel integration** 📌 (Upcoming Feature)  
✅ **Bulk messaging & group support** 📌 (Upcoming Feature)  

---

## 🛠️ Installation
First, install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 📖 Help & Command-Line Usage

```bash
usage: WhatsApp_Selenium.py [-h] [--logout] [--login LOGIN] [--session] [--hide] [--numbers NUMBERS [NUMBERS ...]] [--message MESSAGE]

Send WhatsApp messages using Selenium (Chrome).

options:
  -h, --help            Show this help message and exit.
  --logout              Logout from WhatsApp Web and clear session.
  --login LOGIN         Login with a phone number (without country code).
  --session             Check active session.
  --hide                Run in headless mode. ⚠️ Do not use while logging in!
  --numbers NUMBERS [NUMBERS ...]
                        List of phone numbers to send the message to.
  --message MESSAGE     Message to be sent.
```

---

## 📌 Usage

### 🔑 1. **Login to WhatsApp**
```bash
python3 WhatsApp_Selenium.py --login {phone_number}
```

After running this command, scan the QR code in the opened **Chrome** browser to authenticate.

---

### 📩 2. **Send Messages**
```bash
python3 WhatsApp_Selenium.py --numbers {phone_number_1} {phone_number_2} --message "Test message" --hide
```
- `--hide` → Runs **without opening the browser** (headless mode).  
- `--numbers` → List of **one or more phone numbers** to send the message to.  

---

## 🏗️ TODO List
- 🔲 **Remove GUI dependency** for complete headless operation.
- 🔲 **Support for messages via Excel tables.**
- 🔲 **Enable message sending to WhatsApp groups.**  

---

## 📝 Change Log

### 🆕 **2024-12-12**
- **Changed:** Selectors moved to global variables.
- **Updated:** `chrome_data_dir` path.

### 🆕 **2024-09-27**
- **Created:** Initial repository setup.

---

## 🤝 Contributing
Pull requests are welcome! 🚀  
For major changes, please open an issue first to discuss the feature.

---

## 📜 License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Connect with Me
[![LinkedIn](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kemal-kondak%C3%A7%C4%B1-b62173157/)
