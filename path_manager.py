"""
路径管理模块
负责输入输出路径的校验、创建和拼接
"""
import os
import stat
from pathlib import Path


class PathManager:
    """管理日志分析工具的输入输出路径"""

    INPUT_DIR = "./log_input/"
    OUTPUT_DIR = "./log_analysis_output/"
    PROTECTED_FILE = "system_base.log"

    def __init__(self):
        self.input_path = Path(self.INPUT_DIR).resolve()
        self.output_path = Path(self.OUTPUT_DIR).resolve()
        self.protected_file_path = self.input_path / self.PROTECTED_FILE

    def ensure_output_dir(self):
        """确保输出目录存在，不存在则自动创建"""
        if not self.output_path.exists():
            self.output_path.mkdir(parents=True, exist_ok=True)
            print(f"创建输出目录: {self.output_path}")
        return self.output_path

    def validate_input_dir(self):
        """验证输入目录是否存在"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"输入目录不存在: {self.input_path}")
        if not self.input_path.is_dir():
            raise NotADirectoryError(f"输入路径不是目录: {self.input_path}")
        return True

    def check_protected_file_readonly(self):
        """
        检查受保护文件 system_base.log 是否为只读
        该文件仅允许读取，禁止任何修改、删除、重命名操作
        """
        if not self.protected_file_path.exists():
            print(f"警告: 受保护文件 {self.PROTECTED_FILE} 不存在")
            return False

        # 获取文件状态
        file_stat = self.protected_file_path.stat()
        file_mode = stat.filemode(file_stat.st_mode)

        # 检查文件是否可写（如果不是只读，则发出警告）
        is_writable = os.access(self.protected_file_path, os.W_OK)

        if is_writable:
            print(f"警告: 受保护文件 {self.PROTECTED_FILE} 当前可写，建议设置为只读")
        else:
            print(f"受保护文件 {self.PROTECTED_FILE} 已设置为只读，符合安全要求")

        return not is_writable

    def get_input_files(self):
        """获取输入目录下所有支持的日志文件"""
        self.validate_input_dir()

        log_files = []
        for ext in ["*.log", "*.jsonl"]:
            log_files.extend(self.input_path.glob(ext))

        return sorted(log_files)

    def get_output_txt_path(self):
        """获取文本报告输出路径"""
        self.ensure_output_dir()
        return self.output_path / "log_summary.txt"

    def get_output_json_path(self):
        """获取JSON报告输出路径"""
        self.ensure_output_dir()
        return self.output_path / "log_summary.json"

    def is_protected_file(self, file_path):
        """检查指定路径是否为受保护文件"""
        resolved_path = Path(file_path).resolve()
        return resolved_path == self.protected_file_path.resolve()

    def validate_safe_operation(self, file_path, operation="write"):
        """
        验证对文件的操作是否安全
        禁止对受保护文件进行写、删除、重命名等操作
        """
        if self.is_protected_file(file_path):
            if operation in ["write", "delete", "rename", "modify"]:
                raise PermissionError(
                    f"禁止对受保护文件 {self.PROTECTED_FILE} 执行 {operation} 操作"
                )
        return True
