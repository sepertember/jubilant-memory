import re
from datetime import datetime
from typing import Optional, Dict, List

TIMESTAMP_PATTERNS = [
    r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{3})?)',
    r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]',
    r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',
]

LEVEL_PATTERNS = [
    r'(INFO|WARN|ERROR|CRITICAL)',
    r'\[(INFO|WARN|ERROR|CRITICAL)\]',
]

IP_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

def parse_timestamp(ts_str: str) -> Optional[datetime]:
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    return None

def extract_timestamp(line: str) -> Optional[datetime]:
    for pattern in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            ts_str = match.group(1)
            return parse_timestamp(ts_str)
    return None

def extract_level(line: str) -> Optional[str]:
    for pattern in LEVEL_PATTERNS:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None

def extract_ip(line: str) -> Optional[str]:
    match = re.search(IP_PATTERN, line)
    if match:
        return match.group(0)
    return None

def extract_error_message(line: str) -> str:
    parts = re.split(r'(?:ERROR|CRITICAL|WARN|INFO):?', line, flags=re.IGNORECASE)
    if len(parts) > 1:
        return parts[-1].strip()[:200]
    return line.strip()[:200]

def get_hour_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:00")

def is_in_time_range(dt: datetime, start: Optional[datetime], end: Optional[datetime]) -> bool:
    if start and dt < start:
        return False
    if end and dt > end:
        return False
    return True

def safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b

def format_bytes(size: int) -> str:
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"

def truncate_string(s: str, max_len: int = 50) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len - 3] + "..."

def count_words(s: str) -> int:
    return len(re.findall(r'\w+', s))
