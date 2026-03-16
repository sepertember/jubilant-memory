"""
日志读取解析模块
负责不同格式日志文件的读取和解析
"""
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, Dict, Any, List

from utils import TimeUtils, StringUtils, LevelUtils, ValidationUtils
from path_manager import PathManager


@dataclass
class LogEntry:
    """日志条目数据类"""
    timestamp: Optional[datetime]
    level: str
    message: str
    source_ip: Optional[str] = None
    raw_line: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseLogParser(ABC):
    """日志解析器抽象基类"""

    @abstractmethod
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """解析单行日志"""
        pass

    @abstractmethod
    def can_parse(self, line: str) -> bool:
        """判断是否能解析该行"""
        pass


class PlainTextLogParser(BaseLogParser):
    """
    纯文本日志解析器
    支持常见日志格式:
    - 2024-01-15 14:30:25 [INFO] This is a message
    - INFO 2024-01-15 14:30:25 Message here
    - [2024-01-15T14:30:25Z] ERROR: Something went wrong
    """

    # 常见日志格式正则表达式
    LOG_PATTERNS = [
        # 时间 [级别] 消息
        r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s*[\[\(]?([A-Z]+)[\]\)]?\s*:?\s*(.+)",
        # [时间] [级别] 消息
        r"\[(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})\]\s*[\[\(]?([A-Z]+)[\]\)]?\s*:?\s*(.+)",
        # 级别 时间 消息
        r"([A-Z]+)\s+(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})\s*:?\s*(.+)",
        # 简写月份格式: Jan 15 14:30:25 [INFO] message
        r"([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s*[\[\(]?([A-Z]+)[\]\)]?\s*:?\s*(.+)",
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.LOG_PATTERNS]

    def can_parse(self, line: str) -> bool:
        """检查是否能解析该行"""
        for pattern in self.compiled_patterns:
            if pattern.search(line):
                return True
        return False

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """解析单行日志"""
        line = line.strip()
        if not line:
            return None

        # 尝试匹配各种模式
        for pattern in self.compiled_patterns:
            match = pattern.search(line)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    # 确定哪个组是时间，哪个是级别
                    timestamp_str, level, message = self._identify_groups(groups)

                    timestamp = TimeUtils.parse_datetime(timestamp_str)
                    level = LevelUtils.normalize_level(level)
                    message = StringUtils.clean_message(message)
                    source_ip = StringUtils.extract_ip(line)

                    return LogEntry(
                        timestamp=timestamp,
                        level=level,
                        message=message,
                        source_ip=source_ip,
                        raw_line=line
                    )

        # 如果无法匹配标准格式，尝试提取级别和消息
        return self._parse_fallback(line)

    def _identify_groups(self, groups: tuple) -> tuple:
        """识别时间、级别和消息组"""
        # 检查第一个组是否包含时间特征
        if re.search(r"\d{4}|\d{2}:\d{2}:\d{2}", groups[0]):
            return groups[0], groups[1], groups[2]
        else:
            # 第一个组可能是级别
            return groups[1], groups[0], groups[2]

    def _parse_fallback(self, line: str) -> Optional[LogEntry]:
        """回退解析方法 - 尝试提取任何可用信息"""
        # 尝试提取时间戳
        timestamp = TimeUtils.parse_datetime(line)

        # 尝试提取日志级别
        level = "UNKNOWN"
        level_pattern = r"\b(INFO|WARN|WARNING|ERROR|CRITICAL|DEBUG|TRACE)\b"
        level_match = re.search(level_pattern, line, re.IGNORECASE)
        if level_match:
            level = LevelUtils.normalize_level(level_match.group(1))

        # 提取 IP 地址
        source_ip = StringUtils.extract_ip(line)

        # 清理消息
        message = StringUtils.clean_message(line)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source_ip=source_ip,
            raw_line=line
        )


