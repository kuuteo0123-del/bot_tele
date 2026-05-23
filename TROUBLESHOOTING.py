"""
🔧 TROUBLESHOOTING GUIDE - BOT v3.6.2
Hướng dẫn fix toàn bộ vấn đề phổ biến
"""

# ==========================================
# ✅ QUICK CHECKLIST (10 bước)
# ==========================================

QUICK_CHECKLIST = """
┌─────────────────────────────────────────┐
│  📋 QUICK CHECKLIST (10 BƯỚC)           │
└─────────────────────────────────────────┘

□ 1. Python version >= 3.8?
   Terminal: python --version
   Expected: Python 3.8+

□ 2. Virtual environment đã activate?
   Terminal: venv\Scripts\activate  (Windows)
   Terminal: source venv/bin/activate (Linux/Mac)
   Sign: (venv) ở đầu terminal

□ 3. Requirements đã install?
   Terminal: pip install -r requirements.txt
   Check: pip list | grep telethon

□ 4. .env file có tồn tại?
   File: .env (trong thư mục bot_san_code)
   Có: API_ID, API_HASH, SESSION_NAME

□ 5. Config.py có đúng format?
   File: config.py
   Check: CHANNEL_CONFIG có format -100XXXXX

□ 6. Browser installed?
   Terminal: playwright install chromium
   Folder: ~/.cache/ms-playwright/chromium-*

□ 7. Session file tồn tại?
   File: session_bot_full.session (sau khi login lần 1)
   Size: > 1 KB

□ 8. Channel ID đúng?
   Format: -100XXXXX (13 ký tự)
   Không: 1001234567890 (sai)
   Không: XXXXX (sai)

□ 9. Bot được add vào channel?
   Check: Mở Telegram → channel → members → tìm bot

□ 10. Logs folder tồn tại?
    Folder: logs/ (tự tạo khi chạy)
    File: logs/bot_activity.log

✅ Nếu tất cả ✓ → Chạy: python run.py
❌ Nếu không → Xem PROBLEMS phía dưới
"""

# ==========================================
# 🔴 PROBLEM #1: HANDLER KHÔNG SETUP
# ==========================================

PROBLEM_1 = """
┌─────────────────────────────────────────┐
│  ❌ PROBLEM #1: HANDLER KHÔNG SETUP     │
└─────────────────────────────────────────┘

❌ DẤU HIỆU:
   • Bot chạy OK nhưng không nhận message
   • Logs không in "👀 Vừa có tin nhắn"
   • Gửi code vào channel nhưng bot không phản ứng

✗ NGUYÊN NHÂN:
   • Handler setup TRƯớc client.start()
   • Handler đang ở trong init_systems() → Sai thứ tự
   • Handler setup nhiều lần → Không hoạt động

🔧 FIX NGAY:
   Step 1: Mở file: main_script.py
   Step 2: Tìm dòng: @client.on(events.NewMessage())
   Step 3: Xóa decorators OLD (@client.on...)
   Step 4: Thêm hàm mới: async def setup_telegram_handler()
   Step 5: Gọi: await setup_telegram_handler() TRONG main()
   Step 6: Gọi AFTER: await client.start()
   Step 7: Save & run: python run.py

💡 DEBUG TIP:
   • Xem logs: grep "SETTING UP TELEGRAM" logs/bot_activity.log
   • Expected: "SETTING UP TELEGRAM EVENT HANDLERS"
   • Nếu không → Handler không được gọi

🎯 KỲ VỌNG SAU FIX:
   ✅ Logs in: "SETTING UP TELEGRAM EVENT HANDLERS"
   ✅ Logs in: "Event handlers setup complete!"
   ✅ Logs in: "👀 Vừa có tin nhắn nổ ở kênh ID: ..."
"""

# ==========================================
# 🔴 PROBLEM #2: SESSION KHÔNG HỢP LỆ
# ==========================================

