"""
报告生成模块
生成文本可视化报告和 JSON 结构化报告
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from data_analyzer import AnalysisResult, TrendAnalyzer
from utils import StringUtils
from path_manager import PathManager


class ASCIIChartGenerator:
    """ASCII 图表生成器"""

    @staticmethod
    def horizontal_bar(
        data: Dict[str, int],
        width: int = 50,
        title: str = "",
        show_percentage: bool = True
    ) -> str:
        """生成水平条形图"""
        if not data:
            return "暂无数据\n"

        lines = []
        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        max_label_len = max(len(str(k)) for k in data.keys()) if data else 0
        max_value = max(data.values()) if data else 1
        total = sum(data.values())

        for label, value in data.items():
            bar_length = int((value / max_value) * width) if max_value > 0 else 0
            bar = "█" * bar_length
            percentage = (value / total * 100) if total > 0 else 0

            label_str = StringUtils.pad_right(str(label), max_label_len)
            if show_percentage:
                lines.append(f"{label_str} │{bar:<{width}}│ {value:>6} ({percentage:5.1f}%)")
            else:
                lines.append(f"{label_str} │{bar:<{width}}│ {value:>6}")

        return "\n".join(lines)

    @staticmethod
    def vertical_bar(
        data: Dict[str, int],
        height: int = 10,
        width: int = 3,
        title: str = ""
    ) -> str:
        """生成垂直条形图（趋势图）"""
        if not data:
            return "暂无数据\n"

        lines = []
        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        items = list(data.items())
        max_value = max(data.values()) if data else 1

        # 构建图表
        for row in range(height, 0, -1):
            line = ""
            threshold = (row - 1) * (max_value / height)

            for _, value in items:
                if value >= threshold + (max_value / height):
                    line += "█" * width + " "
                elif value >= threshold:
                    line += "▄" * width + " "
                else:
                    line += " " * width + " "

            lines.append(f"{line}")

        # 添加 X 轴标签
        x_axis = ""
        for label, _ in items:
            short_label = str(label)[-5:] if len(str(label)) > 5 else str(label)
            x_axis += StringUtils.pad_center(short_label, width) + " "

        lines.append("-" * len(x_axis))
        lines.append(x_axis)

        return "\n".join(lines)

    @staticmethod
    def simple_trend_chart(
        data: Dict[str, int],
        height: int = 8,
        title: str = ""
    ) -> str:
        """生成简单的趋势折线图"""
        if not data:
            return "暂无数据\n"

        lines = []
        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        items = list(data.items())
        if len(items) < 2:
            return ASCIIChartGenerator.horizontal_bar(data, title=title)

        max_value = max(v for _, v in items) if items else 1
        min_value = min(v for _, v in items) if items else 0
        value_range = max_value - min_value if max_value != min_value else 1

        chart_width = min(len(items) * 4, 80)
        chart = [[" " for _ in range(chart_width)] for _ in range(height)]

        # 绘制趋势线
        for i in range(len(items) - 1):
            x1 = int(i * (chart_width - 1) / (len(items) - 1))
            x2 = int((i + 1) * (chart_width - 1) / (len(items) - 1))
            y1 = height - 1 - int(((items[i][1] - min_value) / value_range) * (height - 1))
            y2 = height - 1 - int(((items[i + 1][1] - min_value) / value_range) * (height - 1))

            # 简单的线条绘制
            chart[y1][x1] = "●"
            if y1 == y2:
                for x in range(x1 + 1, x2):
                    chart[y1][x] = "─"
            elif y1 < y2:
                for y in range(y1, y2 + 1):
                    chart[y][x1] = "│"
            else:
                for y in range(y2, y1 + 1):
                    chart[y][x1] = "│"

        # 最后一个点
        last_x = chart_width - 1
        last_y = height - 1 - int(((items[-1][1] - min_value) / value_range) * (height - 1))
        chart[last_y][last_x] = "●"

        # 转换为字符串
        for row in chart:
            lines.append("".join(row))

        return "\n".join(lines)

    @staticmethod
    def table(
        headers: List[str],
        rows: List[List[str]],
        title: str = ""
    ) -> str:
        """生成 ASCII 表格"""
        if not rows:
            return "暂无数据\n"

        lines = []
        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        # 计算列宽
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # 构建表格
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        # 表头
        lines.append(separator)
        header_row = "|" + "|".join(
            f" {StringUtils.pad_right(headers[i], col_widths[i])} "
            for i in range(len(headers))
        ) + "|"
        lines.append(header_row)
        lines.append(separator)

        # 数据行
        for row in rows:
            data_row = "|" + "|".join(
                f" {StringUtils.pad_right(str(row[i]) if i < len(row) else '', col_widths[i])} "
                for i in range(len(headers))
            ) + "|"
            lines.append(data_row)

        lines.append(separator)

        return "\n".join(lines)


class ReportGenerator:
    """
    报告生成器
    生成文本和 JSON 格式的分析报告
    """

    def __init__(self, path_manager: PathManager):
        self.path_manager = path_manager
        self.chart_gen = ASCIIChartGenerator()

    def generate_txt_report(self, result: AnalysisResult, stats: Dict[str, Any]) -> str:
        """生成文本格式报告"""
        lines = []

        # 报告标题
        lines.append("=" * 80)
        lines.append(StringUtils.pad_center("日志分析报告", 80))
        lines.append("=" * 80)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 摘要信息
        lines.append("-" * 80)
        lines.append("【摘要信息】")
        lines.append("-" * 80)
        lines.append(f"  总日志条目数: {stats['total_entries']:,}")
        lines.append(f"  日志级别种类: {stats['unique_levels']}")
        lines.append(f"  唯一 IP 数量: {stats['unique_ips']}")
        lines.append(f"  错误率: {stats['error_rate']}")
        lines.append(f"  时间跨度: {stats['time_span_hours']:.1f} 小时" if stats['time_span_hours'] else "  时间跨度: N/A")
        lines.append(f"  解析错误: {stats['parse_errors']} 条")
        lines.append("")

        # 错误级别分布
        if result.level_distribution:
            lines.append(self.chart_gen.horizontal_bar(
                result.level_distribution,
                title="错误级别分布",
                width=40
            ))
            lines.append("")

        # 按小时统计
        if result.hourly_distribution:
            lines.append(self.chart_gen.vertical_bar(
                self._limit_data_points(result.hourly_distribution, 20),
                title="按小时统计（最近20小时）",
                height=10
            ))
            lines.append("")

            # 添加趋势图
            lines.append(self.chart_gen.simple_trend_chart(
                self._limit_data_points(result.hourly_distribution, 30),
                title="日志趋势图（最近30小时）",
                height=8
            ))
            lines.append("")

        # Top 10 错误信息
        if result.top_errors:
            lines.append("-" * 80)
            lines.append("【Top 10 错误信息】")
            lines.append("-" * 80)

            rows = []
            for i, (msg, count) in enumerate(result.top_errors, 1):
                truncated_msg = StringUtils.truncate(msg, 60)
                rows.append([str(i), truncated_msg, str(count)])

            lines.append(self.chart_gen.table(
                headers=["排名", "错误信息", "出现次数"],
                rows=rows
            ))
            lines.append("")

        # IP 分布
        if result.ip_distribution:
            lines.append(self.chart_gen.horizontal_bar(
                dict(list(result.ip_distribution.items())[:10]),
                title="Top 10 请求 IP 分布",
                width=30
            ))
            lines.append("")

        # 异常检测
        if result.hourly_distribution:
            trend_analyzer = TrendAnalyzer(result.hourly_distribution)
            anomalies = trend_analyzer.detect_anomalies(threshold_multiplier=2.0)

            if anomalies:
                lines.append("-" * 80)
                lines.append("【异常时段检测】")
                lines.append("-" * 80)
                lines.append("以下时段的日志量显著高于平均值（>2倍）:")

                rows = []
                for hour, count in anomalies[:5]:
                    rows.append([hour, str(count)])

                lines.append(self.chart_gen.table(
                    headers=["时间", "日志数量"],
                    rows=rows
                ))
                lines.append("")

        # 报告结尾
        lines.append("=" * 80)
        lines.append(StringUtils.pad_center("报告结束", 80))
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_json_report(self, result: AnalysisResult, stats: Dict[str, Any]) -> str:
        """生成 JSON 格式报告"""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
            },
            "summary": stats,
            "analysis": result.to_dict(),
        }

        # 添加趋势分析
        if result.hourly_distribution:
            trend_analyzer = TrendAnalyzer(result.hourly_distribution)
            report["trend_analysis"] = {
                "peak_hours": [
                    {"hour": hour, "count": count}
                    for hour, count in trend_analyzer.get_peak_hours(5)
                ],
                "quiet_hours": [
                    {"hour": hour, "count": count}
                    for hour, count in trend_analyzer.get_quiet_hours(5)
                ],
                "average_per_hour": trend_analyzer.calculate_average_per_hour(),
                "anomalies": [
                    {"hour": hour, "count": count}
                    for hour, count in trend_analyzer.detect_anomalies(2.0)[:5]
                ],
            }

        return json.dumps(report, ensure_ascii=False, indent=2)

    def save_reports(self, result: AnalysisResult, stats: Dict[str, Any]):
        """保存两种格式的报告到输出目录"""
        # 确保输出目录存在
        self.path_manager.ensure_output_dir()

        # 生成并保存文本报告
        txt_report = self.generate_txt_report(result, stats)
        txt_path = self.path_manager.get_output_txt_path()

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_report)
        print(f"文本报告已保存: {txt_path}")

        # 生成并保存 JSON 报告
        json_report = self.generate_json_report(result, stats)
        json_path = self.path_manager.get_output_json_path()

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_report)
        print(f"JSON 报告已保存: {json_path}")

    @staticmethod
    def _limit_data_points(data: Dict[str, int], max_points: int) -> Dict[str, int]:
        """限制数据点数量，保留最新的 N 个"""
        if len(data) <= max_points:
            return data

        sorted_items = sorted(data.items())
        return dict(sorted_items[-max_points:])
