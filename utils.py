"""
通用工具函数模块
包含时间格式转换、字符串处理等通用工具函数
"""
import re
from datetime import datetime
from typing import Optional, Tuple


class TimeUtils:
    """时间处理工具类"""

    COMMON_DATETIME_PATTERNS = [
        # ISO 8601 格式
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?", "%Y-%m-%dT%H:%M:%S"),
        # 标准格式: 2024-01-15 14:30:25
        (r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", "%Y-%m-%d %H:%M:%S"),
        # 紧凑格式: 20240115 143025
        (r"\d{8}\s+\d{6}", "%Y%m%d %H%M%S"),
        # 日志常见格式: Jan 15 14:30:25
        (r"[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}", "%b %d %H:%M:%S"),
        # 带斜杠格式: 15/01/2024 14:30:25
        (r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}", "%d/%m/%Y %H:%M:%S"),
        # 美式格式: 01/15/2024 14:30:25
        (r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}", "%m/%d/%Y %H:%M:%S"),
    ]

    @classmethod
    def parse_datetime(cls, text: str) -> Optional[datetime]:
        """
        从文本中提取并解析日期时间
        返回 datetime 对象或 None
        """
        for pattern, fmt in cls.COMMON_DATETIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                try:
                    # 处理 ISO 8601 格式中的时区信息
                    if "T" in date_str and ("Z" in date_str or re.search(r"[+-]\d{2}:?\d{2}$", date_str)):
                        date_str = date_str.replace("Z", "+00:00")
                        if len(date_str) > 19:
                            date_str = date_str[:19]
                        return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        return None

    @classmethod
    def extract_hour_key(cls, dt: datetime) -> str:
        """提取小时级别的键值，用于按小时统计"""
        return dt.strftime("%Y-%m-%d %H:00")

    @classmethod
    def format_datetime(cls, dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化日期时间"""
        return dt.strftime(fmt)


class StringUtils:
    """字符串处理工具类"""

    @staticmethod
    def truncate(text: str, max_length: int = 80, suffix: str = "...") -> str:
        """截断字符串到指定长度"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def clean_message(message: str) -> str:
        """清理错误信息，去除多余空格和特殊字符"""
        # 去除首尾空白
        message = message.strip()
        # 将多个连续空格替换为单个空格
        message = re.sub(r"\s+", " ", message)
        return message

    @staticmethod
    def extract_ip(text: str) -> Optional[str]:
        """从文本中提取 IP 地址"""
        # IPv4 正则表达式
        ip_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        match = re.search(ip_pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def pad_center(text: str, width: int, fillchar: str = " ") -> str:
        """居中对齐文本"""
        return text.center(width, fillchar)

    @staticmethod
    def pad_left(text: str, width: int, fillchar: str = " ") -> str:
        """左对齐文本"""
        return text.ljust(width, fillchar)

    @staticmethod
    def pad_right(text: str, width: int, fillchar: str = " ") -> str:
        """右对齐文本"""
        return text.rjust(width, fillchar)


class LevelUtils:
    """日志级别处理工具类"""

    VALID_LEVELS = {"INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "DEBUG", "TRACE"}

    # 级别权重，用于排序
    LEVEL_WEIGHTS = {
        "TRACE": 0,
        "DEBUG": 1,
        "INFO": 2,
        "WARN": 3,
        "WARNING": 3,
        "ERROR": 4,
        "CRITICAL": 5,
    }

    @classmethod
    def normalize_level(cls, level: str) -> str:
        """标准化日志级别"""
        level = level.upper().strip()
        if level == "WARNING":
            return "WARN"
        return level if level in cls.VALID_LEVELS else "UNKNOWN"

    @classmethod
    def get_level_weight(cls, level: str) -> int:
        """获取日志级别权重"""
        normalized = cls.normalize_level(level)
        return cls.LEVEL_WEIGHTS.get(normalized, -1)

    @classmethod
    def is_error_or_above(cls, level: str) -> bool:
        """判断是否为 ERROR 或更高级别"""
        weight = cls.get_level_weight(level)
        return weight >= cls.LEVEL_WEIGHTS.get("ERROR", 4)


class ValidationUtils:
    """数据验证工具类"""

    @staticmethod
    def is_valid_log_file(filename: str) -> bool:
        """检查文件名是否为支持的日志文件格式"""
        valid_extensions = (".log", ".jsonl")
        return filename.lower().endswith(valid_extensions)

    @staticmethod
    def is_jsonl_file(filename: str) -> bool:
        """检查是否为 JSONL 格式文件"""
        return filename.lower().endswith(".jsonl")

    @staticmethod
    def is_plain_log_file(filename: str) -> bool:
        """检查是否为纯文本日志文件"""
        return filename.lower().endswith(".log")