PROBLEM_2 = """
┌─────────────────────────────────────────┐
│  ❌ PROBLEM #2: SESSION KHÔNG HỢP LỆ    │
└─────────────────────────────────────────┘

❌ DẤU HIỆU:
   • Logs in: "SESSION KHÔNG HỢP LỆ"
   • Error: 401 UNAUTHORIZED hoặc SESSION_INVALID
   • Không thể kết nối Telegram

✗ NGUYÊN NHÂN:
   • Session file bị corrupt
   • Session file bị xóa hoặc hết hạn
   • API credentials sai trong .env

🔧 FIX NGAY:
   Step 1: Xóa session file:
           rm session_bot_full.session
   
   Step 2: Kiểm tra .env:
           - API_ID: số (20451785)
           - API_HASH: string (f93e22ca85ce0e5c107e5a8027eb4bf4)
           - SESSION_NAME: session_bot_full
   
   Step 3: Chạy lại:
           python run.py
   
   Step 4: Làm theo hướng dẫn login:
           - Nhập phone number
           - Nhập OTP code từ Telegram
           - Xác nhận

💡 DEBUG TIP:
   • Kiểm tra .env có API_ID & API_HASH không
   • Kiểm tra session file size > 1 KB
   • Try: telethon-session-dump session_bot_full.session

🎯 KỲ VỌNG SAU FIX:
   ✅ Logs in: "✅ SESSION HỢP LỆ!"
   ✅ Logs in: "👤 Username: @your_username"
   ✅ Logs in: "🆔 User ID: XXXXX"
"""

# ==========================================
# 🔴 PROBLEM #3: BOT KHÔNG ĐƯỢC ADD VÀO CHANNELS
# ==========================================

PROBLEM_3 = """
┌─────────────────────────────────────────┐
│  ❌ PROBLEM #3: BOT KHÔNG ĐƯỢC ADD      │
│                VÀO CHANNELS             │
└─────────────────────────────────────────┘

❌ DẤU HIỆU:
   • Logs in: "❌ KHÔNG CÓ CHANNEL NÀO HỢP LỆ"
   • Logs in: "Channel không phải supergroup/channel"
   • Không tìm thấy entity với ID

✗ NGUYÊN NHÂN:
   • Bot chưa được add vào channel
   • Channel ID sai định dạng
   • Channel là private không có permissions
   • Bot không phải admin trong channel

🔧 FIX NGAY:
   Step 1: Kiểm tra format Channel ID:
           Đúng: -100XXXXXXXXXXXXX (13 số)
           Sai:  -100XXXXXXXXX (12 số)
           Sai:  XXXXXXXXXXXXX (không dấu -)
   
   Step 2: Mở Telegram, vào channel:
           • Nhấn vào tên channel
           • Settings → Members
           • Tìm account của bot
           • Nếu không có → Click "Add member"
   
   Step 3: Cấp quyền admin cho bot:
           • Channel settings → Administrators
           • Add member/bot
           • Grant: Post messages, Delete messages
   
   Step 4: Copy Channel ID đúng:
           • Channel → Right click → View channel info
           • Hoặc: Telegram app → More → Copy link
           • Link: https://t.me/c/XXXXXXXXXXXXX
           • Channel ID: -100XXXXXXXXXXXXX
   
   Step 5: Update config.py:
           CHANNEL_CONFIG = {
               -100XXXXXXXXXXXXX: {  # ← ID chính xác
                   "name": "Channel Name",
                   "url": "https://...",
                   "priority": 1,
                   "accounts": [...]
               }
           }
   
   Step 6: Save & run: python run.py

💡 DEBUG TIP:
   • Chạy: python run.py → Xem logs
   • Expected: "✅ Tìm thấy: MM88VIP"
   • Nếu thấy "❌" → Copy-paste Channel ID lại

🎯 KỲ VỌNG SAU FIX:
   ✅ Logs in: "✅ Tìm thấy: Channel Name"
   ✅ Logs in: "📍 ID: -100XXXXX"
   ✅ Logs in: "🌐 URL: https://..."
"""

# ==========================================
# 🔴 PROBLEM #4: CODE EXTRACTION SAI
# ==========================================

