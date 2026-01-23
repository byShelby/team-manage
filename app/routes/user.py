"""
用户路由
处理用户兑换页面
"""
import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    tags=["user"]
)


@router.get("/", response_class=HTMLResponse)
async def redeem_page(request: Request):
    """
    用户兑换页面

    Args:
        request: FastAPI Request 对象

    Returns:
        用户兑换页面 HTML
    """
    try:
        from app.main import templates

        logger.info("用户访问兑换页面")

        return templates.TemplateResponse(
            "user/redeem.html",
            {"request": request}
        )

    except Exception as e:
        logger.error(f"渲染兑换页面失败: {e}")
        return HTMLResponse(
            content=f"<h1>页面加载失败</h1><p>{str(e)}</p>",
            status_code=500
        )
