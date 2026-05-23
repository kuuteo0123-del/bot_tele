"""
🤖 BOT - FIREFOX + PERSISTENT PROFILE v3.9 [FIXED]
✅ FIXED: Firefox browser
✅ FIXED: Desktop viewport 1024x768
✅ FIXED: Persistent profile storage
✅ FIXED: Input field detection
"""

import asyncio
import os
import re
import random
import time
import tempfile
import shutil
import subprocess
import psutil
import signal
import sys
import contextlib
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
# ⚙️ STEALTH JS
# ==========================================
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

# ==========================================
# 🔍 FIREFOX PROCESS MANAGER
# ==========================================
class FirefoxProcessManager:
    """Quản lý Firefox processes riêng cho bot"""
    
    BOT_MARKER_FILE = ".bot_firefox_marker"
    
    @staticmethod
    def mark_bot_processes():
        marker_file = Path(tempfile.gettempdir()) / FirefoxProcessManager.BOT_MARKER_FILE
        try:
            current_pids = set()
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name'].lower() if proc.info['name'] else ""
                    if 'firefox' in name:
                        current_pids.add(proc.info['pid'])
                except:
                    pass
            
            with open(marker_file, 'w') as f:
                for pid in current_pids:
                    f.write(f"{pid}\n")
            
            logger.debug(f"🏷️ Đánh dấu {len(current_pids)} Firefox processes hiện tại")
        except Exception as e:
            pass
    
    @staticmethod
    def get_bot_firefox_processes() -> set:
        marker_file = Path(tempfile.gettempdir()) / FirefoxProcessManager.BOT_MARKER_FILE
        original_pids = set()
        if marker_file.exists():
            try:
                with open(marker_file, 'r') as f:
                    original_pids = set(int(line.strip()) for line in f if line.strip())
            except:
                pass
        
        current_pids = set()
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name'].lower() if proc.info['name'] else ""
                    if 'firefox' in name:
                        current_pids.add(proc.info['pid'])
                except:
                    pass
        except:
            pass
        
        bot_pids = current_pids - original_pids
        return bot_pids
    
    @staticmethod
    def kill_only_bot_processes(bot_pids: set):
        logger.info(f"🧹 Đang tắt {len(bot_pids)} Firefox processes của bot...")
        for pid in bot_pids:
            try:
                proc = psutil.Process(pid)
                name = proc.name().lower() if proc.name() else ""
                if 'firefox' in name:
                    proc.terminate()
                    time.sleep(0.1)
            except:
                pass

# ==========================================
# 📁 PERSISTENT PROFILE MANAGER
# ==========================================
class PersistentProfileManager:
    def __init__(self):
        self.profile_base = Path(Config.BROWSER_PROFILE_DIR) / "browser_profiles"
        self.profile_base.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Profile directory: {self.profile_base}")
    
    def get_profile_path(self, user: str) -> Path:
        """Lấy hoặc tạo profile path cho user"""
        profile_path = self.profile_base / user
        profile_path.mkdir(parents=True, exist_ok=True)
        return profile_path
    
    def get_user_profiles(self) -> list:
        """Lấy danh sách tất cả profiles"""
        if not self.profile_base.exists():
            return []
        return [d.name for d in self.profile_base.iterdir() if d.is_dir()]

# ==========================================
# ⚙️ GLOBAL STATE
# ==========================================
class BotState:
    def __init__(self):
        self.playwright_instance = None
        self.account_contexts = {}
        self.context_locks = {}
        self.context_init_tasks = {}
        self.is_running = True
        self.cf_verified = {}
        self.submission_count = {}
        self.handler_registered = False

bot_state = BotState()
client = TelegramClient(Config.SESSION_NAME, Config.API_ID, Config.API_HASH)
profile_manager = PersistentProfileManager()
_systems = None

