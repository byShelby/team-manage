"""
Token 正则匹配工具
用于从文本中提取 AT Token、邮箱、Account ID 等信息
"""
import re
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class TokenParser:
    """Token 正则匹配解析器"""

    # JWT Token 正则 (以 eyJ 开头的 Base64 字符串)
    # 使用非贪婪匹配和正向前瞻,避免匹配到 ---- 分隔符后的内容
    JWT_PATTERN = r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+?(?=----|\s|$)'

    # 邮箱正则 (使用单词边界)
    EMAIL_PATTERN = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

    # Account ID 正则 (UUID 格式,使用单词边界避免匹配Token中的UUID)
    ACCOUNT_ID_PATTERN = r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'

    def extract_jwt_tokens(self, text: str) -> List[str]:
        """
        从文本中提取所有 JWT Token

        Args:
            text: 输入文本

        Returns:
            JWT Token 列表
        """
        tokens = re.findall(self.JWT_PATTERN, text)
        logger.info(f"从文本中提取到 {len(tokens)} 个 JWT Token")
        return tokens

    def extract_emails(self, text: str) -> List[str]:
        """
        从文本中提取所有邮箱地址

        Args:
            text: 输入文本

        Returns:
            邮箱地址列表
        """
        emails = re.findall(self.EMAIL_PATTERN, text)
        # 过滤掉包含特殊字符的假邮箱 (如包含 ---- 的)
        emails = [email for email in emails if '----' not in email and len(email) < 100]
        # 去重
        emails = list(set(emails))
        logger.info(f"从文本中提取到 {len(emails)} 个邮箱地址")
        return emails

    def extract_account_ids(self, text: str) -> List[str]:
        """
        从文本中提取所有 Account ID

        Args:
            text: 输入文本

        Returns:
            Account ID 列表
        """
        account_ids = re.findall(self.ACCOUNT_ID_PATTERN, text)
        # 去重
        account_ids = list(set(account_ids))
        logger.info(f"从文本中提取到 {len(account_ids)} 个 Account ID")
        return account_ids

    def parse_team_import_text(self, text: str) -> List[Dict[str, Optional[str]]]:
        """
        解析 Team 导入文本,提取 AT、邮箱、Account ID

        Args:
            text: 导入的文本内容

        Returns:
            解析结果列表,每个元素包含 token, email, account_id
        """
        results = []

        # 按行分割文本
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 使用正则提取当前行的信息
            tokens = re.findall(self.JWT_PATTERN, line)
            emails = re.findall(self.EMAIL_PATTERN, line)
            account_ids = re.findall(self.ACCOUNT_ID_PATTERN, line)

            # 过滤邮箱 (只保留合法的邮箱地址)
            valid_emails = []
            for email in emails:
                # 邮箱长度合理,且不包含连续的特殊字符
                if len(email) < 100 and '----' not in email:
                    valid_emails.append(email)

            # 如果当前行有 Token,创建一条记录
            if tokens:
                result = {
                    "token": tokens[0],  # 取第一个 Token
                    "email": valid_emails[0] if valid_emails else None,
                    "account_id": account_ids[0] if account_ids else None
                }
                results.append(result)

        logger.info(f"解析完成,共提取 {len(results)} 条 Team 信息")
        return results

    def validate_jwt_format(self, token: str) -> bool:
        """
        验证 JWT Token 格式是否正确

        Args:
            token: JWT Token 字符串

        Returns:
            True 表示格式正确,False 表示格式错误
        """
        return bool(re.fullmatch(self.JWT_PATTERN, token))

    def validate_email_format(self, email: str) -> bool:
        """
        验证邮箱格式是否正确

        Args:
            email: 邮箱地址

        Returns:
            True 表示格式正确,False 表示格式错误
        """
        return bool(re.fullmatch(self.EMAIL_PATTERN, email))

    def validate_account_id_format(self, account_id: str) -> bool:
        """
        验证 Account ID 格式是否正确

        Args:
            account_id: Account ID

        Returns:
            True 表示格式正确,False 表示格式错误
        """
        return bool(re.fullmatch(self.ACCOUNT_ID_PATTERN, account_id))


# 创建全局实例
token_parser = TokenParser()
