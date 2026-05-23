"""
🤖 BOT ENTRY POINT
Chạy bot một cách đơn giản
"""

import asyncio
from main_script import main, client

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Bot đã dừng")