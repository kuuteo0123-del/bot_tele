"""
🤖 BOT AUTO-RUN - CHẠY MỌI THỨ TRONG 1 TERMINAL
Lần đầu: Verify CF → Auto submit
Lần sau: Chỉ submit code (không verify CF lại)
"""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path
from config import Config
from logger_setup import logger

class BotAutoRun:
    def __init__(self):
        self.profile_dir = Path(Config.BROWSER_PROFILE_DIR) / "browser_profiles"
        self.has_profiles = False
        
    def check_profiles_exist(self) -> bool:
        """Kiểm tra xem profiles đã được tạo chưa"""
        if not self.profile_dir.exists():
            return False
        
        # Lấy danh sách accounts từ config
        accounts = set()
        for channel_config in Config.CHANNEL_CONFIG.values():
            for acc in channel_config.get("accounts", []):
                accounts.add(acc["username"])
        
        # Kiểm tra xem có bao nhiêu profiles đã tạo
        existing_profiles = set()
        if self.profile_dir.exists():
            for profile_folder in self.profile_dir.iterdir():
                if profile_folder.is_dir():
                    existing_profiles.add(profile_folder.name)
        
        # Nếu tất cả accounts đều có profile → không cần verify CF lại
        self.has_profiles = accounts.issubset(existing_profiles)
        return self.has_profiles
    
    def show_menu(self):
        """Hiển thị menu lựa chọn"""
        logger.info("\n" + "="*70)
        logger.info("🤖 BOT SĂN CODE - AUTO RUN v3.9")
        logger.info("="*70)
        
        if self.has_profiles:
            logger.info("\n✅ Profiles đã tồn tại")
            logger.info("   Cookies được lưu → Không cần verify CF lại\n")
            logger.info("LỰA CHỌN:")
            logger.info("  1. Chạy bot ngay (submit code)")
            logger.info("  2. Verify CF lại (tạo profiles mới)")
            logger.info("  3. Thoát\n")
        else:
            logger.info("\n⚠️  Profiles chưa tồn tại")
            logger.info("   Cần verify Cloudflare lần đầu\n")
            logger.info("LỰA CHỌN:")
            logger.info("  1. Verify Cloudflare + Setup profiles (LẦN ĐẦU)")
            logger.info("  2. Thoát\n")
        
        return input("📌 Chọn (1-3): ").strip()
    
    async def run_manual_browser(self):
        """Chạy manual_browser.py để verify CF"""
        logger.info("\n" + "="*70)
        logger.info("🖥️  MỞ BROWSER VERIFY CLOUDFLARE")
        logger.info("="*70)
        logger.info("\n📋 HƯỚNG DẪN:")
        logger.info("  1. Nhập username hoặc 'all' để mở tất cả")
        logger.info("  2. Click vào checkbox Cloudflare")
        logger.info("  3. Giải Captcha (nếu có)")
        logger.info("  4. Form tải xong → Nhấn Ctrl+C")
        logger.info("  5. Quay lại terminal, chọn 1 để chạy bot\n")
        
        # Chạy manual_browser.py
        try:
            subprocess.run([sys.executable, "manual_browser.py"], check=False)
        except KeyboardInterrupt:
            logger.info("\n✅ Verify Cloudflare xong")
        except Exception as e:
            logger.error(f"❌ Lỗi: {e}")
    
    async def run_bot(self):
        """Chạy bot submit code"""
        logger.info("\n" + "="*70)
        logger.info("🚀 KHỞI ĐỘNG BOT")
        logger.info("="*70)
        logger.info("\n📡 Bot sẽ lắng nghe Telegram channels...")
        logger.info("⏳ Nhấn Ctrl+C để dừng\n")
        
        try:
            from run_with_open_browser import main
            await main()
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot dừng (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Lỗi bot: {e}")
    
    async def main(self):
        """Main flow"""
        # Cài đặt dependencies (lần đầu)
        logger.info("🔧 Kiểm tra cài đặt...")
        try:
            import playwright
            import telethon
            logger.info("✅ Dependencies OK\n")
        except ImportError:
            logger.warning("⚠️  Thiếu dependencies, cài đặt...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], check=True)
                subprocess.run([sys.executable, "-m", "playwright", "install", "firefox"], check=False)
                logger.info("✅ Cài đặt xong\n")
            except Exception as e:
                logger.error(f"❌ Không thể cài đặt: {e}")
                return
        
        # Kiểm tra profiles
        self.check_profiles_exist()
        
        # Menu chính
        while True:
            choice = self.show_menu()
            
            if self.has_profiles:
                # Menu khi đã có profiles
                if choice == "1":
                    await self.run_bot()
                elif choice == "2":
                    await self.run_manual_browser()
                elif choice == "3":
                    logger.info("\n👋 Tạm biệt!")
                    break
                else:
                    logger.warning("❌ Lựa chọn không hợp lệ")
            else:
                # Menu lần đầu (chưa có profiles)
                if choice == "1":
                    await self.run_manual_browser()
                    # Sau khi verify CF, chạy bot ngay
                    logger.info("\n💡 Tiếp tục chạy bot...")
                    await asyncio.sleep(2)
                    await self.run_bot()
                    break
                elif choice == "2":
                    logger.info("\n👋 Tạm biệt!")
                    break
                else:
                    logger.warning("❌ Lựa chọn không hợp lệ")

if __name__ == '__main__':
    try:
        bot = BotAutoRun()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print("\n\n🛑 Dừng chương trình")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