# ==========================================
# ✅ VERIFY TELEGRAM SESSION
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
    FirefoxProcessManager.mark_bot_processes()
    db = init_database(Config.DATABASE_PATH)
    anti_det = init_anti_detection()
    health_mon, alert_mgr, perf_mon = init_monitoring()
    task_q, sched = init_task_system(max_concurrent=Config.MAX_CONCURRENT_SUBMITS)
    
    bot_state.playwright_instance = await async_playwright().start()
    get_shutdown_handler().setup(bot_state)
    
    return {'db': db, 'anti_detection': anti_det, 'performance_monitor': perf_mon}

# ==========================================
# 🛡️ INIT BROWSER VỚI PERSISTENT PROFILE
# ==========================================
async def init_browser_for_user(user: str, channel_id: int = None):
    """Khởi tạo Firefox browser với persistent profile + cookies"""
    
    if user in bot_state.account_contexts:
        return bot_state.account_contexts[user]
    
    if user in bot_state.context_init_tasks:
        try:
            await asyncio.wait_for(bot_state.context_init_tasks[user], timeout=30)
            return bot_state.account_contexts.get(user)
        except:
            pass
    
    init_future = asyncio.Future()
    bot_state.context_init_tasks[user] = init_future
    
    try:
        profile_dir = profile_manager.get_profile_path(user)
        
        logger.info(f"🖥️ Khởi tạo Firefox cho {user}...")
        logger.info(f"   📁 Profile: {profile_dir}")
        
        context = await bot_state.playwright_instance.firefox.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=Config.HEADLESS_MODE,
            viewport={
                "width": Config.VIEWPORT_WIDTH,
                "height": Config.VIEWPORT_HEIGHT
            },
            ignore_https_errors=True,
            accept_downloads=True,
        )
        
        bot_state.account_contexts[user] = context
        bot_state.context_locks[user] = asyncio.Lock()
        bot_state.cf_verified[user] = False
        bot_state.submission_count[user] = 0
        
        logger.info(f"✅ Firefox mở xong cho {user} (viewport: {Config.VIEWPORT_WIDTH}x{Config.VIEWPORT_HEIGHT})")
        
        init_future.set_result(True)
        return context
    
    except Exception as e:
        logger.error(f"❌ Lỗi khởi tạo Firefox: {e}")
        init_future.set_exception(e)
        raise
    finally:
        bot_state.context_init_tasks.pop(user, None)

# ==========================================
# 🎯 GET PAGE WITH STEALTH
# ==========================================
async def get_stealth_page(context, user: str):
    """Lấy page (hoặc tạo mới) với stealth mode"""
    
    if context.pages:
        page = context.pages[0]
        try:
            await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        except:
            pass
        return page
    
    page = await context.new_page()
    try:
        await page.add_init_script(STEALTH_JS)
    except:
        pass
    
    return page

# ==========================================
# 🛡️ PREPARE BROWSER
# ==========================================
async def prepare_browser_for_submission(user: str, target_url: str, perf_monitor) -> bool:
    """Chuẩn bị browser để submit code"""
    
    start_time = time.time()
    context = bot_state.account_contexts.get(user)
    
    if not context:
        try:
            await init_browser_for_user(user)
            context = bot_state.account_contexts.get(user)
        except Exception as e:
            logger.error(f"❌ [{user}] Không thể khởi tạo browser: {e}")
            return False
    
    try:
        page = await get_stealth_page(context, user)
        
        logger.debug(f"🌐 [{user}] Truy cập: {target_url}")
        
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        except:
            logger.warning(f"⚠️ [{user}] Timeout khi load, thử reload...")
            try:
                await page.reload(wait_until="domcontentloaded", timeout=10000)
            except:
                pass
        
        await asyncio.sleep(1.5)
        
        bot_state.cf_verified[user] = True
        logger.info(f"✅ [{user}] Sẵn sàng submit")
        
        duration = time.time() - start_time
        perf_monitor.record_task("prepare_browser", duration, True)
        return True
        
    except Exception as e:
        logger.error(f"❌ [{user}] Lỗi chuẩn bị: {e}")
        duration = time.time() - start_time
        perf_monitor.record_task("prepare_browser", duration, False)
        return False

