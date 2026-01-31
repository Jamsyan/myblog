"""
启动诊断工具
用于检测和解决间歇性启动失败问题
"""
import os
import sys
import socket
import subprocess
import time
from pathlib import Path

class StartupDiagnostics:
    """
    启动诊断类，用于检测系统状态和潜在问题
    """
    
    def __init__(self, base_path: str):
        """
        初始化诊断工具
        
        Args:
            base_path: 项目根目录路径
        """
        self.base_path = base_path
        self.port = 8000
        self.host = "0.0.0.0"
        self.issues = []
        self.warnings = []
        self.info = []
    
    def check_port_availability(self) -> bool:
        """
        检查端口是否可用
        
        Returns:
            bool: 端口可用返回True，否则返回False
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.host, self.port))
                if result == 0:
                    self.issues.append(f"端口 {self.port} 被占用")
                    return False
                else:
                    self.info.append(f"端口 {self.port} 可用")
                    return True
        except Exception as e:
            self.warnings.append(f"端口检查失败: {str(e)}")
            return True
    
    def check_database_locks(self) -> dict:
        """
        检查数据库文件锁定状态
        
        Returns:
            dict: 数据库状态信息
        """
        db_status = {}
        
        # 检查LinkGateway数据库
        lg_db_path = os.path.join(self.base_path, "data", "linkgateway", "linkgateway.db")
        db_status["linkgateway"] = self._check_db_file(lg_db_path, "LinkGateway")
        
        # 检查引擎数据库
        engines_dir = os.path.join(self.base_path, "data", "engine")
        if os.path.exists(engines_dir):
            for engine_name in os.listdir(engines_dir):
                engine_db_path = os.path.join(engines_dir, engine_name, f"{engine_name}.db")
                db_status[engine_name] = self._check_db_file(engine_db_path, f"引擎 {engine_name}")
        
        return db_status
    
    def _check_db_file(self, db_path: str, name: str) -> dict:
        """
        检查单个数据库文件状态
        
        Args:
            db_path: 数据库文件路径
            name: 数据库名称
            
        Returns:
            dict: 数据库状态
        """
        status = {
            "name": name,
            "path": db_path,
            "exists": os.path.exists(db_path),
            "locked": False,
            "size": 0
        }
        
        if not status["exists"]:
            self.warnings.append(f"{name} 数据库文件不存在: {db_path}")
            return status
        
        # 检查文件大小
        status["size"] = os.path.getsize(db_path)
        
        # 检查是否有锁文件（SQLite通常使用 -wal 和 -shm 文件）
        wal_path = f"{db_path}-wal"
        shm_path = f"{db_path}-shm"
        
        if os.path.exists(wal_path):
            self.issues.append(f"{name} 数据库WAL文件存在，可能被锁定: {wal_path}")
            status["locked"] = True
        
        if os.path.exists(shm_path):
            self.issues.append(f"{name} 数据库SHM文件存在，可能被锁定: {shm_path}")
            status["locked"] = True
        
        # 尝试打开数据库文件（只读）检查是否可访问
        try:
            with open(db_path, 'rb') as f:
                f.read(10)
            self.info.append(f"{name} 数据库文件可访问")
        except PermissionError:
            self.issues.append(f"{name} 数据库文件被锁定（权限错误）: {db_path}")
            status["locked"] = True
        except Exception as e:
            self.warnings.append(f"{name} 数据库文件检查失败: {str(e)}")
        
        return status
    
    def check_zombie_processes(self) -> list:
        """
        检查僵尸进程（Python进程）
        
        Returns:
            list: 僵尸进程信息列表
        """
        try:
            if sys.platform == "win32":
                return self._check_windows_processes()
            else:
                return self._check_unix_processes()
        except subprocess.TimeoutExpired:
            self.warnings.append("进程检查超时")
            return []
        except Exception as e:
            self.warnings.append(f"进程检查失败: {str(e)}")
            return []
    
    def _check_windows_processes(self) -> list:
        """
        检查Windows进程
        
        Returns:
            list: 进程信息列表
        """
        zombie_processes = []
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines[1:]:
                if line.strip():
                    process_info = self._parse_windows_process_line(line)
                    if process_info:
                        zombie_processes.append(process_info)
                        self.issues.append(f"发现Python进程（PID: {process_info['pid']}），可能是僵尸进程")
        
        if not zombie_processes:
            self.info.append("未发现僵尸Python进程")
        
        return zombie_processes
    
    def _parse_windows_process_line(self, line: str) -> dict:
        """
        解析Windows进程行
        
        Args:
            line: 进程行
            
        Returns:
            dict: 进程信息
        """
        parts = line.split(',')
        if len(parts) >= 2:
            return {
                "pid": parts[1].strip('"'),
                "name": parts[0].strip('"'),
                "command": "python.exe"
            }
        return None
    
    def _check_unix_processes(self) -> list:
        """
        检查Unix进程
        
        Returns:
            list: 进程信息列表
        """
        zombie_processes = []
        result = subprocess.run(
            ["ps", "aux", "|", "grep", "python"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines[1:]:
                if "python" in line.lower():
                    process_info = self._parse_unix_process_line(line)
                    if process_info:
                        zombie_processes.append(process_info)
                        self.warnings.append(f"发现Python进程（PID: {process_info['pid']}）")
        
        if not zombie_processes:
            self.info.append("未发现僵尸Python进程")
        
        return zombie_processes
    
    def _parse_unix_process_line(self, line: str) -> dict:
        """
        解析Unix进程行
        
        Args:
            line: 进程行
            
        Returns:
            dict: 进程信息
        """
        parts = line.split()
        if len(parts) >= 2:
            return {
                "pid": parts[1],
                "name": parts[10] if len(parts) > 10 else "python",
                "command": ' '.join(parts[10:]) if len(parts) > 10 else "python"
            }
        return None
    
    def check_log_files(self) -> dict:
        """
        检查日志文件状态
        
        Returns:
            dict: 日志文件状态
        """
        log_status = {}
        log_dir = os.path.join(self.base_path, "log", "linkgateway")
        
        if not os.path.exists(log_dir):
            return log_status
        
        for log_file in os.listdir(log_dir):
            log_path = os.path.join(log_dir, log_file)
            log_status[log_file] = self._check_single_log_file(log_path, log_file)
        
        return log_status
    
    def _check_single_log_file(self, log_path: str, log_file: str) -> dict:
        """
        检查单个日志文件
        
        Args:
            log_path: 日志文件路径
            log_file: 日志文件名
            
        Returns:
            dict: 日志文件状态
        """
        try:
            size = os.path.getsize(log_path)
            mtime = os.path.getmtime(log_path)
            
            if size > 100 * 1024 * 1024:
                self.warnings.append(f"日志文件过大: {log_file} ({size/1024/1024:.2f} MB)")
            
            return {
                "path": log_path,
                "size": size,
                "modified_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
            }
        except Exception as e:
            self.warnings.append(f"日志文件检查失败 {log_file}: {str(e)}")
            return {
                "path": log_path,
                "error": str(e)
            }
    
    def check_temp_files(self) -> list:
        """
        检查临时文件和锁文件
        
        Returns:
            list: 临时文件列表
        """
        temp_files = []
        patterns = ["*.lock", "*.tmp", "*.temp", "*.bak"]
        
        for root, dirs, files in os.walk(self.base_path):
            for pattern in patterns:
                temp_files.extend(self._find_temp_files_in_dir(root, pattern))
        
        return temp_files
    
    def _find_temp_files_in_dir(self, root: str, pattern: str) -> list:
        """
        在指定目录查找临时文件
        
        Args:
            root: 目录路径
            pattern: 文件模式
            
        Returns:
            list: 临时文件列表
        """
        import glob
        temp_files = []
        
        for file in glob.glob(os.path.join(root, pattern)):
            temp_files.append(file)
            self.warnings.append(f"发现临时文件: {file}")
        
        return temp_files
    
    def run_full_diagnostics(self) -> dict:
        """
        运行完整的诊断检查
        
        Returns:
            dict: 诊断结果
        """
        print("=" * 60)
        print("启动诊断工具")
        print("=" * 60)
        print()
        
        # 1. 检查端口
        print("[1/6] 检查端口可用性...")
        port_available = self.check_port_availability()
        print()
        
        # 2. 检查数据库锁定
        print("[2/6] 检查数据库文件锁定...")
        db_status = self.check_database_locks()
        print()
        
        # 3. 检查僵尸进程
        print("[3/6] 检查僵尸进程...")
        zombie_processes = self.check_zombie_processes()
        print()
        
        # 4. 检查日志文件
        print("[4/6] 检查日志文件状态...")
        log_status = self.check_log_files()
        print()
        
        # 5. 检查临时文件
        print("[5/6] 检查临时文件...")
        temp_files = self.check_temp_files()
        print()
        
        # 6. 生成诊断报告
        print("[6/6] 生成诊断报告...")
        print()
        
        return {
            "port_available": port_available,
            "port": self.port,
            "database_status": db_status,
            "zombie_processes": zombie_processes,
            "log_status": log_status,
            "temp_files": temp_files,
            "issues": self.issues,
            "warnings": self.warnings,
            "info": self.info
        }
    
    def print_report(self, diagnostics: dict):
        """
        打印诊断报告
        
        Args:
            diagnostics: 诊断结果字典
        """
        print("=" * 60)
        print("诊断报告")
        print("=" * 60)
        print()
        
        # 打印问题
        if diagnostics["issues"]:
            print("🔴 发现的问题：")
            for issue in diagnostics["issues"]:
                print(f"  ✗ {issue}")
            print()
        else:
            print("✓ 未发现严重问题")
            print()
        
        # 打印警告
        if diagnostics["warnings"]:
            print("🟡 警告信息：")
            for warning in diagnostics["warnings"]:
                print(f"  ⚠ {warning}")
            print()
        else:
            print("✓ 无警告")
            print()
        
        # 打印信息
        if diagnostics["info"]:
            print("ℹ️ 诊断信息：")
            for info in diagnostics["info"]:
                print(f"  ℹ {info}")
            print()
        
        # 打印建议
        print("=" * 60)
        print("修复建议：")
        print("=" * 60)
        print()
        
        if not diagnostics["port_available"]:
            print("1. 端口占用问题：")
            print(f"   - 检查并结束占用端口 {diagnostics['port']} 的进程")
            print(f"   - Windows: taskkill /F /PID <进程ID>")
            print(f"   - Linux/Mac: kill -9 <进程ID>")
            print()
        
        locked_dbs = [name for name, status in diagnostics["database_status"].items() if status.get("locked", False)]
        if locked_dbs:
            print("2. 数据库锁定问题：")
            for db_name in locked_dbs:
                print(f"   - 删除数据库锁文件: {db_name}")
                print(f"   - 重启计算机以释放文件锁")
            print()
        
        if diagnostics["zombie_processes"]:
            print("3. 僵尸进程问题：")
            print("   - 手动结束僵尸Python进程")
            print(f"   - Windows: taskkill /F /PID <进程ID>")
            print(f"   - Linux/Mac: kill -9 <进程ID>")
            print()
        
        if diagnostics["temp_files"]:
            print("4. 临时文件问题：")
            print("   - 清理临时文件和锁文件")
            print("   - 删除 *.lock, *.tmp, *.temp, *.bak 文件")
            print()
        
        if not diagnostics["issues"] and not diagnostics["warnings"]:
            print("✓ 系统状态良好，可以正常启动")
            print()
        
        print("=" * 60)


def main():
    """
    主函数
    """
    # 获取项目根目录
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 创建诊断工具
    diagnostics = StartupDiagnostics(base_path)
    
    # 运行诊断
    result = diagnostics.run_full_diagnostics()
    
    # 打印报告
    diagnostics.print_report(result)
    
    # 返回退出码（有问题返回1，否则返回0）
    if result["issues"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
