import json
from typing import Dict, Any, List
from datetime import datetime

from path_manager import get_output_file_paths

def generate_ascii_table(data: Dict[str, int], title: str, 
                         key_header: str = "Key", 
                         value_header: str = "Count") -> str:
    if not data:
        return f"\n=== {title} ===\nNo data available.\n"
    
    max_key_len = max(len(str(k)) for k in data.keys())
    max_key_len = max(max_key_len, len(key_header))
    max_val_len = max(len(str(v)) for v in data.values())
    max_val_len = max(max_val_len, len(value_header))
    
    width = max_key_len + max_val_len + 7
    
    lines = []
    lines.append(f"\n{'='*width}")
    lines.append(f"{title:^{width}}")
    lines.append(f"{'='*width}")
    
    header = f"| {key_header:<{max_key_len}} | {value_header:>{max_val_len}} |"
    lines.append(header)
    lines.append(f"+{'-'*(max_key_len+2)}+{'-'*(max_val_len+2)}+")
    
    for key, value in sorted(data.items()):
        lines.append(f"| {str(key):<{max_key_len}} | {str(value):>{max_val_len}} |")
    
    lines.append(f"{'='*width}\n")
    return "\n".join(lines)

def generate_bar_chart(data: Dict[str, int], title: str, 
                       max_bar_width: int = 40) -> str:
    if not data:
        return f"\n=== {title} ===\nNo data available.\n"
    
    max_val = max(data.values()) if data else 1
    max_val = max(max_val, 1)
    
    max_key_len = max(len(str(k)) for k in data.keys())
    
    lines = []
    width = max_key_len + max_bar_width + 10
    lines.append(f"\n{'='*width}")
    lines.append(f"{title:^{width}}")
    lines.append(f"{'='*width}\n")
    
    for key, value in sorted(data.items()):
        bar_length = int((value / max_val) * max_bar_width) if max_val > 0 else 0
        bar = '█' * bar_length
        lines.append(f"{str(key):>{max_key_len}} | {bar:<{max_bar_width}} | {value}")
    
    lines.append(f"\n{'='*width}\n")
    return "\n".join(lines)

def generate_trend_chart(hourly_data: Dict[str, int], title: str) -> str:
    if not hourly_data:
        return f"\n=== {title} ===\nNo data available.\n"
    
    sorted_hours = sorted(hourly_data.keys())
    values = [hourly_data[h] for h in sorted_hours]
    
    max_val = max(values) if values else 1
    height = 10
    
    lines = []
    width = len(sorted_hours) * 4 + 10
    lines.append(f"\n{'='*width}")
    lines.append(f"{title:^{width}}")
    lines.append(f"{'='*width}\n")
    
    for row in range(height, -1, -1):
        threshold = (row / height) * max_val if max_val > 0 else 0
        line = f"{int(threshold):>3} | "
        for val in values:
            if val >= threshold:
                line += "███ "
            else:
                line += "    "
        lines.append(line)
    
    x_axis = "    +" + "-" * (len(sorted_hours) * 4 - 1)
    lines.append(x_axis)
    
    hour_labels = ["    "]
    for hour in sorted_hours:
        short_hour = hour.split(' ')[1][:2] if ' ' in hour else hour[:2]
        hour_labels.append(f"{short_hour:^4}")
    lines.append("".join(hour_labels))
    
    lines.append(f"\n{'='*width}\n")
    return "\n".join(lines)

def generate_top_errors_table(errors: List[Dict[str, Any]], title: str) -> str:
    if not errors:
        return f"\n=== {title} ===\nNo error data available.\n"
    
    msg_width = 60
    count_width = 10
    rank_width = 6
    
    width = msg_width + count_width + rank_width + 10
    
    lines = []
    lines.append(f"\n{'='*width}")
    lines.append(f"{title:^{width}}")
    lines.append(f"{'='*width}")
    
    header = f"| {'Rank':^{rank_width}} | {'Error Message':^{msg_width}} | {'Count':^{count_width}} |"
    lines.append(header)
    lines.append(f"+{'-'*(rank_width+2)}+{'-'*(msg_width+2)}+{'-'*(count_width+2)}+")
    
    for i, error in enumerate(errors, 1):
        msg = error.get("message", "")
        if len(msg) > msg_width:
            msg = msg[:msg_width-3] + "..."
        count = str(error.get("count", 0))
        lines.append(f"| {str(i):^{rank_width}} | {msg:<{msg_width}} | {count:>{count_width}} |")
    
    lines.append(f"{'='*width}\n")
    return "\n".join(lines)

def generate_summary_section(summary: Dict[str, Any]) -> str:
    lines = []
    lines.append("\n" + "="*80)
    lines.append(f"{'LOG ANALYSIS SUMMARY REPORT':^80}")
    lines.append("="*80 + "\n")
    
    total = summary.get("total_entries", 0)
    errors = summary.get("error_count", 0)
    warnings = summary.get("warning_count", 0)
    
    lines.append(f"Total Log Entries:      {total}")
    lines.append(f"Total Errors:           {errors}")
    lines.append(f"Total Warnings:         {warnings}")
    
    time_range = summary.get("time_range", {})
    if time_range.get("start"):
        lines.append(f"Time Range Start:       {time_range['start']}")
    if time_range.get("end"):
        lines.append(f"Time Range End:         {time_range['end']}")
    
    lines.append(f"Report Generated:       {datetime.now().isoformat()}")
    lines.append("\n" + "="*80 + "\n")
    
    return "\n".join(lines)

def generate_text_report(analysis_result: Dict[str, Any]) -> str:
    sections = []
    
    sections.append(generate_summary_section(analysis_result.get("summary", {})))
    
    level_dist = analysis_result.get("level_distribution", {})
    sections.append(generate_bar_chart(level_dist, "Log Level Distribution"))
    
    hourly = analysis_result.get("hourly_trend", {})
    sections.append(generate_trend_chart(hourly, "Hourly Log Trend"))
    
    top_errors = analysis_result.get("top_errors", [])
    sections.append(generate_top_errors_table(top_errors, "Top 10 Most Frequent Errors"))
    
    top_ips = analysis_result.get("top_ips", {})
    sections.append(generate_ascii_table(top_ips, "Top Client IPs", "IP Address", "Request Count"))
    
    return "\n".join(sections)

def save_report(analysis_result: Dict[str, Any]) -> None:
    txt_path, json_path = get_output_file_paths()
    
    text_report = generate_text_report(analysis_result)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, default=str)
    
    print(f"Reports saved to:")
    print(f"  - {txt_path}")
    print(f"  - {json_path}")