PROBLEM_4 = """
┌─────────────────────────────────────────┐
│  ❌ PROBLEM #4: CODE EXTRACTION SAI     │
└─────────────────────────────────────────┘

❌ DẤU HIỆU:
   • Logs in: "⚠️ KHÔNG CÓ CODE HỢP LỆ"
   • Bot tìm thấy codes nhưng không nhận diện
   • Codes bị lọc sai (blacklist too aggressive)

✗ NGUYÊN NHÂN:
   • Message không có code (chỉ hình ảnh/video)
   • Code format sai (< 8 hoặc > 12 ký tự)
   • Code bị filter vì trong CODE_BLACKLIST
   • Code là spoiler (✅ cần xử lý thêm)

🔧 FIX NGAY:
   Step 1: Kiểm tra message có code không:
           • Mở channel
           • Mở message gần nhất
           • Tìm code 8-12 ký tự
   
   Step 2: Kiểm tra CODE_BLACKLIST:
           File: config.py
           CODE_BLACKLIST = [
               "COM", "HTTP", "HTTPS", ...
           ]
           • Nếu code chứa từ này → bị lọc
           • Ví dụ: "CODE123" → bị lọc (có "CODE")
           • Fix: Xóa từ không cần từ BLACKLIST
   
   Step 3: Kiểm tra code length:
           File: config.py
           CODE_MIN_LENGTH = 6
           CODE_MAX_LENGTH = 15
           • Nếu code 16+ ký tự → bị lọc
           • Nếu code 5 ký tự → bị lọc
   
   Step 4: Enable debug logging:
           File: logger_setup.py
           LOG_LEVEL = 'DEBUG'  # ← Từ INFO sang DEBUG
           • Sẽ in thêm logs chi tiết extraction
   
   Step 5: Run & xem logs:
           python run.py
           → Xem "CODES ĐÃ TRÍCH XUẤT"
           → Nếu 0 codes → code extraction fail

💡 DEBUG TIP:
   • Tìm logs: grep "CODES ĐÃ TRÍCH XUẤT" logs/bot_activity.log
   • Check: Tổng tìm thấy vs Sau lọc
   • Nếu 0 sau lọc → Code bị loại bỏi

🎯 KỲ VỌNG SAU FIX:
   ✅ Logs in: "📋 CODES ĐÃ TRÍCH XUẤT"
   ✅ Logs in: "Tổng tìm thấy: X"
   ✅ Logs in: "Sau lọc: X"
   ✅ Logs in: "Codes: [CODE1, CODE2, ...]"
"""

# ==========================================
# 🔴 PROBLEM #5: BROWSER/CLOUDFLARE ISSUES
# ==========================================

PROBLEM_5 = """
┌─────────────────────────────────────────┐
│  ❌ PROBLEM #5: BROWSER/CLOUDFLARE      │
└─────────────────────────────────────────┘

❌ DẤU HIỆU:
   • Logs in: "❌ Lỗi Playwright"
   • Logs in: "CF thất bại"
   • Logs in: "❌ Page timeout"
   • Firefox windows không mở

✗ NGUYÊN NHÂN:
   • Playwright chưa install chromium
   • Firefox/Chromium chưa cài
   • CF bypass fail (javascript error)
   • Port 9222 bị chiếm (debugger port)

🔧 FIX NGAY:
   Step 1: Install Playwright browsers:
           python -m playwright install chromium
           → Sẽ download ~400MB Chromium
   
   Step 2: Kill Firefox processes:
           Windows: taskkill /F /IM firefox.exe
           Linux: killall firefox
           Mac: pkill firefox
   
   Step 3: Clear temp profiles:
           Windows: rmdir /S %temp%\bot_isolated_profiles
           Linux: rm -rf /tmp/bot_isolated_profiles
   
   Step 4: Kiểm tra PORT 9222:
           Windows: netstat -ano | findstr 9222
           Linux: lsof -i :9222
           Nếu có → Kill process chiếm port
   
   Step 5: Kiểm tra Firefox settings:
           • Nếu Firefox chạy ở chế độ guest
           • Profiles sẽ fail → Close hết Firefox
   
   Step 6: Run & xem:
           python run.py
           → Nên thấy Firefox windows mở

💡 DEBUG TIP:
   • Logs: grep "Playwright" logs/bot_activity.log
   • Expected: "✅ Playwright khởi tạo xong"
   • Nếu ❌ → Playwright chưa install
   
   • Logs: grep "Stealth browser" logs/bot_activity.log
   • Expected: "✅ Stealth browser mở: account"
   • Nếu ❌ → Firefox launch fail

🎯 KỲ VỌNG SAU FIX:
   ✅ Logs in: "✅ Playwright khởi tạo xong"
   ✅ Logs in: "✅ Stealth browser mở: username"
   ✅ Firefox windows xuất hiện
   ✅ Logs in: "✅ SẴN SÀNG!"
"""

