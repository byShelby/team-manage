"""
通知服务
用于发送 Webhook 预警等通知
"""
import logging
import httpx
from typing import Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.settings import settings_service
from app.services.redemption import RedemptionService

logger = logging.getLogger(__name__)

class NotificationService:
    """通知服务类"""

    def __init__(self):
        self.redemption_service = RedemptionService()

    async def check_and_notify_low_stock(self, db_session: AsyncSession) -> bool:
        """
        检查库存并发送通知
        """
        try:
            # 1. 获取配置
            webhook_url = await settings_service.get_setting(db_session, "webhook_url")
            if not webhook_url:
                return False

            threshold_str = await settings_service.get_setting(db_session, "low_stock_threshold", "10")
            try:
                threshold = int(threshold_str)
            except (ValueError, TypeError):
                threshold = 10

            # 2. 检查库存
            unused_count = await self.redemption_service.get_unused_count(db_session)
            
            if unused_count <= threshold:
                logger.info(f"库存不足预警: 当前库存 {unused_count}, 阈值 {threshold}")
                return await self.send_webhook_notification(webhook_url, unused_count, threshold)
            
            return False

        except Exception as e:
            logger.error(f"检查库存并通知失败: {e}")
            return False

    async def send_webhook_notification(self, url: str, current_stock: int, threshold: int) -> bool:
        """
        发送 Webhook 通知
        """
        try:
            payload = {
                "event": "low_stock",
                "current_stock": current_stock,
                "threshold": threshold,
                "message": f"库存不足预警：当前可用兑换码数量为 {current_stock}，已低于阈值 {threshold}，请及时补货。"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Webhook 通知发送成功: {url}")
                return True
        except Exception as e:
            logger.error(f"发送 Webhook 通知失败: {e}")
            return False

# 创建全局实例
notification_service = NotificationService()
