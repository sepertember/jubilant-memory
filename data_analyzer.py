"""
数据分析模块
实现日志数据的统计、过滤和分析逻辑
"""
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from log_reader import LogEntry
from utils import TimeUtils, LevelUtils, StringUtils


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    total_entries: int = 0
    level_distribution: Dict[str, int] = field(default_factory=dict)
    hourly_distribution: Dict[str, int] = field(default_factory=dict)
    top_errors: List[Tuple[str, int]] = field(default_factory=list)
    ip_distribution: Dict[str, int] = field(default_factory=dict)
    time_range: Optional[Tuple[datetime, datetime]] = None
    parse_errors: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_entries": self.total_entries,
            "level_distribution": self.level_distribution,
            "hourly_distribution": self.hourly_distribution,
            "top_errors": [{"message": msg, "count": count} for msg, count in self.top_errors],
            "ip_distribution": self.ip_distribution,
            "time_range": {
                "start": self.time_range[0].isoformat() if self.time_range else None,
                "end": self.time_range[1].isoformat() if self.time_range else None,
            } if self.time_range else None,
            "parse_errors": self.parse_errors,
        }


class DataAnalyzer:
    """
    日志数据分析器
    负责统计和分析日志数据
    """

    def __init__(self):
        self.entries: List[LogEntry] = []
        self.result = AnalysisResult()

    def add_entries(self, entries):
        """添加日志条目到分析器"""
        if isinstance(entries, (list, tuple)):
            self.entries.extend(entries)
        else:
            # 假设是迭代器
            for entry in entries:
                self.entries.append(entry)

    def analyze(self) -> AnalysisResult:
        """执行完整的数据分析"""
        if not self.entries:
            return self.result

        self.result.total_entries = len(self.entries)

        # 统计错误级别分布
        self._analyze_level_distribution()

        # 按小时统计
        self._analyze_hourly_distribution()

        # 统计最常见的错误
        self._analyze_top_errors()

        # 统计 IP 分布
        self._analyze_ip_distribution()

        # 计算时间范围
        self._analyze_time_range()

        # 统计解析错误
        self._count_parse_errors()

        return self.result

    def _analyze_level_distribution(self):
        """分析错误级别分布"""
        level_counter = Counter()
        for entry in self.entries:
            level = entry.level if entry.level else "UNKNOWN"
            level_counter[level] += 1

        # 按级别权重排序
        sorted_levels = sorted(
            level_counter.items(),
            key=lambda x: LevelUtils.get_level_weight(x[0]),
            reverse=True
        )
        self.result.level_distribution = dict(sorted_levels)

    def _analyze_hourly_distribution(self):
        """按小时维度统计日志条目数量"""
        hourly_counter = Counter()

        for entry in self.entries:
            if entry.timestamp:
                hour_key = TimeUtils.extract_hour_key(entry.timestamp)
                hourly_counter[hour_key] += 1

        # 按时间排序
        self.result.hourly_distribution = dict(sorted(hourly_counter.items()))

    def _analyze_top_errors(self, top_n: int = 10):
        """识别出现频率最高的前 N 个错误信息"""
        # 只统计 ERROR 和 CRITICAL 级别的日志
        error_messages = []
        for entry in self.entries:
            if LevelUtils.is_error_or_above(entry.level):
                # 清理并截断消息
                cleaned_msg = StringUtils.clean_message(entry.message)
                cleaned_msg = StringUtils.truncate(cleaned_msg, 200)
                error_messages.append(cleaned_msg)

        message_counter = Counter(error_messages)
        self.result.top_errors = message_counter.most_common(top_n)

    def _analyze_ip_distribution(self):
        """分析请求 IP 分布"""
        ip_counter = Counter()
        for entry in self.entries:
            if entry.source_ip:
                ip_counter[entry.source_ip] += 1

        # 只保留出现次数最多的前 20 个 IP
        self.result.ip_distribution = dict(ip_counter.most_common(20))

    def _analyze_time_range(self):
        """分析日志的时间范围"""
        timestamps = [e.timestamp for e in self.entries if e.timestamp]

        if timestamps:
            self.result.time_range = (min(timestamps), max(timestamps))

    def _count_parse_errors(self):
        """统计解析错误的数量"""
        self.result.parse_errors = sum(
            1 for e in self.entries if e.level == "PARSE_ERROR"
        )

    def filter_by_level(self, level: str) -> List[LogEntry]:
        """按日志级别过滤条目"""
        normalized_level = LevelUtils.normalize_level(level)
        return [e for e in self.entries if e.level == normalized_level]

    def filter_by_time_range(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[LogEntry]:
        """按时间范围过滤条目"""
        result = self.entries

        if start:
            result = [e for e in result if e.timestamp and e.timestamp >= start]
        if end:
            result = [e for e in result if e.timestamp and e.timestamp <= end]

        return result

    def filter_by_ip(self, ip: str) -> List[LogEntry]:
        """按 IP 地址过滤条目"""
        return [e for e in self.entries if e.source_ip == ip]

    def get_error_rate(self) -> float:
        """计算错误率（ERROR 和 CRITICAL 占总条目的比例）"""
        if not self.entries:
            return 0.0

        error_count = sum(
            1 for e in self.entries
            if LevelUtils.is_error_or_above(e.level)
        )
        return error_count / len(self.entries)

    def get_statistics_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        if not self.result.total_entries:
            self.analyze()

        return {
            "total_entries": self.result.total_entries,
            "unique_levels": len(self.result.level_distribution),
            "unique_ips": len(self.result.ip_distribution),
            "error_rate": f"{self.get_error_rate() * 100:.2f}%",
            "time_span_hours": self._calculate_time_span_hours(),
            "parse_errors": self.result.parse_errors,
        }

    def _calculate_time_span_hours(self) -> Optional[float]:
        """计算日志时间跨度（小时）"""
        if not self.result.time_range:
            return None

        start, end = self.result.time_range
        delta = end - start
        return delta.total_seconds() / 3600


class TrendAnalyzer:
    """
    趋势分析器
    分析日志趋势和模式
    """

    def __init__(self, hourly_data: Dict[str, int]):
        self.hourly_data = hourly_data

    def get_peak_hours(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """获取日志量最高的前 N 个小时"""
        return Counter(self.hourly_data).most_common(top_n)

    def get_quiet_hours(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """获取日志量最低的前 N 个小时"""
        sorted_data = sorted(self.hourly_data.items(), key=lambda x: x[1])
        return sorted_data[:top_n]

    def calculate_average_per_hour(self) -> float:
        """计算平均每小时的日志量"""
        if not self.hourly_data:
            return 0.0
        return sum(self.hourly_data.values()) / len(self.hourly_data)

    def detect_anomalies(self, threshold_multiplier: float = 2.0) -> List[Tuple[str, int]]:
        """
        检测异常时段（日志量显著高于平均值）
        threshold_multiplier: 超过平均值多少倍视为异常
        """
        avg = self.calculate_average_per_hour()
        threshold = avg * threshold_multiplier

        anomalies = [
            (hour, count)
            for hour, count in self.hourly_data.items()
            if count > threshold
        ]

        return sorted(anomalies, key=lambda x: x[1], reverse=True)
