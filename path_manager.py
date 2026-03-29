import os
import stat
from typing import Tuple

INPUT_DIR = "./log_input/"
OUTPUT_DIR = "./log_analysis_output/"
SYSTEM_LOG_FILE = "system_base.log"

def get_absolute_path(path: str) -> str:
    return os.path.abspath(path)

def ensure_input_dir_exists() -> str:
    abs_path = get_absolute_path(INPUT_DIR)
    if not os.path.exists(abs_path):
        os.makedirs(abs_path, exist_ok=True)
    return abs_path

def ensure_output_dir_exists() -> str:
    abs_path = get_absolute_path(OUTPUT_DIR)
    if not os.path.exists(abs_path):
        os.makedirs(abs_path, exist_ok=True)
    return abs_path

def get_input_dir() -> str:
    return ensure_input_dir_exists()

def get_output_dir() -> str:
    return ensure_output_dir_exists()

def get_system_log_path() -> str:
    return os.path.join(get_input_dir(), SYSTEM_LOG_FILE)

def is_file_readonly(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False
    file_stat = os.stat(file_path)
    return not (file_stat.st_mode & stat.S_IWRITE)

def validate_system_log_readonly() -> bool:
    sys_log_path = get_system_log_path()
    if not os.path.exists(sys_log_path):
        return True
    if not is_file_readonly(sys_log_path):
        try:
            os.chmod(sys_log_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        except OSError:
            pass
    return True

def get_log_files() -> list:
    input_dir = get_input_dir()
    log_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(('.log', '.jsonl')):
                log_files.append(os.path.join(root, file))
    return log_files

def get_output_file_paths() -> Tuple[str, str]:
    output_dir = get_output_dir()
    txt_path = os.path.join(output_dir, "log_summary.txt")
    json_path = os.path.join(output_dir, "log_summary.json")
    return txt_path, json_path

def is_system_log(file_path: str) -> bool:
    abs_path = get_absolute_path(file_path)
    sys_log_abs = get_system_log_path()
    return abs_path == sys_log_abs
