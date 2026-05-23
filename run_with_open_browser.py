"""
🤖 BOT - DÙNG BROWSERS ĐÃ MỞ v3.9
Chạy sau khi đã chạy: python manual_browser.py
"""

import asyncio
import os
import re
import random
import time
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntitySpoiler
from playwright.async_api import async_playwright

from config import Config
from logger_setup import logger
from code_validator import CodeValidator
from error_handler import RetryHandler, get_circuit_breaker
from database import init_database, get_database
from rate_limiter import init_anti_detection, get_anti_detection
from monitoring import init_monitoring, get_monitoring_system
from task_manager import init_task_system, CodeTask, TaskPriority

from features import (
    print_version_info,
    ConfigValidator,
    get_stats_manager,
    get_submission_logger,
    MemoryMonitor,
    get_memory_monitor,
    GracefulShutdownHandler,
    get_shutdown_handler,
    send_alert_to_user,
    DatabaseBackup,
    get_db_backup,
    ProfileCleaner,
    get_profile_cleaner,
    SystemTester,
    get_system_tester,
)

# ==========================================
# 📁 PERSISTENT PROFILE MANAGER
# ==========================================
class PersistentProfileManager:
    def __init__(self):
        self.profile_base = Path(Config.BROWSER_PROFILE_DIR) / "browser_profiles"
        self.profile_base.mkdir(parents=True, exist_ok=True)
    
    def get_profile_path(self, user: str) -> Path:
        profile_path = self.profile_base / user
        profile_path.mkdir(parents=True, exist_ok=True)
        return profile_path

# ==========================================
# ⚙️ GLOBAL STATE
# ==========================================
class BotState:
    def __init__(self):
        self.playwright_instance = None
        self.account_contexts = {}
        self.context_locks = {}
        self.is_running = True
        self.cf_verified = {}
        self.submission_count = {}
        self.handler_registered = False

bot_state = BotState()
client = TelegramClient(Config.SESSION_NAME, Config.API_ID, Config.API_HASH)
profile_manager = PersistentProfileManager()
_systems = None

# ==========================================
# 🖥️ CONNECT ĐẾN OPEN BROWSERS
# ==========================================
async def connect_to_open_browsers():
    """Connect đến browsers đã mở từ manual_browser.py"""
    
    logger.info("\n" + "="*70)
    logger.info("🔗 KẾT NỐI ĐẾN BROWSERS ĐÃ MỞ")
    logger.info("="*70)
    
    bot_state.playwright_instance = await async_playwright().start()
    
    # Lấy danh sách accounts
    all_accounts = {}
    for channel_id, config in Config.CHANNEL_CONFIG.items():
        for acc in config.get("accounts", []):
            user = acc["username"]
            if user not in all_accounts:
                all_accounts[user] = True
    
    logger.info(f"\n🔍 Tìm {len(all_accounts)} browsers đã mở...\n")
    
    connected_count = 0
    
    for user in all_accounts.keys():
        try:
            profile_dir = profile_manager.get_profile_path(user)
            
            # Kết nối đến persistent context đã mở
            context = await bot_state.playwright_instance.firefox.connect_over_cdp(
                "http://localhost:9222"  # Default CDP port
            )
            
            if context:
                bot_state.account_contexts[user] = context
                bot_state.context_locks[user] = asyncio.Lock()
                bot_state.cf_verified[user] = True  # Giả định đã verify CF
                bot_state.submission_count[user] = 0
                
                logger.info(f"✅ Kết nối: {user}")
                connected_count += 1
        except Exception as e:
            logger.warning(f"⚠️ Không kết nối được {user}: {e}")
    
    if connected_count == 0:
        logger.warning("\n⚠️ Không tìm thấy browsers nào")
        logger.info("   Hãy chạy: python manual_browser.py trước!")
        return False
    
    logger.info(f"\n✅ Kết nối xong: {connected_count} browsers\n")
    return True

# ==========================================
# ✅ VERIFY SESSION
# ==========================================
async def verify_telegram_session():
    logger.info("\n" + "="*70)
    logger.info("🔐 XÁC MINH TELEGRAM SESSION...")
    try:
        me = await client.get_me()
        logger.info(f"✅ SESSION HỢP LỆ!")
        logger.info(f"   👤 Username: @{me.username}")
        logger.info(f"   🆔 User ID: {me.id}")
        return True
    except Exception as e:
        logger.error(f"❌ SESSION LỖI: {e}")
        return False