class JSONLLogParser(BaseLogParser):
    """
    JSON Lines 日志解析器
    支持 JSON 格式日志，每行一个 JSON 对象
    期望字段: timestamp/time/datetime, level/severity, message/msg, ip/source_ip
    """

    # 可能的字段名映射
    FIELD_MAPPINGS = {
        "timestamp": ["timestamp", "time", "datetime", "date", "ts", "@timestamp"],
        "level": ["level", "severity", "log_level", "levelname", "status"],
        "message": ["message", "msg", "log", "log_message", "text", "content"],
        "source_ip": ["ip", "source_ip", "client_ip", "remote_ip", "host", "client"],
    }

    def can_parse(self, line: str) -> bool:
        """检查是否为有效的 JSON 行"""
        line = line.strip()
        if not line:
            return False
        try:
            json.loads(line)
            return True
        except json.JSONDecodeError:
            return False

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """解析 JSON 行日志"""
        line = line.strip()
        if not line:
            return None

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        # 提取字段
        timestamp = self._extract_timestamp(data)
        level = self._extract_level(data)
        message = self._extract_message(data)
        source_ip = self._extract_source_ip(data)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source_ip=source_ip,
            raw_line=line,
            metadata=data
        )

    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """从数据中提取时间戳"""
        for field in self.FIELD_MAPPINGS["timestamp"]:
            if field in data:
                value = data[field]
                if isinstance(value, (int, float)):
                    # Unix 时间戳
                    return datetime.fromtimestamp(value)
                elif isinstance(value, str):
                    return TimeUtils.parse_datetime(value)
        return None

    def _extract_level(self, data: Dict[str, Any]) -> str:
        """从数据中提取日志级别"""
        for field in self.FIELD_MAPPINGS["level"]:
            if field in data:
                return LevelUtils.normalize_level(str(data[field]))
        return "UNKNOWN"

    def _extract_message(self, data: Dict[str, Any]) -> str:
        """从数据中提取消息"""
        for field in self.FIELD_MAPPINGS["message"]:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    return StringUtils.clean_message(value)
                return str(value)
        # 如果没有找到消息字段，使用整个 JSON 作为消息
        return StringUtils.clean_message(json.dumps(data))

    def _extract_source_ip(self, data: Dict[str, Any]) -> Optional[str]:
        """从数据中提取源 IP"""
        for field in self.FIELD_MAPPINGS["source_ip"]:
            if field in data:
                value = str(data[field])
                # 验证 IP 格式
                if StringUtils.extract_ip(value):
                    return value
        return None


class LogReader:
    """
    日志读取器
    负责读取和解析不同格式的日志文件
    """

    def __init__(self, path_manager: PathManager):
        self.path_manager = path_manager
        self.plain_parser = PlainTextLogParser()
        self.jsonl_parser = JSONLLogParser()

    def read_file(self, file_path: Path) -> Iterator[LogEntry]:
        """
        读取日志文件并返回解析后的条目迭代器
        自动检测文件格式并选择合适的解析器
        """
        file_path = Path(file_path)

        # 检查是否为受保护文件（仅读取，不做修改）
        self.path_manager.validate_safe_operation(file_path, "read")

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 根据扩展名选择解析策略
        if ValidationUtils.is_jsonl_file(file_path.name):
            parser = self.jsonl_parser
        else:
            parser = self.plain_parser

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = parser.parse_line(line)
                    if entry:
                        yield entry
                except Exception as e:
                    # 解析失败时生成一个包含原始行的条目
                    yield LogEntry(
                        timestamp=None,
                        level="PARSE_ERROR",
                        message=f"解析失败 (行 {line_num}): {StringUtils.truncate(line, 100)}",
                        raw_line=line
                    )

    def read_all_files(self) -> Iterator[LogEntry]:
        """读取输入目录下所有日志文件"""
        log_files = self.path_manager.get_input_files()

        if not log_files:
            print(f"警告: 在 {self.path_manager.input_path} 中未找到日志文件")
            return

        for file_path in log_files:
            print(f"正在读取: {file_path.name}")
            yield from self.read_file(file_path)

    def get_file_stats(self) -> Dict[str, Any]:
        """获取输入文件统计信息"""
        log_files = self.path_manager.get_input_files()
        stats = {
            "total_files": len(log_files),
            "log_files": [],
            "jsonl_files": [],
        }

        for file_path in log_files:
            file_info = {
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "is_protected": self.path_manager.is_protected_file(file_path)
            }

            if ValidationUtils.is_jsonl_file(file_path.name):
                stats["jsonl_files"].append(file_info)
            else:
                stats["log_files"].append(file_info)

        return stats
