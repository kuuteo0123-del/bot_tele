# 🤖 BOT SĂN CODE - TELEGRAM v3.9 [FIXED]

## ✨ Tính Năng
- ✅ Firefox persistent profiles (lưu cookies vĩnh viễn)
- ✅ Desktop viewport 1024x768
- ✅ Tự động detect input fields
- ✅ Anti-detection + stealth mode
- ✅ Database tracking
- ✅ Rate limiting
- ✅ Nhanh 5x (3-5s mở browser)

---

## 📋 CÁCH CHẠY

### **Lần Đầu Tiên (Setup):**

#### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
playwright install firefox
```

#### Bước 2: Verify Cloudflare (Bắt buộc lần đầu)
```bash
python manual_browser.py
```
**Hướng dẫn:**
1. Nhập username hoặc `all` để mở tất cả
2. Mỗi browser sẽ mở cửa sổ Firefox
3. **Đợi Cloudflare verify** (click checkbox)
4. Giải Captcha nếu có
5. Form tải xong = OK
6. **KHÔNG đóng browser này!**
7. Cookies được lưu vĩnh viễn ✅

#### Bước 3: Mở Terminal/CMD Mới
Tại đây bạn chạy bot:
```bash
python run_with_open_browser.py
```

Bot sẽ:
- Kết nối đến persistent profiles
- Lắng nghe tin nhắn Telegram
- Tự động submit code khi có message

---

### **Lần Tới (Không cần setup lại):**

Chỉ cần chạy:
```bash
python run_with_open_browser.py
```

✅ Không cần verify Cloudflare lại (cookies đã lưu)
✅ Mở luôn cửa sổ nhập code
✅ Bot tự động submit

---

## 🔧 CẤU HÌNH

### File: `config.py`

```python
# Telegram
API_ID = 20451785
API_HASH = 'f93e22ca85ce0e5c107e5a8027eb4bf4'
SESSION_NAME = 'session_bot_full'

# Browser
BROWSER_TYPE = "firefox"
VIEWPORT_WIDTH = 1024
VIEWPORT_HEIGHT = 768
HEADLESS_MODE = False  # Hiển thị UI

# Channels & Accounts
CHANNEL_CONFIG = {
    -1003134541072: {
        "name": "MM88VIP",
        "url": "https://mm88code.com",
        "accounts": [
            {"username": "dad131"},
            {"username": "kaoboy012"},
        ]
    },
    # ... Thêm channels khác
}

# Speed
MIN_DELAY_BETWEEN_SUBMITS = 0.8
MAX_CONCURRENT_SUBMITS = 3
```

---

## 📁 Cấu Trúc Files

```
bot_tele/
├── run_with_open_browser.py      👈 CHẠY CÁI NÀY
├── manual_browser.py              👈 Setup lần đầu
├── main_script.py                 (Tự động mở browser - không dùng)
├── config.py                      (Cấu hình)
├── database.py                    (Lưu history)
├── code_validator.py              (Kiểm tra code)
├── HoSo_Bot_Vip/                  (Folder profiles)
│   └── browser_profiles/
│       ├── dad131/                (Cookies & settings lưu đây)
│       ├── kaoboy012/
│       └── ...
└── requirements.txt
```

---

## 🚨 Lỗi Thường Gặp

### ❌ "Không tìm thấy persistent profiles"
**Giải pháp:** Chạy `python manual_browser.py` trước

### ❌ "Không tìm input fields"
**Giải pháp:** 
- Thêm selector mới trong `find_input_fields()`
- Hoặc edit `CODE_BLACKLIST` nếu code bị lọc

### ❌ "Cloudflare không pass"
**Giải pháp:**
- Firefox thường pass tốt hơn Chromium
- Thêm delay `MIN_DELAY_BETWEEN_SUBMITS = 1.0`

---

## 📊 Database

Tất cả submissions được lưu trong `data/code_history.db`:

```
Columns:
- code          : Code được submit
- username      : Username submit
- url           : Website submit
- status        : SUCCESS/FAILED
- timestamp     : Thời gian submit
```

Xem database:
```bash
python -c "from database import get_database; db=get_database(); print(db.get_submission_history())"
```

---

## 🎯 Workflow

```
1. Chạy manual_browser.py
   ↓
2. Verify CF một lần
   ↓
3. Profiles được lưu (persistent)
   ↓
4. Chạy run_with_open_browser.py
   ↓
5. Bot lắng nghe Telegram
   ↓
6. Message code → Auto submit (3-5s xong)
   ↓
7. Lần tới chỉ cần chạy step 4 (không setup lại)
```

---

## ⚡ Performance Tips

```python
# config.py

# Tăng tốc độ
MIN_DELAY_BETWEEN_SUBMITS = 0.5   # Min delay (s)
REQUESTS_PER_MINUTE = 60           # Max requests/min
MAX_CONCURRENT_SUBMITS = 5         # Parallel submits

# Giảm tải CPU
HEADLESS_MODE = True               # Ẩn UI
MAX_LOG_SIZE = 5000000             # Giảm log
```

---

## 🔐 Bảo Mật

✅ Session lưu trong `session_bot_full.session`
✅ Credentials từ `.env` (git ignored)
✅ Profiles persistent (không reset lại cookie)
✅ Stealth mode anti-detection

---

## 📞 Support

Lỗi? Check:
1. `logs/bot_activity.log` (chi tiết lỗi)
2. `data/code_history.db` (history submissions)
3. Terminal output (info real-time)

---

## 🎬 Version

**v3.9 - FIXED**
- ✅ Persistent profiles working
- ✅ Lỗi CDP connection fixed
- ✅ Input detection improved
- ✅ Database tracking OK

**Build:** 2026-05-23
**Browser:** Firefox (optimal CF bypass)
**Status:** Production Ready ✅
