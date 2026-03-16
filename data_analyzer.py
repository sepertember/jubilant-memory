from collections import Counter
from typing import List, Dict, Optional, Any
from datetime import datetime

from log_reader import LogEntry
from utils import get_hour_key, is_in_time_range, truncate_string

VALID_LEVELS = {'INFO', 'WARN', 'ERROR', 'CRITICAL'}

def analyze_level_distribution(entries: List[LogEntry]) -> Dict[str, int]:
    counter = Counter()
    for entry in entries:
        level = entry.level
        if level in VALID_LEVELS:
            counter[level] += 1
        else:
            counter['OTHER'] += 1
    return dict(counter)

def analyze_hourly_trend(entries: List[LogEntry], 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, int]:
    counter = Counter()
    for entry in entries:
        if not entry.timestamp:
            continue
        if not is_in_time_range(entry.timestamp, start_time, end_time):
            continue
        hour_key = get_hour_key(entry.timestamp)
        counter[hour_key] += 1
    return dict(sorted(counter.items()))

def analyze_top_errors(entries: List[LogEntry], top_n: int = 10) -> List[Dict[str, Any]]:
    error_messages = []
    for entry in entries:
        if entry.level in ('ERROR', 'CRITICAL'):
            msg = truncate_string(entry.message, 100)
            if msg:
                error_messages.append(msg)
    
    counter = Counter(error_messages)
    top_errors = []
    for msg, count in counter.most_common(top_n):
        top_errors.append({
            "message": msg,
            "count": count
        })
    return top_errors

def analyze_ip_distribution(entries: List[LogEntry], top_n: int = 10) -> Dict[str, int]:
    counter = Counter()
    for entry in entries:
        if entry.ip:
            counter[entry.ip] += 1
    return dict(counter.most_common(top_n))

def filter_by_level(entries: List[LogEntry], levels: List[str]) -> List[LogEntry]:
    upper_levels = {l.upper() for l in levels}
    return [e for e in entries if e.level in upper_levels]

def filter_by_time(entries: List[LogEntry], 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[LogEntry]:
    result = []
    for entry in entries:
        if entry.timestamp and is_in_time_range(entry.timestamp, start_time, end_time):
            result.append(entry)
    return result

def get_total_entries(entries: List[LogEntry]) -> int:
    return len(entries)

def get_error_count(entries: List[LogEntry]) -> int:
    return sum(1 for e in entries if e.level in ('ERROR', 'CRITICAL'))

def get_warning_count(entries: List[LogEntry]) -> int:
    return sum(1 for e in entries if e.level == 'WARN')

def get_time_range(entries: List[LogEntry]) -> Dict[str, Optional[str]]:
    timestamps = [e.timestamp for e in entries if e.timestamp]
    if not timestamps:
        return {"start": None, "end": None}
    min_ts = min(timestamps)
    max_ts = max(timestamps)
    return {
        "start": min_ts.isoformat() if min_ts else None,
        "end": max_ts.isoformat() if max_ts else None
    }

def analyze_all(entries: List[LogEntry],
                start_time: Optional[datetime] = None,
                end_time: Optional[datetime] = None) -> Dict[str, Any]:
    
    filtered = filter_by_time(entries, start_time, end_time) if start_time or end_time else entries
    
    return {
        "summary": {
            "total_entries": get_total_entries(filtered),
            "error_count": get_error_count(filtered),
            "warning_count": get_warning_count(filtered),
            "time_range": get_time_range(filtered)
        },
        "level_distribution": analyze_level_distribution(filtered),
        "hourly_trend": analyze_hourly_trend(filtered, start_time, end_time),
        "top_errors": analyze_top_errors(filtered, 10),
        "top_ips": analyze_ip_distribution(filtered, 10)
    }