# ==========================================
# 🔍 SMART INPUT FINDER
# ==========================================
async def find_input_fields(page, user: str):
    """Tìm input fields cho username & code"""
    
    try:
        username_selectors = [
            "input[placeholder*='tài' i]",
            "input[placeholder*='username' i]",
            "input[placeholder*='account' i]",
            "input[name='username']",
            "input[name='user']",
        ]
        
        code_selectors = [
            "input[placeholder*='code' i]",
            "input[placeholder*='mã' i]",
            "input[placeholder*='gift' i]",
            "input[name='code']",
            "input[name='giftcode']",
        ]
        
        username_input = None
        code_input = None
        
        for sel in username_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible():
                    username_input = elem
                    logger.debug(f"✅ Tìm thấy username input: {sel}")
                    break
            except:
                pass
        
        for sel in code_selectors:
            try:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible():
                    code_input = elem
                    logger.debug(f"✅ Tìm thấy code input: {sel}")
                    break
            except:
                pass
        
        if not username_input or not code_input:
            logger.debug("⚠️ Fallback: Tìm 2 input visible đầu tiên...")
            
            inputs = await page.query_selector_all("input:not([type='hidden']):not([type='checkbox']):not([type='radio'])")
            visible_inputs = []
            
            for inp in inputs:
                try:
                    if await inp.is_visible():
                        visible_inputs.append(inp)
                except:
                    pass
            
            if len(visible_inputs) >= 2:
                if not username_input:
                    username_input = visible_inputs[0]
                    logger.debug(f"✅ Dùng input thứ 1 làm username")
                
                if not code_input:
                    code_input = visible_inputs[1]
                    logger.debug(f"✅ Dùng input thứ 2 làm code")
        
        if not username_input or not code_input:
            logger.warning(f"❌ [{user}] Không tìm thấy đủ input fields!")
            return None, None
        
        return username_input, code_input
        
    except Exception as e:
        logger.error(f"❌ [{user}] Lỗi tìm input fields: {e}")
        return None, None

