import ast
import os
from typing import List, Dict, Any


class ArchitectureViolation:
    """
    架构违规信息
    """
    
    def __init__(self, violation_type: str, file_path: str, line: int, message: str):
        self.violation_type = violation_type
        self.file_path = file_path
        self.line = line
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict[str, Any]: 违规信息字典
        """
        return {
            "type": self.violation_type,
            "file": self.file_path,
            "line": self.line,
            "message": self.message
        }


class ArchitectureChecker(ast.NodeVisitor):
    """
    架构合规性检查器
    使用 AST 分析代码，检测架构违规
    """
    
    def __init__(self, file_path: str):
        """
        初始化检查器
        
        Args:
            file_path: 文件路径
        """
        self.file_path = file_path
        self.violations: List[ArchitectureViolation] = []
        self.imports_from_engines = set()
        self.calls_to_engine_methods = set()
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """
        检查导入语句
        """
        # 检查是否从 engines 导入
        if node.module and node.module.startswith("engines"):
            for alias in node.names:
                self.violations.append(ArchitectureViolation(
                    violation_type="illegal_import",
                    file_path=self.file_path,
                    line=node.lineno,
                    message=f"服务层不能直接导入引擎模块: {alias.name}"
                ))
                self.imports_from_engines.add(alias.name)
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """
        检查函数调用
        """
        if not isinstance(node.func, ast.Attribute):
            self.generic_visit(node)
            return
        
        if node.func.attr not in ["handle_request", "_handle_request_impl"]:
            self.generic_visit(node)
            return
        
        if not isinstance(node.func.value, ast.Name):
            self.generic_visit(node)
            return
        
        var_name = node.func.value.id
        if var_name not in self.imports_from_engines:
            self.generic_visit(node)
            return
        
        self.violations.append(ArchitectureViolation(
            violation_type="illegal_call",
            file_path=self.file_path,
            line=node.lineno,
            message=f"服务层不能直接调用引擎方法: {var_name}.{node.func.attr}"
        ))
        self.calls_to_engine_methods.add((var_name, node.func.attr))
        self.generic_visit(node)
    
    def get_violations(self) -> List[ArchitectureViolation]:
        """
        获取所有违规信息
        
        Returns:
            List[ArchitectureViolation]: 违规信息列表
        """
        return self.violations


def check_architecture(project_root: str) -> List[ArchitectureViolation]:
    """
    检查整个项目的架构合规性
    
    Args:
        project_root: 项目根目录
        
    Returns:
        List[ArchitectureViolation]: 所有违规信息
    """
    services_dir = os.path.join(project_root, "services")
    if not os.path.exists(services_dir):
        return []
    
    violations = []
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            
            if file == "__init__.py" or "test" in file:
                continue
            
            file_path = os.path.join(root, file)
            violations.extend(_check_file_architecture(file_path))
    
    return violations


def _check_file_architecture(file_path: str) -> List[ArchitectureViolation]:
    """
    检查单个文件的架构合规性
    
    Args:
        file_path: 文件路径
        
    Returns:
        List[ArchitectureViolation]: 违规信息列表
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
            checker = ArchitectureChecker(file_path)
            checker.visit(tree)
            return checker.get_violations()
    except Exception as e:
        return [ArchitectureViolation(
            violation_type="parse_error",
            file_path=file_path,
            line=0,
            message=f"解析文件失败: {str(e)}"
        )]


def print_violations(violations: List[ArchitectureViolation]) -> None:
    """
    打印违规信息
    
    Args:
        violations: 违规信息列表
    """
    if not violations:
        print("✅ 架构合规性检查通过")
        return
    
    print("❌ 发现架构违规：")
    
    # 按类型分组
    violations_by_type = {}
    for v in violations:
        if v.violation_type not in violations_by_type:
            violations_by_type[v.violation_type] = []
        violations_by_type[v.violation_type].append(v)
    
    for v_type, v_list in violations_by_type.items():
        print(f"\n  {v_type.upper()}:")
        for v in v_list:
            print(f"    {v.file_path}:{v.line} - {v.message}")


def main():
    """
    主函数
    """
    import sys
    
    # 获取项目根目录
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # 默认使用当前目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"检查项目架构: {project_root}")
    
    # 检查架构
    violations = check_architecture(project_root)
    
    # 打印结果
    print_violations(violations)
    
    # 返回退出码
    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()