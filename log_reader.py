import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime

from path_manager import is_system_log, validate_system_log_readonly
from utils import extract_timestamp, extract_level, extract_ip, extract_error_message

class LogEntry:
    def __init__(self):
        self.timestamp: Optional[datetime] = None
        self.level: Optional[str] = None
        self.ip: Optional[str] = None
        self.message: str = ""
        self.raw_line: str = ""
        self.source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "ip": self.ip,
            "message": self.message,
            "source_file": self.source_file
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        entry = cls()
        if data.get("timestamp"):
            from utils import parse_timestamp
            entry.timestamp = parse_timestamp(data["timestamp"])
        entry.level = data.get("level")
        entry.ip = data.get("ip")
        entry.message = data.get("message", "")
        entry.source_file = data.get("source_file", "")
        return entry

def read_plain_log(file_path: str) -> List[LogEntry]:
    entries = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line.strip():
                    continue
                entry = parse_plain_log_line(line)
                entry.source_file = file_path
                entry.raw_line = line
                entries.append(entry)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return entries

def parse_plain_log_line(line: str) -> LogEntry:
    entry = LogEntry()
    entry.timestamp = extract_timestamp(line)
    entry.level = extract_level(line)
    entry.ip = extract_ip(line)
    entry.message = extract_error_message(line)
    entry.raw_line = line
    return entry

def read_jsonl_log(file_path: str) -> List[LogEntry]:
    entries = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = parse_jsonl_entry(data)
                    entry.source_file = file_path
                    entry.raw_line = line
                    entries.append(entry)
                except json.JSONDecodeError:
                    entry = parse_plain_log_line(line)
                    entry.source_file = file_path
                    entry.raw_line = line
                    entries.append(entry)
    except Exception as e:
        print(f"Error reading JSONL {file_path}: {e}")
    return entries

def parse_jsonl_entry(data: Dict[str, Any]) -> LogEntry:
    entry = LogEntry()
    
    ts = data.get("timestamp") or data.get("time") or data.get("datetime")
    if ts:
        from utils import parse_timestamp
        if isinstance(ts, str):
            entry.timestamp = parse_timestamp(ts)
    
    entry.level = data.get("level") or data.get("severity") or data.get("log_level")
    if entry.level:
        entry.level = str(entry.level).upper()
    
    entry.ip = data.get("ip") or data.get("client_ip") or data.get("remote_addr")
    
    entry.message = str(data.get("message") or data.get("msg") or data.get("content") or "")
    
    return entry

def read_log_file(file_path: str) -> List[LogEntry]:
    validate_system_log_readonly()
    
    if is_system_log(file_path):
        if os.access(file_path, os.W_OK):
            raise PermissionError(f"System log file {file_path} must be read-only!")
    
    if file_path.endswith('.jsonl'):
        return read_jsonl_log(file_path)
    elif file_path.endswith('.log'):
        return read_plain_log(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def read_all_log_files(file_paths: List[str]) -> List[LogEntry]:
    all_entries = []
    for file_path in file_paths:
        entries = read_log_file(file_path)
        all_entries.extend(entries)
    return all_entries
