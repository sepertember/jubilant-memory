# 多格式日志文件分析与可视化工具

一个基于 Python 标准库开发的模块化日志分析工具，支持 .log 和 .jsonl 格式，生成 ASCII 可视化报告。

## 功能特性

- **多格式支持**：解析 `.log`（纯文本）和 `.jsonl`（JSON 行）两种日志格式
- **错误级别统计**：统计 INFO/WARN/ERROR/CRITICAL 等级别分布
- **小时维度分析**：按小时统计日志条目数量
- **Top 10 错误**：识别出现频率最高的前 10 个错误信息
- **IP 分布统计**：分析请求 IP 的来源分布
- **ASCII 可视化**：生成条形图、趋势图、表格等文本可视化报告
- **双格式输出**：同时生成 `.txt` 纯文本和 `.json` 结构化数据报告

## 项目结构

```
.
├── main.py                 # 程序入口，处理命令行参数
├── log_reader.py           # 日志文件读取和解析
├── data_analyzer.py        # 数据统计和分析逻辑
├── report_generator.py     # 报告生成（文本 + JSON）
├── path_manager.py         # 路径管理和校验
├── utils.py                # 通用工具函数
├── log_input/              # 输入目录（放置日志文件）
│   ├── system_base.log     # 系统核心日志（受保护，只读）
│   ├── app.log             # 应用程序日志
│   └── access.jsonl        # JSONL 格式日志
└── log_analysis_output/    # 输出目录（自动生成）
    ├── log_summary.txt     # 文本格式报告
    └── log_summary.json    # JSON 格式报告
```

## 使用方法

### 1. 准备日志文件

将需要分析的日志文件放入 `./log_input/` 目录：
- 支持 `.log` 纯文本日志
- 支持 `.jsonl` JSON 行日志

### 2. 运行分析

```bash
python main.py
```

### 3. 命令行选项

```bash
python main.py --stats-only    # 仅显示统计摘要，不生成详细报告
python main.py --verbose       # 显示详细处理信息
python main.py --version       # 显示版本信息
python main.py --help          # 显示帮助信息
```

### 4. 查看报告

分析完成后，报告将输出到 `./log_analysis_output/` 目录：
- `log_summary.txt` - ASCII 可视化文本报告
- `log_summary.json` - 结构化 JSON 数据

## 约束条件

| 约束项 | 说明 |
|--------|------|
| 输入路径 | 必须从 `./log_input/` 读取日志文件 |
| 输出路径 | 必须输出到 `./log_analysis_output/`（自动创建） |
| 输出格式 | 必须同时生成 `log_summary.txt` 和 `log_summary.json` |
| 受保护文件 | `system_base.log` 仅允许读取，禁止修改/删除/重命名 |
| 技术栈 | Python 3.9+，仅使用标准库 |

## 示例输出

### 统计摘要
```
============================================================
统计摘要
============================================================
  总日志条目数: 159
  日志级别种类: 6
  唯一 IP 数量: 20
  错误率: 20.75%
  时间跨度: 16.0 小时
  解析错误: 0 条
============================================================
```

### 错误级别分布
```
CRITICAL │██                                      │      6 (  3.8%)
   ERROR │██████████                              │     27 ( 17.0%)
    WARN │███████                                 │     19 ( 11.9%)
    INFO │████████████████████████████████████████│    102 ( 64.2%)
```

## 技术栈

- **语言**: Python 3.9+
- **依赖**: 仅使用 Python 标准库（无第三方依赖）

## 许可证

MIT License