# ==========================================
# ✅ VERIFY CHANNELS
# ==========================================
async def verify_channels_and_get_ids():
    logger.info("\n" + "="*70)
    logger.info("📡 XÁC MINH CHANNELS...")
    valid_channels = {}
    my_dialogs = {dialog.id: dialog async for dialog in client.iter_dialogs()}
    
    for chat_id, config in Config.CHANNEL_CONFIG.items():
        if chat_id in my_dialogs:
            logger.info(f"✅ HỢP LỆ: {config['name']}")
            valid_channels[chat_id] = config
        else:
            logger.warning(f"❌ CHƯA THAM GIA: {config['name']}")
    return valid_channels

# ==========================================
# 🌐 INIT SYSTEMS
# ==========================================
async def init_systems():
    print_version_info()
    db = init_database(Config.DATABASE_PATH)
    anti_det = init_anti_detection()
    health_mon, alert_mgr, perf_mon = init_monitoring()
    task_q, sched = init_task_system(max_concurrent=Config.MAX_CONCURRENT_SUBMITS)
    
    get_shutdown_handler().setup(bot_state)
    
    return {'db': db, 'anti_detection': anti_det, 'performance_monitor': perf_mon}

# ==========================================
# 🔍 FIND INPUT FIELDS
# ==========================================
async def find_input_fields(page, user: str):
    """Tìm input fields"""
    try:
        username_selectors = [
            "input[placeholder*='tài' i]",
            "input[placeholder*='username' i]",
            "input[name='username']",
        ]
        
        code_selectors = [
            "input[placeholder*='code' i]",
            "input[placeholder*='mã' i]",
            "input[name='code']",
        ]
        
        username_input = None
        code_input = None
        
        for sel in username_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible():
                    username_input = elem
                    break
            except:
                pass
        
        for sel in code_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible():
                    code_input = elem
                    break
            except:
                pass
        
        if not username_input or not code_input:
            inputs = await page.query_selector_all("input:not([type='hidden']):not([type='checkbox'])")
            visible_inputs = []
            
            for inp in inputs:
                try:
                    if await inp.is_visible():
                        visible_inputs.append(inp)
                except:
                    pass
            
            if len(visible_inputs) >= 2:
                username_input = visible_inputs[0]
                code_input = visible_inputs[1]
        
        return username_input, code_input
    except Exception as e:
        logger.error(f"❌ [{user}] Lỗi tìm input: {e}")
        return None, None

# ==========================================
# 📝 SUBMIT CODE
# ==========================================
async def submit_code_safe(user: str, code: str, target_url: str, systems: dict):
    """Submit code"""
    
    start_time = time.time()
    db = systems['db']
    perf_mon = systems['performance_monitor']
    
    if user not in bot_state.context_locks:
        return {'success': False}
    
    try:
        async with bot_state.context_locks[user]:
            context = bot_state.account_contexts.get(user)
            
            if not context:
                logger.error(f"❌ [{user}] Không có context")
                return {'success': False}
            
            try:
                pages = context.pages
            except:
                pages = []
            
            if not pages:
                logger.error(f"❌ [{user}] Không có page")
                return {'success': False}
            
            page = pages[0]
            
            logger.info(f"🚀 [{user}] Gửi code: {code}")
            
            username_input, code_input = await find_input_fields(page, user)
            
            if not username_input or not code_input:
                logger.error(f"❌ [{user}] Không tìm input")
                return {'success': False}
            
            try:
                await username_input.click()
                await username_input.fill(user)
                await asyncio.sleep(0.2)
                logger.debug(f"✅ Nhập: {user}")
            except Exception as e:
                logger.error(f"❌ Lỗi nhập username: {e}")
                return {'success': False}
            
            await asyncio.sleep(0.3)
            
            try:
                await code_input.click()
                await code_input.fill(code)
                await asyncio.sleep(0.2)
                logger.debug(f"✅ Nhập code: {code}")
            except Exception as e:
                logger.error(f"❌ Lỗi nhập code: {e}")
                return {'success': False}
            
            await asyncio.sleep(0.5)
            
            try:
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    try:
                        text = (await btn.inner_text()).upper()
                        if any(kw in text for kw in ["NẠP", "SUBMIT", "GỬI"]):
                            await btn.click(no_wait_after=True)
                            break
                    except:
                        pass
            except:
                pass
            
            await asyncio.sleep(2)
            
            result_text = ""
            try:
                for elem in await page.query_selector_all(".swal2-html-container, .alert"):
                    try:
                        t = await elem.inner_text()
                        if t:
                            result_text += t
                    except:
                        pass
            except:
                pass
            
            elapsed = time.time() - start_time
            
            is_success = False
            if result_text:
                result_upper = result_text.upper()
                is_success = any(kw in result_upper for kw in ["THÀNH CÔNG", "SUCCESS"])
            
            if is_success:
                logger.info(f"✅ [{user}] THÀNH CÔNG ({elapsed:.2f}s)")
                db.record_submission(code, user, target_url, "SUCCESS", result_text[:100])
                return {'success': True}
            else:
                logger.warning(f"❌ [{user}] THẤT BẠI ({elapsed:.2f}s)")
                db.record_submission(code, user, target_url, "FAILED", result_text[:100])
                return {'success': False}
    
    except Exception as e:
        logger.error(f"❌ [{user}] Lỗi: {e}")
        return {'success': False}

