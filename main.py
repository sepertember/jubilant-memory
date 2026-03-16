import argparse
import sys
from datetime import datetime
from typing import Optional

from path_manager import get_log_files, validate_system_log_readonly
from log_reader import read_all_log_files
from data_analyzer import analyze_all
from report_generator import save_report, generate_text_report

def parse_time_arg(time_str: str) -> Optional[datetime]:
    if not time_str:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    print(f"Warning: Could not parse time '{time_str}'")
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Log Analysis Tool - Analyze log files and generate reports"
    )
    parser.add_argument(
        "--start-time", "-s",
        type=str,
        default=None,
        help="Start time for filtering (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"
    )
    parser.add_argument(
        "--end-time", "-e",
        type=str,
        default=None,
        help="End time for filtering (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed report to console"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Log Analysis Tool Starting...")
    print("="*60)
    
    validate_system_log_readonly()
    
    log_files = get_log_files()
    print(f"\nFound {len(log_files)} log file(s):")
    for f in log_files:
        print(f"  - {f}")
    
    if not log_files:
        print("\nNo log files found in ./log_input/ directory!")
        print("Please add .log or .jsonl files to analyze.")
        sys.exit(0)
    
    print("\nReading and parsing log files...")
    entries = read_all_log_files(log_files)
    print(f"Total log entries parsed: {len(entries)}")
    
    start_time = parse_time_arg(args.start_time)
    end_time = parse_time_arg(args.end_time)
    
    if start_time or end_time:
        print(f"\nApplying time filter:")
        if start_time:
            print(f"  From: {start_time}")
        if end_time:
            print(f"  To:   {end_time}")
    
    print("\nAnalyzing data...")
    analysis_result = analyze_all(entries, start_time, end_time)
    
    print("\nSaving reports...")
    save_report(analysis_result)
    
    if args.verbose:
        print("\n" + "="*60)
        print("DETAILED REPORT")
        print("="*60)
        print(generate_text_report(analysis_result))
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)

if __name__ == "__main__":
    main()