# ==========================================
# 🆘 EMERGENCY FIXES (6 cách)
# ==========================================

EMERGENCY_FIXES = """
┌─────────────────────────────────────────┐
│  🆘 EMERGENCY FIXES (6 CÁCH)            │
└─────────────────────────────────────────┘

Nếu bot vẫn không hoạt động sau toàn bộ fixes trên:

🔧 FIX #1: SOFT RESET (nhẹ nhất)
   1. Dừng bot (Ctrl+C)
   2. Xóa logs: rm -rf logs/*
   3. Run lại: python run.py
   ✅ Giữ lại: session, database, profiles

🔧 FIX #2: SESSION RESET
   1. Dừng bot (Ctrl+C)
   2. Xóa session: rm session_bot_full.session
   3. Run lại: python run.py
   4. Login lại khi yêu cầu
   ✅ Giữ lại: database, profiles

🔧 FIX #3: VENV RESET
   1. Dừng bot (Ctrl+C)
   2. Xóa venv: rm -rf venv/
   3. Tạo mới: python -m venv venv
   4. Activate: venv\Scripts\activate (Windows)
   5. Install: pip install -r requirements.txt
   6. Install browsers: playwright install chromium
   7. Run: python run.py
   ✅ Giữ lại: session, database, profiles, configs

🔧 FIX #4: FULL CLEANUP
   1. Dừng bot (Ctrl+C)
   2. Xóa: rm -rf venv/ logs/ data/ backups/
   3. Xóa: rm session_bot_full.session
   4. Kill Firefox: taskkill /F /IM firefox.exe (Windows)
   5. Làm lại từ FIX #3
   ✅ Giữ lại: config.py, .env, requirements.txt

🔧 FIX #5: HARD RESET (nặng)
   1. Backup config.py & .env
   2. Xóa toàn bộ thư mục ngoài backup
   3. Tải lại source code
   4. Copy config.py & .env vào
   5. Tạo venv & install lại
   6. Run: python run.py
   ✅ Giữ lại: custom config & credentials

🔧 FIX #6: NUCLEAR OPTION (xóa hết)
   1. Xóa toàn bộ thư mục bot
   2. Tải lại source code
   3. Tạo mới .env với credentials
   4. Tạo venv & install
   5. Run: python run.py
   6. Login lại khi yêu cầu
   ⚠️ LƯU Ý: Mất toàn bộ database lịch sử

─────────────────────────────────────────
CHỌN FIX NÀO?
• Logs còn → FIX #1 hoặc #2
• Session fail → FIX #2 hoặc #3
• Venv corrupt → FIX #3
• Vẫn không → FIX #4 hoặc #5
• Cuối cùng → FIX #6
"""

# ==========================================
# ✅ EXPECTED LOGS (khi chạy đúng)
# ==========================================