# ==========================================
# 📝 SUBMIT CODE
# ==========================================
async def submit_code_safe(user: str, code: str, target_url: str, systems: dict):
    """Submit code một cách an toàn"""
    
    start_time = time.time()
    db = systems['db']
    perf_mon = systems['performance_monitor']
    
    if user not in bot_state.context_locks:
        logger.error(f"❌ [{user}] Không có context lock")
        return {'success': False}
    
    try:
        async with bot_state.context_locks[user]:
            context = bot_state.account_contexts.get(user)
            
            if not context:
                logger.error(f"❌ [{user}] Không có browser context")
                return {'success': False}
            
            if not bot_state.cf_verified.get(user):
                logger.warning(f"⚠️ [{user}] Browser chưa chuẩn bị, chuẩn bị lại...")
                ok = await prepare_browser_for_submission(user, target_url, perf_mon)
                if not ok:
                    return {'success': False}
            
            page = await get_stealth_page(context, user)
            
            logger.info(f"🚀 [{user}] Gửi code: {code}")
            
            username_input, code_input = await find_input_fields(page, user)
            
            if not username_input or not code_input:
                logger.error(f"❌ [{user}] Không tìm thấy input fields!")
                return {'success': False}
            
            try:
                await username_input.click()
                await username_input.fill("")
                await asyncio.sleep(0.2)
                await username_input.type(user, delay=random.randint(30, 80))
                logger.debug(f"✅ [{user}] Nhập username: {user}")
            except Exception as e:
                logger.error(f"❌ [{user}] Lỗi nhập username: {e}")
                return {'success': False}
            
            await asyncio.sleep(random.uniform(0.3, 0.6))
            
            try:
                await code_input.click()
                await code_input.fill("")
                await asyncio.sleep(0.2)
                await code_input.type(code, delay=random.randint(30, 80))
                logger.debug(f"✅ [{user}] Nhập code: {code}")
            except Exception as e:
                logger.error(f"❌ [{user}] Lỗi nhập code: {e}")
                return {'success': False}
            
            await asyncio.sleep(0.5)
            
            try:
                buttons = await page.query_selector_all("button, input[type='submit'], input[type='button']")
                
                submitted = False
                for btn in buttons:
                    try:
                        text = (await btn.inner_text()).upper()
                        if any(kw in text for kw in ["NẠP", "SUBMIT", "GỬI", "NHẬN", "REDEEM", "SEND", "OK"]):
                            logger.debug(f"✅ Tìm thấy submit button: {text}")
                            await btn.click(no_wait_after=True)
                            submitted = True
                            break
                    except:
                        pass
                
                if not submitted:
                    logger.debug("⚠️ Không tìm thấy button, thử Enter...")
                    await page.keyboard.press("Enter")
                
            except Exception as e:
                logger.error(f"❌ [{user}] Lỗi submit: {e}")
                return {'success': False}
            
            await asyncio.sleep(2)
            
            result_text = ""
            try:
                for sel in [".swal2-html-container", ".swal2-title", ".modal-body", ".alert", ".message", "[class*='success']", "[class*='error']"]:
                    for elem in await page.query_selector_all(sel):
                        try:
                            t = await elem.inner_text()
                            if t and len(t.strip()) > 0:
                                result_text += t.strip() + " "
                        except:
                            pass
            except:
                pass
            
            elapsed = time.time() - start_time
            
            is_success = False
            if result_text:
                result_upper = result_text.upper()
                is_success = any(kw in result_upper for kw in ["THÀNH CÔNG", "SUCCESS", "OK", "CỘNG", "RECEIVED"])
                is_failed = any(kw in result_upper for kw in ["SAI", "LỖI", "ĐÃ SỬ", "HẾT HẠN", "KHÔNG", "FAILED"])
                is_success = is_success and not is_failed
            
            if is_success or (not result_text or len(result_text) < 5):
                logger.info(f"✅ [{user}] THÀNH CÔNG ({elapsed:.2f}s)")
                db.record_submission(code, user, target_url, "SUCCESS", result_text[:100] if result_text else "OK")
                bot_state.submission_count[user] += 1
                perf_mon.record_task("submit_code", elapsed, True)
                return {'success': True}
            else:
                logger.warning(f"❌ [{user}] THẤT BẠI ({elapsed:.2f}s): {result_text[:60]}")
                db.record_submission(code, user, target_url, "FAILED", result_text[:100] if result_text else "Unknown")
                perf_mon.record_task("submit_code", elapsed, False)
                return {'success': False}
    
    except Exception as e:
        logger.error(f"❌ [{user}] Lỗi submit code: {e}")
        perf_mon.record_task("submit_code", time.time() - start_time, False)
        return {'success': False}

