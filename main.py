"""
多格式日志文件分析与可视化工具
程序入口，处理命令行参数并调用核心分析逻辑
"""
import argparse
import sys
from pathlib import Path

from path_manager import PathManager
from log_reader import LogReader
from data_analyzer import DataAnalyzer
from report_generator import ReportGenerator


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="log_analyzer",
        description="多格式日志文件分析与可视化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    # 分析所有日志文件
  python main.py --stats-only       # 仅显示统计摘要
  python main.py --verbose          # 显示详细日志
        """
    )

    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="仅显示统计摘要，不生成详细报告"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细处理信息"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           多格式日志文件分析与可视化工具 v1.0.0              ║
║                                                              ║
║           支持 .log 和 .jsonl 格式                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(stats: dict):
    """打印统计摘要"""
    print("\n" + "=" * 60)
    print("统计摘要")
    print("=" * 60)
    print(f"  总日志条目数: {stats['total_entries']:,}")
    print(f"  日志级别种类: {stats['unique_levels']}")
    print(f"  唯一 IP 数量: {stats['unique_ips']}")
    print(f"  错误率: {stats['error_rate']}")
    if stats['time_span_hours']:
        print(f"  时间跨度: {stats['time_span_hours']:.1f} 小时")
    print(f"  解析错误: {stats['parse_errors']} 条")
    print("=" * 60)


def main():
    """主函数"""
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()

    # 打印横幅
    print_banner()

    try:
        # 初始化路径管理器
        path_manager = PathManager()

        # 验证输入目录
        print(f"输入目录: {path_manager.input_path}")
        path_manager.validate_input_dir()

        # 检查受保护文件
        print(f"检查受保护文件: {path_manager.PROTECTED_FILE}")
        path_manager.check_protected_file_readonly()

        # 确保输出目录存在
        path_manager.ensure_output_dir()
        print(f"输出目录: {path_manager.output_path}")

        # 初始化日志读取器
        log_reader = LogReader(path_manager)

        # 获取文件统计信息
        file_stats = log_reader.get_file_stats()
        print(f"\n找到 {file_stats['total_files']} 个日志文件:")
        for file_info in file_stats['log_files']:
            protected_mark = " [受保护]" if file_info['is_protected'] else ""
            print(f"  - {file_info['name']} ({file_info['size']:,} bytes){protected_mark}")
        for file_info in file_stats['jsonl_files']:
            print(f"  - {file_info['name']} ({file_info['size']:,} bytes) [JSONL]")

        if file_stats['total_files'] == 0:
            print("\n错误: 未找到日志文件，请将 .log 或 .jsonl 文件放入 ./log_input/ 目录")
            sys.exit(1)

        # 读取所有日志条目
        print("\n开始读取日志文件...")
        entries = list(log_reader.read_all_files())
        print(f"共读取 {len(entries)} 条日志记录")

        if len(entries) == 0:
            print("\n警告: 未解析到任何日志记录")
            sys.exit(0)

        # 数据分析
        print("\n开始分析数据...")
        analyzer = DataAnalyzer()
        analyzer.add_entries(entries)
        result = analyzer.analyze()

        # 获取统计摘要
        stats = analyzer.get_statistics_summary()

        # 打印统计摘要
        print_summary(stats)

        if args.verbose:
            print("\n详细分析结果:")
            print(f"  错误级别分布: {result.level_distribution}")
            print(f"  时间范围: {result.time_range}")

        # 生成报告（如果不是仅统计模式）
        if not args.stats_only:
            print("\n正在生成报告...")
            report_generator = ReportGenerator(path_manager)
            report_generator.save_reports(result, stats)

        print("\n✓ 分析完成!")

    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        print("请确保 ./log_input/ 目录存在且包含日志文件")
        sys.exit(1)

    except PermissionError as e:
        print(f"\n权限错误: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
