# 📖 BOT TELE v3.9 - SETUP GUIDE

## 🎯 Complete Setup for Windows

Hướng dẫn chi tiết cài đặt Bot Tele trên Windows với Virtual Environment.

---

## ✅ **PREREQUISITE (Yêu Cầu)**

### 1️⃣ **Python Installation**
- Download Python 3.9+ từ: https://www.python.org/downloads/
- **QUAN TRỌNG:** Check ✅ "Add Python to PATH" khi cài đặt
- Verify: Mở Command Prompt, gõ `python --version`

### 2️⃣ **Telegram Account**
- Cần có account Telegram
- Có quyền truy cập: https://my.telegram.org

### 3️⃣ **Get Telegram API Credentials**
1. Vào https://my.telegram.org/apps
2. Đăng nhập bằng số điện thoại Telegram
3. Tạo "New Application"
4. Lấy **API_ID** và **API_HASH**

---

## 🚀 **INSTALLATION STEPS**

### **Step 1: Clone Repository**

```bash
cd C:\Users\YourUsername\Desktop
git clone https://github.com/kuuteo0123-del/bot_tele.git
cd bot_tele
```

### **Step 2: Run Setup Script**

**Double-click** `setup.bat` hoặc mở Command Prompt:

```bash
setup.bat
```

**Điều này sẽ:**
- ✅ Tạo Virtual Environment (`venv/`)
- ✅ Cài đặt tất cả thư viện (requirements.txt)
- ✅ Cài đặt Playwright Firefox
- ✅ Tạo thư mục cần thiết (`logs/`, `data/`, `HoSo_Bot_Vip/`)
- ✅ Tạo file `.env` từ `.env.example`

**Output nên như sau:**
```
✅ Virtual environment created
✅ Directories created
✅ .env created from .env.example
✅ SETUP COMPLETE!
```

### **Step 3: Configure .env File**

Mở file `.env` (tạo được từ setup.bat):

```env
# 🔑 TELEGRAM CREDENTIALS (BẮT BUỘC)
API_ID=YOUR_API_ID_HERE
API_HASH=YOUR_API_HASH_HERE
SESSION_NAME=session_bot_full

# 📝 LOGGING
LOG_LEVEL=INFO

# 🔄 BATCH PROCESSING
BATCH_MODE_ENABLED=True
BATCH_SIZE=5

# ... các config khác
```

**Điền thông tin:**
- `API_ID` → Lấy từ https://my.telegram.org
- `API_HASH` → Lấy từ https://my.telegram.org
- Lưu file

---

## 🎯 **FIRST TIME SETUP**

### **Step 4: Verify Cloudflare (Bắt Buộc Lần Đầu)**

Mở Command Prompt **tại folder bot_tele**:

```bash
venv\Scripts\activate.bat
python manual_browser.py
```

**Hướng dẫn:**
1. Nhập username hoặc `all` để mở tất cả accounts
2. Firefox sẽ mở cửa sổ cho mỗi account
3. **Đợi Cloudflare verify** (click checkbox)
4. Giải Captcha nếu có
5. Form tải xong = ✅ OK
6. **KHÔNG đóng browser này!**

**Output:**
```
✅ Session created: session_bot_full.session
✅ Browser profiles saved:
   - HoSo_Bot_Vip/browser_profiles/dad131/
   - HoSo_Bot_Vip/browser_profiles/kaoboy012/
   - ...
```

Browser window sẽ **GIỮ NGUYÊN TRẠNG THÁI** và cookies được lưu vĩnh viễn ✅

### **Step 5: Run Bot**

**Double-click** `run.bat` hoặc:

```bash
run.bat
```

**Bot sẽ:**
- ✅ Kết nối đến browsers đã mở
- ✅ Lắng nghe tin nhắn Telegram
- ✅ Tự động submit code khi có message
- ✅ Track submission history trong database

**Output:**
```
✅ Connected to 3 browsers
✅ Telegram session valid: @your_username
✅ Bot ready - listening for messages...
📡 Waiting for codes...
```

---

## 📋 **LẦN TỚI (Không Cần Setup Lại)**

### **Quick Start**

Chỉ cần:

```bash
run.bat
```

**Điều này sẽ:**
- ✅ Activate venv tự động
- ✅ Kết nối đến existing browsers
- ✅ Load saved cookies
- ✅ Lắng nghe tin nhắn

**KHÔNG cần chạy `manual_browser.py` lại** vì cookies đã lưu! 🎉

---

## 🔧 **CONFIGURATION**

### **Edit config.py** (Optional)

Mở `config.py` để tuning:

```python
# Performance
MAX_CONCURRENT_SUBMITS = 3          # Tăng để submit nhanh hơn
MIN_DELAY_BETWEEN_SUBMITS = 0.8     # Giảm để nhanh, tăng để safe

# Batch Processing
BATCH_SIZE = 5                       # Xử lý 5 codes cùng lúc
BATCH_MODE_ENABLED = True           # Enable batch mode

# Health Check
HEALTH_CHECK_ENABLED = True         # Auto-recovery browsers
HEALTH_CHECK_INTERVAL = 60          # Check mỗi 60 giây

# Logging
LOG_LEVEL = 'INFO'                  # DEBUG, INFO, WARNING, ERROR
```

