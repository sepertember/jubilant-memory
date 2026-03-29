# jubilant-memory

多格式日志文件分析与可视化工具

## 项目简介

这是一个模块化的日志分析工具，能够读取不同格式的日志文件，提取关键指标（如错误类型、时间戳、请求 IP），统计分析后生成结构化的文本可视化报告。

## 功能特性

- ✅ 支持解析 `.log`（纯文本日志）和 `.jsonl`（JSON 行日志）两种格式
- ✅ 提取并统计日志错误级别（INFO/WARN/ERROR/CRITICAL）分布
- ✅ 按小时维度统计指定时间范围内的日志条目数量
- ✅ 识别并列出出现频率最高的前 10 个错误信息
- ✅ 统计请求来源 IP 分布
- ✅ 生成 ASCII 可视化图表（柱状图、趋势图）
- ✅ 同时输出文本报告和 JSON 结构化数据

## 文件结构

```
├── main.py              # 程序入口，处理命令行参数
├── path_manager.py      # 路径管理模块（输入输出路径校验、创建）
├── utils.py             # 通用工具函数（时间解析、字符串处理）
├── log_reader.py        # 日志读取解析模块
├── data_analyzer.py     # 数据分析统计模块
├── report_generator.py  # 报告生成模块（ASCII 图表、JSON）
├── log_input/           # 输入目录（放置待分析的日志文件）
│   └── system_base.log  # 系统核心日志（只读保护）
└── log_analysis_output/ # 输出目录（自动创建）
    ├── log_summary.txt  # 文本可视化报告
    └── log_summary.json # 结构化数据报告
```

## 使用方法

### 基本使用
```bash
# 分析所有日志文件
python main.py

# 带时间范围过滤
python main.py -s "2026-03-16 08:00:00" -e "2026-03-16 18:00:00"

# 显示详细报告到控制台
python main.py --verbose
```

### 命令行参数
- `-s, --start-time` : 开始时间 (格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)
- `-e, --end-time`   : 结束时间 (格式同上)
- `-v, --verbose`    : 输出详细报告到控制台

## 输入输出说明

### 输入
- 日志文件需放置在 `./log_input/` 目录下
- 支持 `.log` 和 `.jsonl` 格式
- `system_base.log` 为系统核心日志，自动设为只读保护

### 输出
- 分析结果输出到 `./log_analysis_output/` 目录
- `log_summary.txt` : ASCII 可视化文本报告
- `log_summary.json` : 结构化 JSON 数据

## 技术栈

- Python 3.9+
- 仅使用 Python 标准库

## 约束条件

1. 严格从 `./log_input/` 读取，输出到 `./log_analysis_output/`
2. `system_base.log` 禁止修改，代码中包含只读校验
3. 报告必须同时输出 `.txt` 和 `.json` 两种格式
4. 禁止使用第三方库（如 pandas、matplotlib）
