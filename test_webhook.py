
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.notification import notification_service
from app.services.settings import settings_service
from app.models import Setting

# 这是一个模拟测试脚本
# 建议在开发环境下运行，它会修改数据库中的配置

DATABASE_URL = "sqlite+aiosqlite:///./team_manage.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_webhook():
    async with AsyncSessionLocal() as db:
        # 1. 设置 Webhook URL (可以先去 https://webhook.site 拿一个地址)
        # 这里只是模拟，我们通过日志观察是否发送
        test_url = "https://webhook.site/placeholder"
        await settings_service.update_settings(db, {
            "webhook_url": test_url,
            "low_stock_threshold": "100" # 设高一点确保触发
        })
        
        print(f"Checking stock level and sending webhook to {test_url}...")
        
        # 2. 手动触发检查
        result = await notification_service.check_and_notify_low_stock(db)
        
        if result:
            print("Webhook check triggered notification successfully (check logs).")
        else:
            print("Webhook notification was not sent (maybe stock is higher than threshold or error occurred).")

if __name__ == "__main__":
    asyncio.run(test_webhook())