EXPECTED_LOGS = """
┌─────────────────────────────────────────┐
│  ✅ EXPECTED LOGS (khi chạy đúng)       │
└─────────────────────────────────────────┘

🟢 STARTUP LOGS:
════════════════════════════════════════
🚀 KHỞI ĐỘNG BOT v3.6.2 (STEALTH + AUTO-SUBMIT + FAST)
════════════════════════════════════════
🔍 Quét Firefox processes hiện tại...
   Tìm thấy X Firefox processes
📊 Khởi tạo Database...
✅ Database khởi tạo xong
🛡️ Khởi tạo Anti-Detection (FAST DELAYS 0.8s)...
✅ Anti-Detection khởi tạo xong
📡 Khởi tạo Monitoring...
✅ Monitoring khởi tạo xong
📋 Khởi tạo Task System...
✅ Task System khởi tạo xong
🌐 Khởi tạo Playwright (Stealth Mode)...
✅ Playwright khởi tạo xong (Stealth Mode)
════════════════════════════════════════

🔐 SESSION VERIFICATION LOGS:
════════════════════════════════════════
🔐 XÁC MINH TELEGRAM SESSION...
✅ SESSION HỢP LỆ!
   👤 Username: @your_username
   🆔 User ID: XXXXX
   📝 Tên: Your Name
════════════════════════════════════════

📡 CHANNEL VERIFICATION LOGS:
════════════════════════════════════════
📡 XÁC MINH CHANNELS & LẤY IDs...
✅ Tìm thấy: MM88VIP Dịch Vụ Giai Nhân
   📍 ID: -1003134541072
   🌐 URL: https://mm88code.com
✅ Tìm thấy: LLwin ĐỈNH CAO CHIẾN THẮNG
   📍 ID: -1003859359508
   🌐 URL: https://llwincode.com
════════════════════════════════════════

📡 HANDLER SETUP LOGS:
════════════════════════════════════════
📡 SETTING UP TELEGRAM EVENT HANDLERS...
📡 REGISTERING HANDLERS FOR 3 CHANNELS:
   • -1003134541072: MM88VIP Dịch Vụ Giai Nhân
   • -1003859359508: LLwin ĐỈNH CAO CHIẾN THẮNG
   • -1002626603440: NEW88 PHÁT C.O.DE NỔ HŨ
✅ Event handlers setup complete!
════════════════════════════════════════

✅ BOT READY LOGS:
════════════════════════════════════════
✅ BOT SẴN SÀNG (v3.6.2 - STEALTH + AUTO-SUBMIT + FAST DELAYS)
Features: Fingerprint spoofing, webdriver bypass, 100% AUTO-SUBMIT
Delays: 0.8s min (TỐI ƯU HÓA ĐỂ KHÔNG MẤT LƯỢT)
════════════════════════════════════════

👀 MESSAGE RECEIVED LOGS (khi có message):
════════════════════════════════════════
👀 Vừa có tin nhắn nổ ở kênh ID: -1003134541072
📨 NHẬN MESSAGE TỪ CHANNEL
   Tên channel: MM88VIP Dịch Vụ Giai Nhân
   Channel ID: -1003134541072
   Website: https://mm88code.com
   Thời gian: 2026-05-19 14:30:45
   Message ID: 123456
════════════════════════════════════════

📋 CODE EXTRACTION LOGS:
════════════════════════════════════════
📋 CODES ĐÃ TRÍCH XUẤT
   Tổng tìm thấy: 5
   Sau lọc: 4
   Codes: [CODE1, CODE2, CODE3, CODE4]
════════════════════════════════════════

✅ CODE VALIDATION LOGS:
════════════════════════════════════════
✅ KẾT QUẢ KIỂM ĐỊNH CODE
   Codes hợp lệ: 4
   Codes không hợp lệ: 0
   Chi tiết:
      CODE1: Hợp lệ 100%
      CODE2: Hợp lệ 95%
════════════════════════════════════════

🌐 BROWSER INIT LOGS:
════════════════════════════════════════
🌐 KHỞI TẠO STEALTH BROWSERS...
📍 Mở stealth browser cho account_name
   Vị trí: (0, 0)
   Tạo 2 Firefox processes
✅ Stealth browser mở: account_name
════════════════════════════════════════

🛡️ CF BYPASS LOGS:
════════════════════════════════════════
🛡️ CHUẨN BỊ BROWSERS XÓA XONG
   Cloudflare: ĐÃ BYPASS ✅
   Stealth Mode: ĐÃ BẬT ✅
   Trạng thái Account: ✅ Sẵn sàng (CF bypass)
════════════════════════════════════════

🚀 AUTO-SUBMIT LOGS:
════════════════════════════════════════
🚀 AUTO-SUBMIT 4 codes trong 2 giây...
🚀 AUTO-SUBMIT ĐÃ BẮTDẦU
   Tổng codes: 4
   Codes: [CODE1, CODE2, CODE3, CODE4]
   Accounts: [account1, account2, ...]
   Trạng thái: Sẽ bắt đầu trong 2 giây... ⏳
════════════════════════════════════════

✅ SUBMISSION LOGS:
════════════════════════════════════════
🚀 [account1] Gửi: CODE1
✅ [account1] THÀNH CÔNG (2.45s): Thành công
📊 KẾT QUẢ: 3/4 thành công
════════════════════════════════════════
"""

# ==========================================
# ❓ Q&A (Các câu hỏi thường gặp)
# ==========================================