# ==========================================
# 📨 TELEGRAM HANDLER
# ==========================================
async def setup_telegram_handler():
    """Setup Telegram message handler"""
    
    if bot_state.handler_registered:
        return
    
    channel_ids = list(Config.CHANNEL_CONFIG.keys())
    logger.info(f"\n📡 SETUP TELEGRAM HANDLERS cho {len(channel_ids)} channels...")
    
    @client.on(events.NewMessage(chats=channel_ids))
    async def handler(event):
        """Xử lý message mới từ channels"""
        
        if not _systems:
            logger.error("❌ Systems chưa khởi tạo")
            return
        
        config = Config.CHANNEL_CONFIG.get(event.chat_id)
        if not config:
            return
        
        target_url = config["url"]
        accounts = config["accounts"]
        
        logger.info(f"\n👀 Vừa có message từ: {config['name']}")
        logger.info(f"   🌐 URL: {target_url}")
        
        text = event.message.text or ""
        
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
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
        unique_codes = set(codes)
        
        final_codes = []
        for code in unique_codes:
            if len(code) < Config.CODE_MIN_LENGTH or len(code) > Config.CODE_MAX_LENGTH:
                continue
            
            if any(x in code.upper() for x in blacklist_upper):
                continue
            
            validation = CodeValidator.validate_code(code, target_url)
            if validation['valid']:
                final_codes.append(code)
        
        if not final_codes:
            logger.warning("⚠️ Không tìm thấy code hợp lệ")
            return
        
        logger.info(f"📋 Codes tìm thấy: {len(final_codes)}")
        logger.info(f"   Codes: {final_codes}")
        
        logger.info(f"🖥️ Khởi tạo browsers cho {len(accounts)} accounts...")
        
        for acc in accounts:
            try:
                await init_browser_for_user(acc["username"])
                logger.debug(f"   ✅ {acc['username']}")
            except Exception as e:
                logger.error(f"   ❌ {acc['username']}: {e}")
        
        logger.info(f"⚡ Chuẩn bị browsers...")
        for acc in accounts:
            try:
                ok = await prepare_browser_for_submission(acc["username"], target_url, _systems['performance_monitor'])
                if ok:
                    logger.debug(f"   ✅ {acc['username']}")
            except Exception as e:
                logger.error(f"   ❌ {acc['username']}: {e}")
        
        await asyncio.sleep(1)
        
        logger.info(f"\n🚀 BẮT ĐẦU SUBMIT ({len(final_codes)} codes, {len(accounts)} accounts)...\n")
        
        tasks = []
        for i, acc in enumerate(accounts):
            if i < len(final_codes):
                code = final_codes[i]
                tasks.append(submit_code_safe(acc["username"], code, target_url, _systems))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            logger.info(f"\n📊 KẾT QUẢ: {success_count}/{len(final_codes)} thành công")
    
    bot_state.handler_registered = True
    logger.info("✅ Telegram handlers setup xong!\n")

# ==========================================
# 🛑 CLEANUP
# ==========================================
async def cleanup_browsers():
    """Cleanup tất cả browsers"""
    
    logger.info("\n🧹 Cleanup browsers...")
    
    for user, ctx in list(bot_state.account_contexts.items()):
        try:
            for page in list(ctx.pages):
                try:
                    await page.close()
                except:
                    pass
            await ctx.close()
            logger.debug(f"   ✅ {user}")
        except Exception as e:
            logger.debug(f"   ⚠️ {user}: {e}")
    
    bot_pids = FirefoxProcessManager.get_bot_firefox_processes()
    if bot_pids:
        FirefoxProcessManager.kill_only_bot_processes(bot_pids)

# ==========================================
# 🏁 MAIN
# ==========================================
async def main():
    global _systems
    
    try:
        logger.info("\n" + "="*70)
        logger.info("🚀 KHỞI ĐỘNG BOT v3.9 (FIREFOX + PERSISTENT PROFILE)")
        logger.info("="*70)
        
        _systems = await init_systems()
        
        logger.info("\n📨 Kết nối Telegram...")
        await client.start()
        logger.info("✅ Kết nối Telegram OK")
        
        if not await verify_telegram_session():
            return
        
        if not await verify_channels_and_get_ids():
            return
        
        tester = get_system_tester(client)
        if not await tester.test_all(_systems['db']):
            return
        
        await setup_telegram_handler()
        
        logger.info("="*70)
        logger.info("✅ BOT SẴN SÀNG (v3.9 - FIREFOX)")
        logger.info("="*70)
        logger.info("\n📡 Lắng nghe tin nhắn từ channels...")
        logger.info("⏳ Nhấn Ctrl+C để tắt\n")
        
        asyncio.create_task(get_db_backup().schedule_daily_backup(Config.DATABASE_PATH, bot_state))
        asyncio.create_task(get_profile_cleaner().schedule_daily_cleanup(
            Path(Config.BROWSER_PROFILE_DIR) / "browser_profiles", 
            bot_state
        ))
        
        await client.run_until_disconnected()
    
    except Exception as e:
        logger.critical(f"❌ Lỗi critical: {e}")
    
    finally:
        logger.info("\n🛑 Dừng bot...")
        bot_state.is_running = False
        await cleanup_browsers()
        if bot_state.playwright_instance:
            await bot_state.playwright_instance.stop()
        logger.info("✅ Bot đã tắt")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Bot đã dừng (Ctrl+C)")