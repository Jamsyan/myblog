import os
import json
import importlib.util
from typing import Dict, Any, List, Optional
from pathlib import Path
from BaseEngine.base import BaseEngine
from .db import init_db, ServiceType, ServiceStatus, EngineType
from .path_manager import PathManager
from .standards import ServiceStandard, EngineStandard
from .logs import get_logger

class ServiceRegistry:
    """
    服务注册与发现类，负责管理业务和引擎的注册与发现
    """
    
    def __init__(self, base_path: str):
        """
        初始化服务注册中心
        
        Args:
            base_path: 项目根目录路径
        """
        self.base_path = base_path
        self.engines: Dict[str, BaseEngine] = {}
        self.businesses: Dict[str, Dict[str, Any]] = {}
        self.services: Dict[str, Any] = {}
        
        self.registered_engines = []
        self.registered_businesses = []
        
        self._initialize_path_manager(base_path)
        self._initialize_logger()
        self._initialize_directories(base_path)
        self._initialize_database()
    
    def _initialize_path_manager(self, base_path: str) -> None:
        """
        初始化路径管理器
        
        Args:
            base_path: 项目根目录路径
        """
        self.path_manager = PathManager(base_path)
    
    def _initialize_logger(self) -> None:
        """
        初始化日志
        """
        log_path = self.path_manager.get_linkgateway_log_path()
        self.logger = get_logger("ServiceRegistry", log_path)
    
    def _initialize_directories(self, base_path: str) -> None:
        """
        初始化目录路径
        
        Args:
            base_path: 项目根目录路径
        """
        self.services_dir = os.path.join(base_path, "services")
        self.engines_dir = os.path.join(base_path, "engines")
    
    def _initialize_database(self) -> None:
        """
        初始化数据库
        """
        self.db_path = self.path_manager.get_linkgateway_db_path()
        
        if not self._init_database_manager():
            self.db_manager = None
            self.logger.log_progress("服务注册中心以内存模式初始化，部分功能可能受限")
            return
        
        self._load_services_from_database()
        self.logger.log("INFO", "服务注册中心初始化成功", True)
    
    def _init_database_manager(self) -> bool:
        """
        初始化数据库管理器
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        try:
            self.db_manager = init_db(self.db_path)
            return True
        except Exception as e:
            self.logger.log("ERROR", f"数据库初始化: {str(e)}", False)
            return False
    
    def _load_services_from_database(self) -> None:
        """
        从数据库加载服务信息
        """
        try:
            self._load_services_from_db()
        except Exception as e:
            self.logger.log("ERROR", f"从数据库加载服务信息: {str(e)}", False)
            self.services.clear()
            self.businesses.clear()
            self.engines.clear()
            self.logger.log_progress("服务注册中心初始化完成，但未加载到服务信息")
    
    def _load_services_from_db(self) -> None:
        """
        从数据库加载服务信息
        """
        self.services.clear()
        self.businesses.clear()
        self.engines.clear()
        
        if not self.db_manager:
            self.logger.log("WARNING", "数据库管理器未初始化，无法从数据库加载服务信息")
            return
        
        try:
            db_services = self.db_manager.list_services()
            
            if not isinstance(db_services, list):
                self.logger.log("ERROR", "数据库返回的服务列表格式错误", False)
                return
            
            for db_service in db_services:
                self._process_db_service(db_service)
        except Exception as e:
            self.logger.log("ERROR", f"从数据库加载服务信息失败: {str(e)}", False)
            self.services.clear()
            self.businesses.clear()
            self.engines.clear()
    
    def _process_db_service(self, db_service: Any) -> None:
        """
        处理单个数据库服务
        
        Args:
            db_service: 数据库服务对象
        """
        try:
            service_id = getattr(db_service, 'service_id', None)
            if not service_id:
                self.logger.log("WARNING", "跳过缺少service_id的服务", None)
                return
            
            service_type = getattr(db_service, 'service_type', None)
            if not service_type:
                self.logger.log("WARNING", f"服务 {service_id} 缺少服务类型", None)
                return
            
            service_type_value = service_type.value if hasattr(service_type, 'value') else str(service_type)
            
            if service_type_value == "business":
                self._process_business_service(db_service, service_id)
            elif service_type_value == "engine":
                self._process_engine_service(db_service, service_id)
        except Exception as e:
            self.logger.log("ERROR", f"处理服务 {getattr(db_service, 'service_id', 'unknown')} 时出错: {str(e)}", False)
    
    def _process_business_service(self, db_service: Any, service_id: str) -> None:
        """
        处理业务服务
        
        Args:
            db_service: 数据库服务对象
            service_id: 服务ID
        """
        service_info = {
            "service_id": service_id,
            "service_name": getattr(db_service, 'service_name', service_id),
            "version": getattr(db_service, 'version', "1.0.0"),
            "status": getattr(db_service, 'status', None).value if getattr(db_service, 'status', None) else "unknown",
            "reason": getattr(db_service, 'reason', None),
            "description": getattr(db_service, 'description', "")
        }
        
        business_info = service_info.copy()
        
        if getattr(db_service, 'database_config', None):
            try:
                business_info["database"] = json.loads(db_service.database_config)
            except json.JSONDecodeError as e:
                self.logger.log("ERROR", f"解析服务 {service_id} 的数据库配置失败: {str(e)}", False)
                business_info["database"] = {}
        
        if getattr(db_service, 'api_config', None):
            try:
                business_info["apis"] = json.loads(db_service.api_config)
            except json.JSONDecodeError as e:
                self.logger.log("ERROR", f"解析服务 {service_id} 的API配置失败: {str(e)}", False)
                business_info["apis"] = []
        
        business_info["business_path"] = getattr(db_service, 'business_path', "")
        
        self.businesses[service_id] = business_info
        self.services[service_id] = {
            "type": "business",
            "info": business_info
        }
    
    def _process_engine_service(self, db_service: Any, service_id: str) -> None:
        """
        处理引擎服务
        
        Args:
            db_service: 数据库服务对象
            service_id: 服务ID
        """
        service_info = {
            "service_id": service_id,
            "service_name": getattr(db_service, 'service_name', service_id),
            "version": getattr(db_service, 'version', "1.0.0"),
            "status": getattr(db_service, 'status', None).value if getattr(db_service, 'status', None) else "unknown",
            "reason": getattr(db_service, 'reason', None),
            "description": getattr(db_service, 'description', "")
        }
        
        engine_info = service_info.copy()
        engine_type = getattr(db_service, 'engine_type', None)
        engine_info["engine_type"] = engine_type.value if engine_type else None
        
        self.services[service_id] = {
            "type": "engine",
            "info": engine_info
        }
    
    def _find_config_file(self, directory: str, service_name: str, file_patterns: list) -> str:
        """
        查找配置文件
        
        Args:
            directory: 目录路径
            service_name: 服务名称
            file_patterns: 文件模式列表
            
        Returns:
            str: 配置文件路径，未找到返回None
        """
        for pattern in file_patterns:
            candidate_path = os.path.join(directory, pattern.format(name=service_name))
            if os.path.exists(candidate_path):
                self.logger.debug(f"找到配置文件：{candidate_path}")
                return candidate_path
        
        # 最后尝试查找任何.json文件
        for file in os.listdir(directory):
            if file.endswith(".json"):
                candidate_path = os.path.join(directory, file)
                self.logger.debug(f"找到配置文件：{candidate_path}（通用JSON文件）")
                return candidate_path
        
        return None
    
    def _find_engine_file(self, directory: str, engine_name: str) -> str:
        """
        查找引擎实现文件
        
        Args:
            directory: 目录路径
            engine_name: 引擎名称
            
        Returns:
            str: 引擎实现文件路径，未找到返回None
        """
        # 首先尝试查找与引擎名称同名的.py文件
        expected_engine_file = os.path.join(directory, f"{engine_name}.py")
        if os.path.exists(expected_engine_file):
            self.logger.debug(f"找到引擎实现文件：{expected_engine_file}（与引擎名称同名）")
            return expected_engine_file
        
        # 查找包含引擎类定义的文件
        for file in os.listdir(directory):
            if not file.endswith(".py") or file.startswith("_"):
                continue
            
            # 跳过可能是路由或配置文件的文件
            if "route" in file.lower() or "config" in file.lower() or "test" in file.lower():
                self.logger.debug(f"跳过非引擎实现文件：{file}")
                continue
            
            file_path = os.path.join(directory, file)
            if self._is_engine_file(file_path):
                return file_path
        
        return None
    
    def _is_engine_file(self, file_path: str) -> bool:
        """
        检查文件是否是引擎实现文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是引擎文件返回True，否则返回False
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 简单检查是否包含引擎类定义
                if "class " in content and "BaseEngine" in content:
                    self.logger.debug(f"找到引擎实现文件：{file_path}（包含引擎类定义）")
                    return True
        except Exception as e:
            self.logger.log("ERROR", f"检查引擎文件失败: {file_path}, 错误: {str(e)}", False)
        
        return False
    
    def discover_services(self) -> Dict[str, Any]:
        """
        发现所有服务（业务和引擎）
        
        Returns:
            Dict[str, Any]: 发现结果，包含业务和引擎的信息
        """
        # 清空当前服务信息，避免重复计数
        self.services.clear()
        self.businesses.clear()
        self.engines.clear()
        
        # 清空注册信息收集结构
        self.registered_engines.clear()
        self.registered_businesses.clear()
        
        self.logger.info("开始服务发现...")
        
        # 发现业务
        business_result = []
        try:
            self.logger.debug("正在发现业务服务...")
            business_result = self.discover_businesses()
            if not isinstance(business_result, list):
                self.logger.error("业务服务发现结果格式错误")
                business_result = []
        except Exception as e:
            self.logger.log("ERROR", f"发现业务服务失败: {str(e)}", False)
            business_result = []
        
        engine_result = []
        try:
            self.logger.log_progress("发现引擎服务")
            engine_result = self.discover_engines()
            if not isinstance(engine_result, list):
                self.logger.log("ERROR", "引擎服务发现结果格式错误", False)
                engine_result = []
        except Exception as e:
            self.logger.log("ERROR", f"发现引擎服务失败: {str(e)}", False)
            engine_result = []
        
        # 统计结果
        business_count = len(business_result)
        engine_count = len(engine_result)
        total_services = len(self.services)
        
        # 统计成功和失败的服务数量
        valid_businesses = sum(1 for b in business_result if isinstance(b, dict) and b.get("status") == "valid")
        invalid_businesses = business_count - valid_businesses
        
        valid_engines = sum(1 for e in engine_result if isinstance(e, dict) and e.get("status") == "valid")
        invalid_engines = engine_count - valid_engines
        
        # 统一输出服务发现汇总信息
        self.logger.info(f"服务发现完成：共发现 {total_services} 个服务")
        self.logger.info(f"  - 业务服务：{business_count} 个（有效: {valid_businesses}, 无效: {invalid_businesses}")
        self.logger.info(f"  - 引擎服务：{engine_count} 个（有效: {valid_engines}, 无效: {invalid_engines}")
        
        # 输出注册成功的业务服务详情
        if self.registered_businesses:
            self.logger.log_progress("  - 注册成功的业务服务：")
            for business_info in self.registered_businesses:
                service_id = business_info.get('service_id')
                service_name = business_info.get('service_name', service_id)
                self.logger.log("INFO", f"    - 服务{service_name} 注册成功 服务ID：{service_id}", True)
        
        if self.registered_engines:
            self.logger.log_progress("  - 注册成功的引擎服务：")
            for engine_info in self.registered_engines:
                service_id = engine_info.get('service_id')
                service_name = engine_info.get('service_name', service_id)
                self.logger.log("INFO", f"    - 引擎{service_name} 注册成功 服务ID：{service_id}", True)
        
        return {
            "businesses": business_result,
            "engines": engine_result,
            "total_services": total_services,
            "summary": {
                "businesses": {
                    "total": business_count,
                    "valid": valid_businesses,
                    "invalid": invalid_businesses
                },
                "engines": {
                    "total": engine_count,
                    "valid": valid_engines,
                    "invalid": invalid_engines
                }
            }
        }
    
    def discover_businesses(self) -> List[Dict[str, Any]]:
        """
        发现所有业务服务
        
        Returns:
            List[Dict[str, Any]]: 业务列表，包含业务信息和状态
        """
        result = []
        
        # 确保服务目录存在
        if not os.path.exists(self.services_dir):
            self.logger.debug(f"业务服务目录不存在：{self.services_dir}")
            return result
        
        self.logger.debug(f"开始扫描业务服务目录：{self.services_dir}")
        
        # 递归扫描服务目录下的所有文件夹
        for root, dirs, files in os.walk(self.services_dir):
            # 只在DEBUG级别下输出扫描目录信息，正常运行时不输出
            self.logger.debug(f"扫描目录：{root}")
            
            # 检查当前目录下是否有 service.json 文件
            service_json_path = os.path.join(root, "service.json")
            if os.path.exists(service_json_path):
                # 处理业务服务，使用文件夹名称作为业务名称
                business_name = os.path.basename(root)
                business_path = root
                
                business_info = self._process_business(business_name, business_path)
                result.append(business_info)
        
        return result
    
    def _process_business(self, business_name: str, business_path: str) -> Dict[str, Any]:
        """
        处理单个业务
        
        Args:
            business_name: 业务名称
            business_path: 业务路径
            
        Returns:
            Dict[str, Any]: 业务处理结果
        """
        self.logger.debug(f"正在处理业务服务：{business_name}，路径：{business_path}")
        
        # 检查是否存在 service.json 文件
        service_json_path = self.path_manager.get_service_json_path(business_path)
        if not os.path.exists(service_json_path):
            self.logger.error(f"业务服务 {business_name} 缺少 service.json 文件")
            # 保存到数据库
            self.db_manager.update_service_status(
                business_name,
                ServiceStatus.INVALID,
                "Missing service.json file"
            )
            return {
                "service_id": business_name,
                "service_name": business_name,
                "status": "invalid",
                "reason": "Missing service.json file"
            }
        
        try:
            # 解析 service.json 文件
            with open(service_json_path, "r", encoding="utf-8") as f:
                service_info = json.load(f)
            self.logger.debug(f"成功解析业务服务 {business_name} 的 service.json 文件")
            
            # 使用服务标准验证配置文件
            validation_result = ServiceStandard.validate_service_json(service_info)
            if not validation_result["valid"]:
                service_id = service_info.get("service_id", business_name)
                self.logger.log("ERROR", f"业务服务 {service_id} 的配置验证失败: {validation_result['reason']}", False)
                # 保存到数据库
                self.db_manager.update_service_status(
                    service_id,
                    ServiceStatus.INVALID,
                    validation_result["reason"]
                )
                return {
                    "service_id": service_id,
                    "service_name": service_info.get("service_name", service_id),
                    "status": "invalid",
                    "reason": validation_result["reason"]
                }
            
            self.logger.debug(f"业务服务 {service_info.get('service_id', business_name)} 的配置验证成功")
            
            # 检查业务是否提供数据库连接信息
            if "database" not in service_info or not service_info["database"]:
                service_id = service_info["service_id"]
                self.logger.log("ERROR", f"业务服务 {service_id} 缺少数据库配置", False)
                # 保存到数据库
                self.db_manager.update_service_status(
                    service_id,
                    ServiceStatus.INVALID,
                    "Missing database configuration"
                )
                return {
                    "service_id": service_id,
                    "service_name": service_info["service_name"],
                    "version": service_info["version"],
                    "status": "invalid",
                    "reason": "Missing database configuration"
                }
            
            # 获取数据库配置
            db_config = service_info["database"]
            
            # 注册业务
            business_info = {
                "service_id": service_info["service_id"],
                "service_name": service_info["service_name"],
                "version": service_info["version"],
                "description": service_info.get("description", ""),
                "database": db_config,
                "apis": service_info.get("apis", []),
                "status": "valid",
                "business_path": business_path
            }
            
            service_id = service_info["service_id"]
            
            # 添加到业务注册表
            self.businesses[service_id] = business_info
            self.services[service_id] = {
                "type": "business",
                "info": business_info
            }
            
            # 保存到数据库
            db_service_info = {
                "service_id": service_id,
                "service_name": service_info["service_name"],
                "service_type": ServiceType.BUSINESS,
                "version": service_info["version"],
                "status": ServiceStatus.VALID,
                "description": service_info.get("description", ""),
                "database_config": json.dumps(db_config),
                "api_config": json.dumps(service_info.get("apis", [])),
                "business_path": business_path
            }
            
            if self.db_manager.service_exists(service_id):
                self.db_manager.update_service(service_id, db_service_info)
                self.logger.debug(f"已更新业务服务 {service_id} 到数据库")
            else:
                self.db_manager.add_service(db_service_info)
                self.logger.debug(f"已注册业务服务 {service_id} 到数据库")
            
            # 将注册成功的业务服务信息添加到收集结构
            self.registered_businesses.append(business_info)
            
            self.logger.debug(f"业务服务 {service_id} 处理完成，状态: 有效")
            return business_info
        except json.JSONDecodeError as e:
            self.logger.log("ERROR", f"业务服务 {business_name} 的 service.json 文件格式无效: {str(e)}", False)
            # 保存到数据库
            self.db_manager.update_service_status(
                business_name,
                ServiceStatus.INVALID,
                f"Invalid service.json format: {str(e)}"
            )
            return {
                "service_id": business_name,
                "service_name": business_name,
                "status": "invalid",
                "reason": f"Invalid service.json format: {str(e)}"
            }
        except Exception as e:
            self.logger.log("ERROR", f"处理业务服务 {business_name} 失败: {str(e)}", False)
            # 保存到数据库
            self.db_manager.update_service_status(
                business_name,
                ServiceStatus.INVALID,
                f"Error processing business: {str(e)}"
            )
            return {
                "service_id": business_name,
                "service_name": business_name,
                "status": "invalid",
                "reason": f"Error processing business: {str(e)}"
            }
    
    def discover_engines(self) -> List[Dict[str, Any]]:
        """
        发现所有引擎
        
        Returns:
            List[Dict[str, Any]]: 引擎列表，包含引擎信息和状态
        """
        result = []
        
        # 确保引擎目录存在
        if not os.path.exists(self.engines_dir):
            self.logger.debug(f"引擎目录不存在：{self.engines_dir}")
            return result
        
        self.logger.debug(f"开始扫描引擎目录：{self.engines_dir}")
        
        # 递归扫描引擎目录下的所有文件夹
        for root, dirs, files in os.walk(self.engines_dir):
            self.logger.debug(f"扫描目录：{root}")
            
            engine_name = os.path.basename(root)
            
            # 查找引擎配置文件
            engine_json_path = self._find_config_file(root, engine_name, ["{name}.json", "engine.json"])
            
            if engine_json_path:
                # 查找引擎实现文件
                engine_file = self._find_engine_file(root, engine_name)
                
                if engine_file:
                    engine_info = self._process_engine(engine_name, engine_file)
                    result.append(engine_info)
                else:
                    self.logger.debug(f"在目录 {root} 中未找到有效的引擎实现文件")
        
        return result
    
    def _process_engine(self, engine_name: str, engine_path: str) -> Dict[str, Any]:
        """
        处理单个引擎
        
        Args:
            engine_name: 引擎名称（文件夹名称）
            engine_path: 引擎路径
            
        Returns:
            Dict[str, Any]: 引擎处理结果
        """
        self.logger.debug(f"正在处理引擎服务：{engine_name}，路径：{engine_path}")
        
        engine_dir = self._get_engine_dir(engine_path)
        engine_json_path = self._find_engine_config_file(engine_dir, engine_name)
        
        if not engine_json_path:
            return self._build_engine_error_result(
                engine_name,
                engine_name,
                f"Missing engine configuration file. Searched directory: {engine_dir}"
            )
        
        try:
            engine_config = self._load_and_validate_engine_config(engine_json_path, engine_name)
            if not engine_config:
                return self._build_engine_error_result(
                    engine_name,
                    engine_name,
                    "Unknown error"
                )
            
            engine = self._load_and_create_engine(engine_config, engine_path, engine_name)
            if not engine:
                return self._build_engine_error_result(
                    engine_name,
                    engine_name,
                    "Unknown error"
                )
            
            engine_metadata = self._start_and_register_engine(engine, engine_config, engine_path)
            
            self.logger.debug(f"引擎服务 {engine_metadata['service_id']} 处理完成，状态: {'有效' if engine.status == 'running' else '无效'}")
            return {
                "service_id": engine_metadata["service_id"],
                "service_name": engine_metadata["service_name"],
                "version": engine_metadata["version"],
                "engine_type": engine_metadata["engine_type"],
                "status": "valid"
            }
        except json.JSONDecodeError as e:
            return self._build_engine_error_result(
                engine_name,
                engine_name,
                f"Invalid engine.json format: {str(e)}"
            )
        except Exception as e:
            return self._build_engine_error_result(
                engine_name,
                engine_name,
                f"Error loading engine: {str(e)}"
            )
    
    def _get_engine_dir(self, engine_path: str) -> str:
        """
        获取引擎目录
        
        Args:
            engine_path: 引擎路径
            
        Returns:
            str: 引擎目录
        """
        return os.path.dirname(engine_path) if os.path.isfile(engine_path) else engine_path
    
    def _find_engine_config_file(self, engine_dir: str, engine_name: str) -> Optional[str]:
        """
        查找引擎配置文件
        
        Args:
            engine_dir: 引擎目录
            engine_name: 引擎名称
            
        Returns:
            Optional[str]: 配置文件路径，未找到返回None
        """
        engine_json_path = self._find_config_file(engine_dir, engine_name, ["{name}.json", "engine.json"])
        
        if not engine_json_path:
            self.logger.log("ERROR", f"引擎服务 {engine_name} 缺少配置文件，查找目录：{engine_dir}", False)
            self.db_manager.update_service_status(
                engine_name,
                ServiceStatus.INVALID,
                f"Missing engine configuration file. Searched directory: {engine_dir}"
            )
        
        return engine_json_path
    
    def _load_and_validate_engine_config(self, engine_json_path: str, engine_name: str) -> Optional[Dict[str, Any]]:
        """
        加载并验证引擎配置
        
        Args:
            engine_json_path: 配置文件路径
            engine_name: 引擎名称
            
        Returns:
            Optional[Dict[str, Any]]: 配置信息，验证失败返回None
        """
        engine_config = self.path_manager.load_json_file(engine_json_path)
        self.logger.debug(f"成功加载引擎服务 {engine_name} 的配置文件：{engine_json_path}")
        
        validation_result = EngineStandard.validate_engine_json(engine_config)
        if not validation_result["valid"]:
            service_id = engine_config.get("service_id", engine_name)
            self.logger.log("ERROR", f"引擎服务 {service_id} 的配置验证失败: {validation_result['reason']}", False)
            self.db_manager.update_service_status(
                service_id,
                ServiceStatus.INVALID,
                validation_result["reason"]
            )
            return None
        
        self.logger.debug(f"引擎服务 {engine_config.get('service_id', engine_name)} 的配置验证成功")
        return engine_config
    
    def _load_and_create_engine(self, engine_config: Dict[str, Any], engine_path: str, engine_name: str) -> Optional[BaseEngine]:
        """
        加载并创建引擎实例
        
        Args:
            engine_config: 引擎配置
            engine_path: 引擎路径
            engine_name: 引擎名称
            
        Returns:
            Optional[BaseEngine]: 引擎实例，失败返回None
        """
        service_id = engine_config.get("service_id", engine_name)
        service_name = engine_config.get("service_name", service_id)
        
        self.logger.debug(f"正在创建引擎服务 {service_id} 的实例...")
        
        spec = importlib.util.spec_from_file_location(service_id, engine_path)
        if not spec or not spec.loader:
            self.logger.log("ERROR", f"引擎服务 {service_id} 模块加载失败", False)
            self.db_manager.update_service_status(
                service_id,
                ServiceStatus.INVALID,
                "Failed to load engine module"
            )
            return None
        
        engine_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine_module)
        self.logger.debug(f"成功导入引擎模块：{engine_path}")
        
        engine_class = self._find_engine_class(engine_module, service_id)
        if not engine_class:
            return None
        
        self.logger.debug(f"找到引擎类：{engine_class.__name__}")
        
        engine = self._create_engine_instance(engine_class, service_id, service_name, engine_config)
        self._start_engine_safely(engine, service_id)
        
        return engine
    
    def _find_engine_class(self, engine_module: Any, service_id: str) -> Optional[type]:
        """
        查找引擎类
        
        Args:
            engine_module: 引擎模块
            service_id: 服务ID
            
        Returns:
            Optional[type]: 引擎类，未找到返回None
        """
        for name, cls in engine_module.__dict__.items():
            if isinstance(cls, type) and issubclass(cls, BaseEngine) and cls != BaseEngine:
                return cls
        
        self.logger.log("ERROR", f"引擎服务 {service_id} 中未找到继承自 BaseEngine 的类", False)
        self.db_manager.update_service_status(
            service_id,
            ServiceStatus.INVALID,
            "No class inheriting from BaseEngine found"
        )
        return None
    
    def _create_engine_instance(self, engine_class: type, service_id: str, service_name: str, engine_config: Dict[str, Any]) -> BaseEngine:
        """
        创建引擎实例
        
        Args:
            engine_class: 引擎类
            service_id: 服务ID
            service_name: 服务名称
            engine_config: 引擎配置
            
        Returns:
            BaseEngine: 引擎实例
        """
        self.logger.debug(f"正在初始化引擎实例：{service_id}")
        engine = engine_class(service_id, engine_config["version"])
        engine.service_name = service_name
        engine.engine_type = engine_config["engine_type"]
        return engine
    
    def _start_engine_safely(self, engine: BaseEngine, service_id: str) -> None:
        """
        安全启动引擎
        
        Args:
            engine: 引擎实例
            service_id: 服务ID
        """
        self.logger.debug(f"正在启动引擎：{service_id}")
        try:
            start_result = self._start_engine_with_timeout(engine, service_id, timeout=30)
            if start_result:
                self.logger.info(f"引擎 {service_id} 启动成功")
            else:
                self.logger.error(f"引擎 {service_id} 启动失败")
        except Exception as e:
            self.logger.error(f"引擎 {service_id} 启动过程中发生错误: {str(e)}")
            engine.status = "failed"
    
    def _start_and_register_engine(self, engine: BaseEngine, engine_config: Dict[str, Any], engine_path: str) -> Dict[str, Any]:
        """
        启动并注册引擎
        
        Args:
            engine: 引擎实例
            engine_config: 引擎配置
            engine_path: 引擎路径
            
        Returns:
            Dict[str, Any]: 引擎元数据
        """
        engine_metadata = engine.get_metadata()
        self.logger.debug(f"引擎实例初始化完成，元数据：{engine_metadata}")
        
        self._register_engine_to_memory(engine_metadata, engine)
        self._register_engine_to_db(engine_metadata, engine_config, engine_path)
        
        self.registered_engines.append(engine_metadata)
        return engine_metadata
    
    def _register_engine_to_memory(self, engine_metadata: Dict[str, Any], engine: BaseEngine) -> None:
        """
        注册引擎到内存
        
        Args:
            engine_metadata: 引擎元数据
            engine: 引擎实例
        """
        self.engines[engine_metadata["service_id"]] = engine
        self.services[engine_metadata["service_id"]] = {
            "type": "engine",
            "info": engine_metadata
        }
        self.logger.debug(f"引擎服务 {engine_metadata['service_id']} 已注册到内存注册表")
    
    def _register_engine_to_db(self, engine_metadata: Dict[str, Any], engine_config: Dict[str, Any], engine_path: str) -> None:
        """
        注册引擎到数据库
        
        Args:
            engine_metadata: 引擎元数据
            engine_config: 引擎配置
            engine_path: 引擎路径
        """
        service_status = ServiceStatus.VALID if engine_metadata.get("status") == "running" else ServiceStatus.INVALID
        reason = None if engine_metadata.get("status") == "running" else f"Engine startup failed, current status: {engine_metadata.get('status')}"
        
        db_service_info = {
            "service_id": engine_metadata["service_id"],
            "service_name": engine_metadata["service_name"],
            "service_type": ServiceType.ENGINE,
            "version": engine_metadata["version"],
            "status": service_status,
            "reason": reason,
            "description": engine_config.get("description", ""),
            "engine_type": EngineType(engine_metadata["engine_type"].lower()),
            "engine_path": engine_path
        }
        
        if self.db_manager.service_exists(engine_metadata["service_id"]):
            self.db_manager.update_service(engine_metadata["service_id"], db_service_info)
            self.logger.debug(f"已更新引擎服务 {engine_metadata['service_id']} 到数据库")
        else:
            self.db_manager.add_service(db_service_info)
            self.logger.debug(f"已注册引擎服务 {engine_metadata['service_id']} 到数据库")
    
    def _build_engine_error_result(self, service_id: str, service_name: str, reason: str) -> Dict[str, Any]:
        """
        构建引擎错误结果
        
        Args:
            service_id: 服务ID
            service_name: 服务名称
            reason: 错误原因
            
        Returns:
            Dict[str, Any]: 错误结果
        """
        self.db_manager.update_service_status(
            service_id,
            ServiceStatus.INVALID,
            reason
        )
        return {
            "service_id": service_id,
            "service_name": service_name,
            "status": "invalid",
            "reason": reason
        }
    
    def _start_engine_with_timeout(self, engine: Any, service_id: str, timeout: int = 30) -> bool:
        """
        启动引擎，带超时保护
        
        Args:
            engine: 引擎实例
            service_id: 服务ID
            timeout: 超时时间（秒）
            
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        import threading
        import time
        
        result = {"success": False, "error": None}
        
        def start_engine():
            try:
                result["success"] = engine.start()
            except Exception as e:
                result["error"] = str(e)
        
        # 创建启动线程
        thread = threading.Thread(target=start_engine, daemon=True)
        thread.start()
        
        # 等待线程完成或超时
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            # 超时，引擎启动卡住了
            self.logger.error(f"引擎 {service_id} 启动超时（{timeout}秒），跳过该引擎")
            return False
        
        if result["error"]:
            # 启动过程中出错
            self.logger.log("ERROR", f"引擎 {service_id} 启动失败: {result['error']}", False)
            return False
        
        return result["success"]
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        根据服务ID获取服务信息
        
        Args:
            service_id: 服务ID
            
        Returns:
            Optional[Dict[str, Any]]: 服务信息，未找到返回None
        """
        return self.services.get(service_id)
    
    def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        """
        根据业务ID获取业务信息
        
        Args:
            business_id: 业务ID
            
        Returns:
            Optional[Dict[str, Any]]: 业务信息，未找到返回None
        """
        return self.businesses.get(business_id)
    
    def get_engine(self, engine_id: str) -> Optional[BaseEngine]:
        """
        根据引擎ID获取引擎实例
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            Optional[BaseEngine]: 引擎实例，未找到返回None
        """
        return self.engines.get(engine_id)
    
    def list_services(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有服务
        
        Args:
            service_type: 服务类型，"business"表示业务，"engine"表示引擎，不指定则返回所有类型
            
        Returns:
            List[Dict[str, Any]]: 服务列表，包含完整的服务信息
        """
        result = []
        for service_id, service_info in self.services.items():
            if service_type is None or service_info["type"] == service_type:
                # 从数据库获取完整的服务信息
                db_service = self.db_manager.get_service(service_id)
                
                # 复制原始info，确保包含business_path
                info_copy = service_info["info"].copy()
                
                # 根据服务类型添加特有字段到info中
                if service_info["type"] == "business" and db_service:
                    info_copy["business_path"] = db_service.business_path
                
                # 构建完整的服务信息
                complete_service_info = {
                    "service_id": service_id,
                    "type": service_info["type"],
                    "info": info_copy,
                    "database_info": {
                        "status": db_service.status.value if db_service else "unknown",
                        "reason": db_service.reason if db_service else None,
                        "created_at": db_service.created_at.isoformat() if db_service else None,
                        "updated_at": db_service.updated_at.isoformat() if db_service else None,
                        "last_check_at": db_service.last_check_at.isoformat() if db_service and db_service.last_check_at else None,
                        "version": db_service.version if db_service else None,
                        "description": db_service.description if db_service else None
                    }
                }
                
                # 根据服务类型添加特有字段到database_info中
                if service_info["type"] == "business" and db_service:
                    complete_service_info["database_info"]["business_path"] = db_service.business_path
                elif service_info["type"] == "engine" and db_service:
                    complete_service_info["database_info"]["engine_type"] = db_service.engine_type.value if db_service.engine_type else None
                    complete_service_info["database_info"]["engine_path"] = db_service.engine_path
                
                result.append(complete_service_info)
        
        return result
    
    def register_service(self, service_info: Dict[str, Any]) -> bool:
        """
        手动注册服务
        
        Args:
            service_info: 服务信息
            
        Returns:
            bool: 注册成功返回True，失败返回False
        """
        # 这里可以添加手动注册服务的逻辑
        # 例如，注册网络引擎
        pass
    
    def unregister_service(self, service_id: str) -> bool:
        """
        注销服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 注销成功返回True，失败返回False
        """
        # 从服务注册表中移除
        if service_id in self.services:
            del self.services[service_id]
        
        # 从业务注册表中移除
        if service_id in self.businesses:
            del self.businesses[service_id]
        
        # 从引擎注册表中移除
        if service_id in self.engines:
            del self.engines[service_id]
        
        # 从数据库中移除
        self.db_manager.delete_service(service_id)
        
        return True
    
    def reload_services(self) -> Dict[str, Any]:
        """
        重新加载所有服务
        
        Returns:
            Dict[str, Any]: 重载结果
        """
        self.logger.log_progress("正在重新加载所有服务")
        self.services.clear()
        self.businesses.clear()
        self.engines.clear()
        
        result = self.discover_services()
        self.logger.log_success("服务重新加载完成")
        return result
    
    def update_service_health(self, service_id: str, is_healthy: bool, reason: str = None) -> bool:
        """
        更新服务健康状态
        
        Args:
            service_id: 服务ID
            is_healthy: 服务是否健康
            reason: 状态变更原因
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        status = ServiceStatus.VALID if is_healthy else ServiceStatus.INVALID
        
        # 更新数据库中的服务状态
        db_update_result = self.db_manager.update_service_status(service_id, status, reason)
        
        # 同时更新内存中的服务状态
        if db_update_result and service_id in self.services:
            service_info = self.services[service_id]
            # 更新内存中的状态信息
            if "info" in service_info:
                service_info["info"]["status"] = "valid" if is_healthy else "invalid"
                if reason:
                    service_info["info"]["reason"] = reason
            
            # 如果是业务服务，也更新businesses中的状态
            if service_id in self.businesses:
                self.businesses[service_id]["status"] = "valid" if is_healthy else "invalid"
                if reason:
                    self.businesses[service_id]["reason"] = reason
            
            # 如果是引擎服务，也更新engines中的状态
            if service_id in self.engines:
                engine = self.engines[service_id]
                engine.status = "running" if is_healthy else "failed"
        
        return db_update_result
    
    def check_service_health(self, service_id: str) -> bool:
        """
        检查服务健康状态
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 服务健康返回True，否则返回False
        """
        try:
            # 首先检查内存中的服务状态
            is_healthy = self._check_memory_service_health(service_id)
            if is_healthy is not None:
                return is_healthy
            
            # 然后检查数据库中的服务状态
            return self._check_db_service_health(service_id)
        except Exception as e:
            self.logger.error(f"检查服务 {service_id} 健康状态失败: {str(e)}")
            return False
    
    def _check_memory_service_health(self, service_id: str) -> Optional[bool]:
        """
        检查内存中的服务健康状态
        
        Args:
            service_id: 服务ID
            
        Returns:
            Optional[bool]: 健康返回True，不健康返回False，内存中不存在返回None
        """
        if service_id not in self.services:
            return None
        
        service_info = self.services[service_id]
        if not isinstance(service_info, dict):
            return None
        
        if "info" not in service_info:
            return None
        
        info = service_info["info"]
        if not isinstance(info, dict):
            return None
        
        if info.get("status") != "valid":
            return False
        
        # 对于引擎服务，额外检查引擎实例的状态
        if service_info.get("type") != "engine":
            return True
        
        if service_id not in self.engines:
            return False
        
        engine = self.engines[service_id]
        if not hasattr(engine, "status"):
            return False
        
        return engine.status == "running"
    
    def _check_db_service_health(self, service_id: str) -> bool:
        """
        检查数据库中的服务健康状态
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 健康返回True，否则返回False
        """
        if not self.db_manager:
            return False
        
        try:
            service = self.db_manager.get_service(service_id)
            if service and hasattr(service, "status"):
                return service.status == ServiceStatus.VALID
        except Exception as e:
            self.logger.log("ERROR", f"从数据库检查服务健康状态失败: {str(e)}", False)
        
        return False
    
    def check_all_services_health(self) -> Dict[str, Any]:
        """
        检查所有服务的健康状态
        
        Returns:
            Dict[str, Any]: 检查结果，包含健康和不健康的服务列表
        """
        result = {
            "healthy": [],
            "unhealthy": []
        }
        
        try:
            self._check_memory_services_health(result)
            self._check_db_services_health(result)
        except Exception as e:
            self.logger.log("ERROR", f"检查所有服务健康状态失败: {str(e)}", False)
            return {"healthy": [], "unhealthy": []}
        
        return result
    
    def _check_memory_services_health(self, result: Dict[str, Any]) -> None:
        """
        检查内存中所有服务的健康状态
        
        Args:
            result: 结果字典，用于存储健康检查结果
        """
        for service_id, service_info in self.services.items():
            try:
                is_healthy, reason = self._check_single_memory_service_health(service_id, service_info)
                
                if is_healthy:
                    result["healthy"].append(service_id)
                else:
                    result["unhealthy"].append({
                        "service_id": service_id,
                        "reason": reason or "Unknown health issue"
                    })
            except Exception as e:
                self.logger.error(f"检查服务 {service_id} 健康状态失败: {str(e)}")
                result["unhealthy"].append({
                    "service_id": service_id,
                    "reason": f"Health check failed: {str(e)}"
                })
    
    def _check_single_memory_service_health(self, service_id: str, service_info: Dict[str, Any]) -> tuple:
        """
        检查单个内存服务的健康状态
        
        Args:
            service_id: 服务ID
            service_info: 服务信息
            
        Returns:
            tuple: (is_healthy, reason)
        """
        if not isinstance(service_info, dict):
            return False, "Invalid service info"
        
        if "info" not in service_info:
            return False, "No info in service"
        
        info = service_info["info"]
        if not isinstance(info, dict):
            return False, "Invalid info format"
        
        status = info.get("status")
        reason = info.get("reason")
        is_healthy = status == "valid"
        
        if not is_healthy and self.db_manager:
            try:
                service = self.db_manager.get_service(service_id)
                if service and hasattr(service, "status"):
                    is_healthy = service.status == ServiceStatus.VALID
                    reason = getattr(service, "reason", None)
            except Exception as e:
                self.logger.error(f"从数据库检查服务 {service_id} 健康状态失败: {str(e)}")
        
        if service_info.get("type") == "engine" and service_id in self.engines:
            engine = self.engines[service_id]
            if hasattr(engine, "status") and engine.status != "running":
                is_healthy = False
                reason = f"Engine status: {engine.status}"
        
        return is_healthy, reason
    
    def _check_db_services_health(self, result: Dict[str, Any]) -> None:
        """
        检查数据库中存在但内存中不存在的服务
        
        Args:
            result: 结果字典，用于存储健康检查结果
        """
        if not self.db_manager:
            return
        
        try:
            db_services = self.db_manager.list_services()
            if not isinstance(db_services, list):
                return
            
            db_service_ids = {getattr(service, "service_id", None) for service in db_services}
            db_service_ids.discard(None)
            memory_service_ids = set(self.services.keys())
            
            missing_services = db_service_ids - memory_service_ids
            
            for service_id in missing_services:
                try:
                    self._check_single_db_service_health(service_id, result)
                except Exception as e:
                    self.logger.error(f"检查数据库服务 {service_id} 健康状态失败: {str(e)}")
                    result["unhealthy"].append({
                        "service_id": service_id,
                        "reason": f"Database check failed: {str(e)}"
                    })
        except Exception as e:
            self.logger.log("ERROR", f"获取数据库服务列表失败: {str(e)}", False)
    
    def _check_single_db_service_health(self, service_id: str, result: Dict[str, Any]) -> None:
        """
        检查单个数据库服务的健康状态
        
        Args:
            service_id: 服务ID
            result: 结果字典，用于存储健康检查结果
        """
        service = self.db_manager.get_service(service_id)
        if not service:
            return
        
        if hasattr(service, "status") and service.status == ServiceStatus.VALID:
            result["healthy"].append(service_id)
        else:
            reason = getattr(service, "reason", None)
            result["unhealthy"].append({
                "service_id": service_id,
                "reason": reason or "Service not in memory"
            })
    
    def is_service_allowed(self, source_service_id: str, target_service_id: str) -> bool:
        """
        检查服务是否被允许调用目标服务
        
        Args:
            source_service_id: 源服务ID
            target_service_id: 目标服务ID
            
        Returns:
            bool: 允许调用返回True，否则返回False
        """
        # 交互规则：
        # 1. 业务服务可以调用引擎服务
        # 2. 引擎服务不能直接相互调用
        # 3. 引擎服务可以被业务服务调用
        
        # 获取源服务和目标服务的类型
        source_service = self.db_manager.get_service(source_service_id)
        target_service = self.db_manager.get_service(target_service_id)
        
        if not source_service or not target_service:
            return False
        
        # 引擎服务不能直接相互调用
        if source_service.service_type == ServiceType.ENGINE and target_service.service_type == ServiceType.ENGINE:
            return False
        
        # 其他情况都允许
        return True