Q_AND_A = """
┌─────────────────────────────────────────┐
│  ❓ Q&A - CÂU HỎI THƯỜNG GẶP            │
└─────────────────────────────────────────┘

❓ Q1: Bot chạy nhưng không nhận message?
✅ A1:
   • Kiểm tra: Logs in "👀 Vừa có tin nhắn"?
   • Không → Handler chưa setup (xem PROBLEM #1)
   • Có → Channel ID có đúng không? (xem PROBLEM #3)

❓ Q2: "SESSION KHÔNG HỢP LỆ" error?
✅ A2:
   • Xóa: rm session_bot_full.session
   • Run: python run.py
   • Login lại khi yêu cầu

❓ Q3: Bot bị crash khi submit code?
✅ A3:
   • Check: asyncio.timeout() có được support?
   • Python < 3.11 → Thay asyncio.timeout() bằng asyncio.wait_for()
   • Nếu lỗi: await asyncio.wait_for(lock.__aenter__(), timeout=5)

❓ Q4: Firefox không mở?
✅ A4:
   • Run: playwright install chromium
   • Kill firefox: taskkill /F /IM firefox.exe (Windows)
   • Check port: netstat -ano | findstr 9222

❓ Q5: Code không được trích xuất?
✅ A5:
   • Check: Message có chứa code 8-12 ký tự?
   • Check: Code có nằm trong BLACKLIST không?
   • Enable DEBUG logs để xem chi tiết

❓ Q6: Bot rất chậm?
✅ A6:
   • Normal delays 0.8s → OK
   • Nếu > 5s → Check CPU/Memory
   • Check: Có bao nhiêu Firefox processes?

❓ Q7: Database bị corrupt?
✅ A7:
   • Xóa: rm data/code_history.db
   • Bot sẽ tạo database mới
   • Lịch sử cũ sẽ mất (có backups/)

❓ Q8: Làm sao để reset toàn bộ?
✅ A8:
   • Soft reset: rm -rf logs/
   • Full reset: rm -rf venv/ logs/ data/
   • Nuclear: Xóa thư mục → Tải lại source

❓ Q9: Bot bao lâu sẽ nhận được message?
✅ A9:
   • Ngay lập tức khi có message trong channel
   • Nếu bot offline → Sẽ miss message
   • Nên giữ bot chạy 24/7

❓ Q10: Làm sao để tắt bot?
✅ A10:
   • Press: Ctrl+C
   • Bot sẽ cleanup resources
   • Firefox sẽ tắt
   • Database sẽ close

❓ Q11: Success rate thấp?
✅ A11:
   • Check: Code đúng không?
   • Check: Account có đủ quyền submit?
   • Check: Website còn hoạt động?
   • Enable monitoring để xem chi tiết

❓ Q12: Làm sao để debug?
✅ A12:
   • Đổi: LOG_LEVEL = 'DEBUG' trong config.py
   • Xem: logs/bot_activity.log
   • Grep: grep "ERROR" logs/bot_activity.log
   • Follow: asyncio logs để xem lỗi async

❓ Q13: Bot được báo "trao đổi" trên Telegram?
✅ A13:
   • Normal - Bot chỉ đọc/gửi tự động
   • Telegram sẽ không khóa account
   • Delay 0.8s là optimize để tránh rate limit

❓ Q14: Có thể config multiple channels?
✅ A14:
   • Có - Xem config.py CHANNEL_CONFIG
   • Thêm channel: Thêm 1 dict vào CHANNEL_CONFIG
   • Bot sẽ tự handle tất cả channels

❓ Q15: Backup database ở đâu?
✅ A15:
   • Folder: backups/
   • File: code_history_YYYYMMDD_HHMMSS.db
   • Auto backup hàng ngày lúc 2 AM
"""

# ==========================================
# 📋 PRINT GUIDES
# ==========================================

if __name__ == '__main__':
    print(QUICK_CHECKLIST)
    print("\n" + "="*80 + "\n")
    print(PROBLEM_1)
    print("\n" + "="*80 + "\n")
    print(PROBLEM_2)
    print("\n" + "="*80 + "\n")
    print(PROBLEM_3)
    print("\n" + "="*80 + "\n")
    print(PROBLEM_4)
    print("\n" + "="*80 + "\n")
    print(PROBLEM_5)
    print("\n" + "="*80 + "\n")
    print(EMERGENCY_FIXES)
    print("\n" + "="*80 + "\n")
    print(EXPECTED_LOGS)
    print("\n" + "="*80 + "\n")
    print(Q_AND_A)
