"""
🖥️ MỞ BROWSER THỦ CÔNG - VERIFY CF SẴN
Chạy trước: python manual_browser.py
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from config import Config
from logger_setup import logger

STEALTH_JS = """
try {
    delete Object.getPrototypeOf(navigator).webdriver;
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
} catch(e) {}

try {
    let keys = Object.keys(window).filter(key => key.includes('cdc_') || key.includes('wd_'));
    keys.forEach(key => { delete window[key]; });
} catch(e) {}

try {
    if (!window.chrome) { window.chrome = { runtime: {} }; }
} catch(e) {}
"""

class PersistentProfileManager:
    def __init__(self):
        self.profile_base = Path(Config.BROWSER_PROFILE_DIR) / "browser_profiles"
        self.profile_base.mkdir(parents=True, exist_ok=True)
    
    def get_profile_path(self, user: str) -> Path:
        profile_path = self.profile_base / user
        profile_path.mkdir(parents=True, exist_ok=True)
        return profile_path

async def main():
    logger.info("\n" + "="*70)
    logger.info("🖥️ MỞ BROWSER THỦ CÔNG ĐỂ VERIFY CLOUDFLARE")
    logger.info("="*70)
    
    # Lấy danh sách accounts
    all_accounts = {}
    for channel_id, config in Config.CHANNEL_CONFIG.items():
        for acc in config.get("accounts", []):
            user = acc["username"]
            if user not in all_accounts:
                all_accounts[user] = {
                    "url": config["url"]
                }
    
    logger.info("\n📋 CÁC WEBSITES CẦN VERIFY:\n")
    for i, (user, info) in enumerate(all_accounts.items(), 1):
        logger.info(f"{i}. {user}: {info['url']}\n")
    
    # Chọn account
    choice = input("📌 Nhập username (hoặc 'all' để mở tất cả): ").strip()
    
    if choice.lower() == 'all':
        accounts_to_open = list(all_accounts.keys())
    else:
        accounts_to_open = [choice] if choice in all_accounts else list(all_accounts.keys())
    
    logger.info(f"\n✅ Sẽ mở: {', '.join(accounts_to_open)}\n")
    
    profile_manager = PersistentProfileManager()
    
    async with async_playwright() as playwright:
        contexts = {}
        
        for user in accounts_to_open:
            info = all_accounts[user]
            profile_dir = profile_manager.get_profile_path(user)
            
            logger.info(f"\n🖥️ Mở Firefox cho {user}...")
            logger.info(f"   📁 Profile: {profile_dir}")
            logger.info(f"   🌐 URL: {info['url']}")
            
            context = await playwright.firefox.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                viewport={
                    "width": Config.VIEWPORT_WIDTH,
                    "height": Config.VIEWPORT_HEIGHT
                },
                ignore_https_errors=True,
            )
            
            page = await context.new_page()
            
            try:
                await page.add_init_script(STEALTH_JS)
            except:
                pass
            
            try:
                await page.goto(info['url'], wait_until="domcontentloaded", timeout=30000)
            except:
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=10000)
                except:
                    pass
            
            contexts[user] = (context, page)
            
            logger.info(f"✅ Browser mở xong cho {user}")
            logger.info(f"\n📋 HƯỚNG DẪN:")
            logger.info(f"   1. Click vào checkbox Cloudflare")
            logger.info(f"   2. Giải Captcha (nếu có)")
            logger.info(f"   3. Form sẽ tải xong")
            logger.info(f"   4. Đừng đóng browser này!")
            logger.info(f"   5. Mở terminal mới, chạy: python run.py\n")
        
        logger.info("\n" + "="*70)
        logger.info("✅ TẤT CẢ BROWSERS ĐÃ MỞ")
        logger.info("="*70)
        logger.info("\n💡 TIẾP THEO:")
        logger.info("   1. Xác minh Cloudflare ở mỗi browser")
        logger.info("   2. Mở Terminal mới")
        logger.info("   3. Chạy: python run.py")
        logger.info("   4. Bot sẽ dùng browsers này để submit code\n")
        
        logger.info("⏳ Chờ... (nhấn Ctrl+C khi muốn tắt)")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Đang đóng browsers...")
            for user, (ctx, page) in contexts.items():
                try:
                    await page.close()
                except:
                    pass
                try:
                    await ctx.close()
                except:
                    pass
            logger.info("✅ Tất cả browsers đã đóng")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Dừng")