### **Add More Channels** (Optional)

Trong `config.py`, CHANNEL_CONFIG:

```python
CHANNEL_CONFIG = {
    # Channel hiện tại
    -1003134541072: { ... },
    
    # Thêm channel mới
    -1002345678901: {
        "name": "New Channel Name",
        "url": "https://newsite.com",
        "priority": 7,
        "accounts": [
            {"username": "user1", "priority": 1},
            {"username": "user2", "priority": 2}
        ]
    }
}
```

---

## 🐛 **TROUBLESHOOTING**

### ❌ **"Python not found"**
```
❌ Python is NOT installed!
   Please install Python 3.9+ from https://www.python.org
   Make sure to check "Add Python to PATH"
```

**Giải pháp:**
1. Cài Python từ https://www.python.org
2. ✅ Check "Add Python to PATH"
3. Restart Command Prompt
4. Chạy setup.bat lại

---

### ❌ **"Failed to create virtual environment"**

**Giải pháp:**
```bash
# Xóa venv cũ
rmdir /s /q venv

# Chạy setup.bat lại
setup.bat
```

---

### ❌ **"Playwright browser installation failed"**

**Giải pháp:**
```bash
venv\Scripts\activate.bat
python -m playwright install firefox
```

---

### ❌ **"CDP port is not responding"**

**Giải pháp:**
1. Chạy `manual_browser.py` trước
2. **Giữ Firefox windows mở**
3. Sau đó chạy `run.bat`

```bash
# Terminal 1: Run manual_browser.py
python manual_browser.py

# Terminal 2: Run bot
run.bat
```

---

### ❌ **"Session expired"**

**Giải pháp:**
```bash
# Xóa session cũ
del session_bot_full.session

# Chạy manual_browser.py lại để re-authenticate
python manual_browser.py
```

---

### ❌ **"Cannot find input fields"**

**Nguyên nhân:** Form HTML khác format

**Giải pháp:**
1. Check `logs/bot_activity.log` để xem error
2. Edit `input_finder.py` để thêm CSS selector mới
3. Hoặc edit `config.py` → `CODE_BLACKLIST` nếu code bị lọc

---

## 📊 **MONITORING**

### **Check Logs**

```bash
# Real-time log
type logs\bot_activity.log

# Xem history submissions
python -c "from database import get_database; db=get_database(); print(db.get_submission_history())"
```

### **Check Database**

```bash
# View submission history
data/code_history.db
```

### **Performance Stats**

Bot sẽ in ra mỗi 5 phút:

```
📊 PERFORMANCE REPORT
⏱️  Uptime: 300s
📈 submit_code:
   Total: 15 | Success: 14 | Failed: 1
   Avg: 3.245s | Min: 2.123s | Max: 5.678s
   Success Rate: 93.3%
```

---

## 🎬 **FULL WORKFLOW**

### **First Time (Setup)**
```
1. Run setup.bat
   ↓
2. Edit .env (add API_ID, API_HASH)
   ↓
3. Run manual_browser.py
   ↓
4. Verify Cloudflare (click checkbox)
   ↓
5. Cookies saved ✅
```

### **Then (Every Time)**
```
1. Run run.bat
   ↓
2. Bot connects to browsers
   ↓
3. Wait for Telegram messages
   ↓
4. Auto-submit codes
   ↓
5. View results in logs
```

---

## ⚡ **PERFORMANCE TIPS**

### **Tăng Tốc Độ**

```python
# config.py
MAX_CONCURRENT_SUBMITS = 5          # Tăng từ 3
MIN_DELAY_BETWEEN_SUBMITS = 0.5     # Giảm từ 0.8
BATCH_SIZE = 10                     # Tăng từ 5
HEADLESS_MODE = True                # Ẩn UI để chạy nhanh hơn
```

### **Giảm Lỗi (Safe Mode)**

```python
# config.py
MIN_DELAY_BETWEEN_SUBMITS = 1.5     # Tăng delay
MAX_CONCURRENT_SUBMITS = 1          # Chạy 1 lúc
PAGE_LOAD_MAX_RETRIES = 5           # Retry nhiều lần
```

---

## 📞 **SUPPORT**

Khi có lỗi, check:

1. **logs/bot_activity.log** - Chi tiết lỗi
2. **data/code_history.db** - History submissions  
3. **Terminal output** - Real-time info

---

## 📌 **IMPORTANT NOTES**

✅ **DO's:**
- ✅ Giữ Firefox windows mở khi chạy bot
- ✅ Set safe delays để tránh ban
- ✅ Monitor logs định kỳ
- ✅ Backup database nếu có dữ liệu quan trọng

❌ **DON'Ts:**
- ❌ Không đóng Firefox windows (mất session)
- ❌ Không chạy 2 bot cùng lúc trên 1 account
- ❌ Không submit quá nhiều codes (risk ban)
- ❌ Không edit config khi bot đang chạy

---

## 🎉 **Setup Complete!**

Nếu mọi thứ ✅ hoàn tất, bạn có thể:

```bash
# Lần sau chỉ cần
run.bat
```

Và bot sẽ **tự động** làm việc! 🚀

---

**Version:** v3.9 - ENHANCED  
**Last Updated:** 2026-05-23  
**Branch:** improvements/critical-fixes-and-enhancements