# ==========================================
# 📨 TELEGRAM HANDLER
# ==========================================
async def setup_telegram_handler():
    """Setup handler"""
    
    if bot_state.handler_registered:
        return
    
    channel_ids = list(Config.CHANNEL_CONFIG.keys())
    logger.info(f"\n📡 Setup handlers cho {len(channel_ids)} channels...\n")
    
    @client.on(events.NewMessage(chats=channel_ids))
    async def handler(event):
        if not _systems:
            return
        
        config = Config.CHANNEL_CONFIG.get(event.chat_id)
        if not config:
            return
        
        target_url = config["url"]
        accounts = config["accounts"]
        
        logger.info(f"\n👀 Message từ: {config['name']}")
        
        text = event.message.text or ""
        text = re.sub(r'https?://\S+', '', text)
        
        codes = []
        if event.message.entities:
            for ent in event.message.entities:
                if isinstance(ent, MessageEntitySpoiler):
                    try:
                        code_text = event.message.text[ent.offset:ent.offset + ent.length]
                        codes.extend(re.findall(r'[a-zA-Z0-9]+', code_text))
                    except:
                        pass
        
        codes.extend(re.findall(r'[a-zA-Z0-9]+', text))
        
        blacklist_upper = [b.upper() for b in Config.CODE_BLACKLIST]
        final_codes = []
        
        for code in set(codes):
            if len(code) < Config.CODE_MIN_LENGTH or len(code) > Config.CODE_MAX_LENGTH:
                continue
            if any(x in code.upper() for x in blacklist_upper):
                continue
            if CodeValidator.validate_code(code, target_url)['valid']:
                final_codes.append(code)
        
        if not final_codes:
            return
        
        logger.info(f"📋 Codes: {final_codes}")
        
        logger.info(f"\n🚀 SUBMIT ({len(final_codes)} codes)...\n")
        
        tasks = []
        for i, acc in enumerate(accounts):
            if i < len(final_codes):
                code = final_codes[i]
                tasks.append(submit_code_safe(acc["username"], code, target_url, _systems))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            logger.info(f"\n📊 KẾT QUẢ: {success_count}/{len(final_codes)} ✅\n")
    
    bot_state.handler_registered = True

# ==========================================
# 🏁 MAIN
# ==========================================
async def main():
    global _systems
    
    try:
        logger.info("\n" + "="*70)
        logger.info("🚀 BOT v3.9 (DÙNG BROWSERS ĐÃ MỞ)")
        logger.info("="*70)
        
        _systems = await init_systems()
        
        if not await connect_to_open_browsers():
            return
        
        logger.info("\n📨 Kết nối Telegram...")
        await client.start()
        logger.info("✅ OK")
        
        if not await verify_telegram_session():
            return
        
        if not await verify_channels_and_get_ids():
            return
        
        await setup_telegram_handler()
        
        logger.info("="*70)
        logger.info("✅ BOT SẴN SÀNG (DÙNG BROWSERS ĐÃ MỞ)")
        logger.info("="*70)
        logger.info("\n📡 Lắng nghe tin nhắn...\n")
        
        await client.run_until_disconnected()
    
    except Exception as e:
        logger.critical(f"❌ Lỗi: {e}")
    
    finally:
        logger.info("\n🛑 Dừng bot...")
        bot_state.is_running = False

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Dừng")