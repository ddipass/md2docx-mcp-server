"""
统一转换管理器 - 支持多种输出格式的 Markdown 转换
"""
import os
import sys
import subprocess
import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from abc import ABC, abstractmethod

from .config_manager import get_config_manager


class ConversionError(Exception):
    """转换错误"""
    pass


class BaseConverter(ABC):
    """转换器基类"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"md2{self.get_format()}_converter")
        logger.setLevel(getattr(logging, self.config.batch_settings.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    def get_format(self) -> str:
        """获取输出格式"""
        pass
    
    @abstractmethod
    def get_project_path(self) -> Path:
        """获取项目路径"""
        pass
    
    @abstractmethod
    def get_output_extension(self) -> str:
        """获取输出文件扩展名"""
        pass
    
    @abstractmethod
    async def _convert_via_subprocess(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """通过子进程转换"""
        pass
    
    @abstractmethod
    async def _convert_via_import(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """通过Python模块导入转换"""
        pass
    
    def validate_input(self, input_file: str) -> bool:
        """验证输入文件"""
        input_path = Path(input_file)
        return (
            input_path.exists() 
            and input_path.is_file() 
            and input_path.suffix.lower() in self.config.file_settings.supported_extensions
        )
    
    def get_supported_extensions(self) -> List[str]:
        """获取支持的扩展名"""
        return self.config.file_settings.supported_extensions
    
    async def convert(
        self, 
        input_file: str, 
        output_file: Optional[str] = None,
        debug: bool = None,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """
        转换文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            debug: 调试模式（可选，使用配置默认值）
            **kwargs: 格式特定参数
        
        Returns:
            转换结果字典
        """
        try:
            # 验证输入文件
            input_path = Path(input_file)
            if not input_path.exists():
                raise ConversionError(f"输入文件不存在: {input_file}")
            
            if not input_path.suffix.lower() in self.get_supported_extensions():
                raise ConversionError(f"不支持的文件类型: {input_path.suffix}")
            
            # 确定输出文件路径
            if output_file is None:
                output_dir = Path(self.config.conversion_settings.output_dir)
                if not output_dir.is_absolute():
                    # 如果是相对路径，相对于 MCP 服务器的工作目录
                    mcp_server_dir = Path(__file__).parent.parent  # md2docx-mcp-server 目录
                    output_dir = mcp_server_dir / output_dir
                
                # 创建格式特定的子目录
                format_dir = output_dir / self.get_format()
                format_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = str(format_dir / f"{input_path.stem}{self.get_output_extension()}")
            else:
                # 确保输出文件路径是绝对路径
                output_path = Path(output_file)
                if not output_path.is_absolute():
                    # 相对于 MCP 服务器目录
                    mcp_server_dir = Path(__file__).parent.parent
                    output_path = mcp_server_dir / output_path
                output_file = str(output_path)
                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 确定调试模式
            if debug is None:
                debug = self.config.conversion_settings.debug_mode
            
            # 调试信息：显示实际路径
            if debug:
                self.logger.info(f"Input file (absolute): {input_path.absolute()}")
                self.logger.info(f"Output file (absolute): {Path(output_file).absolute()}")
                self.logger.info(f"Current working directory: {Path.cwd()}")
            
            # 执行转换
            start_time = time.time()
            
            if self.config.server_settings.use_subprocess:
                result = await self._convert_via_subprocess(input_file, output_file, debug, **kwargs)
            else:
                result = await self._convert_via_import(input_file, output_file, debug, **kwargs)
            
            end_time = time.time()
            
            return {
                'success': result['success'],
                'input_file': input_file,
                'output_file': str(Path(output_file).absolute()),
                'format': self.get_format(),
                'message': result['message'],
                'duration': round(end_time - start_time, 2),
                'file_size': input_path.stat().st_size if input_path.exists() else 0,
                'debug_info': {
                    'absolute_output_path': str(Path(output_file).absolute()),
                    'current_working_dir': str(Path.cwd()),
                    'project_working_dir': str(self.get_project_path()),
                    'mcp_server_dir': str(Path(__file__).parent.parent),
                    'subprocess_result': result.get('debug_info')
                } if debug else None
            }
        
        except Exception as e:
            self.logger.error(f"转换失败: {input_file} -> {e}")
            return {
                'success': False,
                'input_file': input_file,
                'output_file': output_file or 'N/A',
                'format': self.get_format(),
                'message': str(e),
                'duration': 0,
                'file_size': 0
            }


class DOCXConverter(BaseConverter):
    """DOCX 转换器"""
    
    def get_format(self) -> str:
        return "docx"
    
    def get_project_path(self) -> Path:
        project_path = Path(self.config.server_settings.md2docx_project_path)
        if not project_path.is_absolute():
            mcp_server_dir = Path(__file__).parent.parent
            project_path = mcp_server_dir / project_path
        return project_path
    
    def get_output_extension(self) -> str:
        return self.config.file_settings.output_extension_docx
    
    async def _convert_via_subprocess(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """通过子进程调用 md2docx 转换器"""
        try:
            project_path = self.get_project_path()
            if not project_path.exists():
                raise ConversionError(f"MD2DOCX 项目路径不存在: {project_path}")
            
            # 确保使用绝对路径
            abs_input_file = str(Path(input_file).absolute())
            abs_output_file = str(Path(output_file).absolute())
            
            # 构建命令
            cmd = [
                sys.executable, "src/cli.py",
                abs_input_file, abs_output_file
            ]
            
            if debug:
                cmd.append("--debug")
            
            # 调试信息
            if debug:
                self.logger.info(f"Executing command: {' '.join(cmd)}")
                self.logger.info(f"Working directory: {project_path}")
            
            # 设置环境变量
            env = os.environ.copy()
            src_path = str(project_path / "src")
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{src_path}:{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = src_path
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(project_path),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'message': f"DOCX转换成功: {abs_output_file}",
                    'debug_info': {
                        'command': ' '.join(cmd),
                        'stdout': stdout.decode('utf-8') if stdout else '',
                        'stderr': stderr.decode('utf-8') if stderr else '',
                        'return_code': process.returncode
                    } if debug else None
                }
            else:
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                return {
                    'success': False,
                    'message': f"DOCX转换失败: {error_msg}",
                    'debug_info': {
                        'command': ' '.join(cmd),
                        'stdout': stdout.decode('utf-8') if stdout else '',
                        'stderr': stderr.decode('utf-8') if stderr else '',
                        'return_code': process.returncode
                    } if debug else None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"DOCX子进程调用失败: {str(e)}"
            }
    
    async def _convert_via_import(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """通过直接导入 Python 模块转换"""
        try:
            project_path = self.get_project_path()
            if str(project_path) not in sys.path:
                sys.path.insert(0, str(project_path))
            
            # 导入转换器
            from src.converter import BaseConverter
            
            # 读取输入文件
            with open(input_file, 'r', encoding=self.config.file_settings.encoding) as f:
                content = f.read()
            
            # 执行转换
            converter = BaseConverter(debug=debug)
            doc = converter.convert(content)
            
            # 保存文档
            doc.save(output_file)
            
            return {
                'success': True,
                'message': f"DOCX转换成功: {output_file}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"DOCX Python模块调用失败: {str(e)}"
            }


class PPTXConverter(BaseConverter):
    """PPTX 转换器"""
    
    def get_format(self) -> str:
        return "pptx"
    
    def get_project_path(self) -> Path:
        project_path = Path(self.config.server_settings.md2pptx_project_path)
        if not project_path.is_absolute():
            mcp_server_dir = Path(__file__).parent.parent
            project_path = mcp_server_dir / project_path
        return project_path
    
    def get_output_extension(self) -> str:
        return self.config.file_settings.output_extension_pptx
    
    async def _convert_via_subprocess(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """通过子进程调用 md2pptx 转换器"""
        try:
            project_path = self.get_project_path()
            if not project_path.exists():
                raise ConversionError(f"MD2PPTX 项目路径不存在: {project_path}")
            
            # 确保使用绝对路径
            abs_output_file = str(Path(output_file).absolute())
            
            # 使用当前 MCP 服务器的 Python 环境，而不是 md2pptx 项目的环境
            mcp_server_dir = Path(__file__).parent.parent
            
            # 确保使用当前虚拟环境的 Python
            if 'VIRTUAL_ENV' in os.environ:
                # 如果在虚拟环境中，使用虚拟环境的 Python
                venv_python = Path(os.environ['VIRTUAL_ENV']) / 'bin' / 'python'
                if venv_python.exists():
                    python_executable = str(venv_python)
                else:
                    python_executable = sys.executable
            else:
                # 检查是否在 .venv 目录中
                venv_python = mcp_server_dir / '.venv' / 'bin' / 'python'
                if venv_python.exists():
                    python_executable = str(venv_python)
                else:
                    python_executable = sys.executable
            
            # 构建命令 - md2pptx 从 stdin 读取
            cmd = [python_executable, "md2pptx", abs_output_file]
            
            # 调试信息
            if debug:
                self.logger.info(f"Executing command: {' '.join(cmd)}")
                self.logger.info(f"Working directory: {project_path}")
                self.logger.info(f"Python executable: {python_executable}")
            
            # 读取输入文件内容
            with open(input_file, 'r', encoding=self.config.file_settings.encoding) as f:
                markdown_content = f.read()
            
            # 添加模板信息到 markdown 内容开头（如果配置了模板）
            template_file = self.config.pptx_settings.template_file
            if template_file and template_file != "":
                # 检查模板文件是否存在
                template_path = project_path / template_file
                if template_path.exists():
                    markdown_content = f"template: {template_file}\n\n{markdown_content}"
            
            # 设置环境变量，确保使用当前虚拟环境的包
            env = os.environ.copy()
            
            # 添加 md2pptx 项目目录到 PYTHONPATH
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{project_path}:{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = str(project_path)
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(project_path),
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=markdown_content.encode('utf-8'))
            
            if debug:
                self.logger.info(f"Return code: {process.returncode}")
                self.logger.info(f"Stdout: {stdout.decode('utf-8') if stdout else 'None'}")
                self.logger.info(f"Stderr: {stderr.decode('utf-8') if stderr else 'None'}")
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'message': f"PPTX转换成功: {abs_output_file}",
                    'debug_info': {
                        'command': ' '.join(cmd),
                        'stdout': stdout.decode('utf-8') if stdout else '',
                        'stderr': stderr.decode('utf-8') if stderr else '',
                        'return_code': process.returncode,
                        'template_used': template_file,
                        'python_executable': python_executable
                    } if debug else None
                }
            else:
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                return {
                    'success': False,
                    'message': f"PPTX转换失败: {error_msg}",
                    'debug_info': {
                        'command': ' '.join(cmd),
                        'stdout': stdout.decode('utf-8') if stdout else '',
                        'stderr': stderr.decode('utf-8') if stderr else '',
                        'return_code': process.returncode,
                        'python_executable': python_executable
                    } if debug else None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"PPTX子进程调用失败: {str(e)}"
            }
    
    async def _convert_via_import(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """通过直接导入 Python 模块转换"""
        # md2pptx 的 Python 模块导入比较复杂，暂时不实现
        # 可以在后续版本中添加
        return {
            'success': False,
            'message': "PPTX Python模块导入暂未实现，请使用子进程模式"
        }


class UnifiedConverterManager:
    """统一转换管理器"""
    
    def __init__(self):
        self.config = get_config_manager()
        self.logger = self._setup_logger()
        
        # 初始化转换器
        self.converters = {
            'docx': DOCXConverter(self.config),
            'pptx': PPTXConverter(self.config)
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("unified_converter")
        logger.setLevel(getattr(logging, self.config.batch_settings.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_converter(self, format_type: str) -> BaseConverter:
        """获取指定格式的转换器"""
        if format_type not in self.converters:
            raise ConversionError(f"不支持的格式: {format_type}")
        return self.converters[format_type]
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        return list(self.converters.keys())
    
    async def convert_single_file(
        self, 
        input_file: str, 
        output_format: str = "docx",
        output_file: Optional[str] = None,
        debug: bool = None,
        **kwargs
    ) -> Dict[str, Union[str, bool]]:
        """
        转换单个文件
        
        Args:
            input_file: 输入文件路径
            output_format: 输出格式 (docx/pptx)
            output_file: 输出文件路径（可选）
            debug: 调试模式
            **kwargs: 格式特定参数
        
        Returns:
            转换结果字典
        """
        try:
            converter = self.get_converter(output_format)
            return await converter.convert(input_file, output_file, debug, **kwargs)
        except Exception as e:
            self.logger.error(f"转换失败: {input_file} -> {e}")
            return {
                'success': False,
                'input_file': input_file,
                'output_file': output_file or 'N/A',
                'format': output_format,
                'message': str(e),
                'duration': 0,
                'file_size': 0
            }
    
    async def convert_multiple_formats(
        self, 
        input_file: str, 
        output_formats: List[str],
        output_dir: Optional[str] = None,
        debug: bool = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        将单个文件转换为多种格式
        
        Args:
            input_file: 输入文件路径
            output_formats: 输出格式列表
            output_dir: 输出目录（可选）
            debug: 调试模式
            **kwargs: 格式特定参数
        
        Returns:
            转换结果字典
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for format_type in output_formats:
            try:
                # 确定输出文件路径
                if output_dir:
                    output_path = Path(output_dir) / format_type
                    output_path.mkdir(parents=True, exist_ok=True)
                    output_file = str(output_path / f"{Path(input_file).stem}.{format_type}")
                else:
                    output_file = None
                
                result = await self.convert_single_file(
                    input_file, format_type, output_file, debug, **kwargs
                )
                results.append(result)
                
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'input_file': input_file,
                    'output_file': 'N/A',
                    'format': format_type,
                    'message': str(e),
                    'duration': 0,
                    'file_size': 0
                })
                failed_count += 1
        
        return {
            'total_formats': len(output_formats),
            'success': success_count,
            'failed': failed_count,
            'results': results,
            'message': f"多格式转换完成: 成功 {success_count}, 失败 {failed_count}"
        }
    
    async def batch_convert(
        self, 
        input_dir: str, 
        output_formats: List[str] = ["docx"],
        output_dir: Optional[str] = None,
        file_pattern: str = "*.md"
    ) -> Dict[str, Union[int, List[Dict]]]:
        """
        批量转换目录中的文件
        
        Args:
            input_dir: 输入目录路径
            output_formats: 输出格式列表
            output_dir: 输出目录路径（可选）
            file_pattern: 文件匹配模式
        
        Returns:
            批量转换结果
        """
        try:
            input_path = Path(input_dir)
            if not input_path.exists():
                raise ConversionError(f"输入目录不存在: {input_dir}")
            
            # 确定输出目录
            if output_dir is None:
                output_dir = self.config.conversion_settings.output_dir
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 查找匹配的文件
            md_files = list(input_path.glob(file_pattern))
            if not md_files:
                return {
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'results': [],
                    'message': f"在 {input_dir} 中未找到匹配 {file_pattern} 的文件"
                }
            
            self.logger.info(f"找到 {len(md_files)} 个文件待转换为 {len(output_formats)} 种格式")
            
            # 并行转换
            results = []
            success_count = 0
            failed_count = 0
            
            # 使用线程池进行并行处理
            with ThreadPoolExecutor(max_workers=self.config.batch_settings.parallel_jobs) as executor:
                # 提交任务
                future_to_file = {}
                for md_file in md_files:
                    future = executor.submit(
                        asyncio.run,
                        self.convert_multiple_formats(
                            str(md_file), 
                            output_formats, 
                            str(output_path)
                        )
                    )
                    future_to_file[future] = md_file
                
                # 收集结果
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.extend(result['results'])
                    success_count += result['success']
                    failed_count += result['failed']
            
            # 创建日志文件
            if self.config.batch_settings.create_log:
                await self._create_batch_log(results, input_dir, output_dir, output_formats)
            
            return {
                'total': len(md_files) * len(output_formats),
                'success': success_count,
                'failed': failed_count,
                'results': results,
                'message': f"批量转换完成: 成功 {success_count}, 失败 {failed_count}"
            }
        
        except Exception as e:
            self.logger.error(f"批量转换失败: {str(e)}")
            return {
                'total': 0,
                'success': 0,
                'failed': 1,
                'results': [],
                'message': f"批量转换失败: {str(e)}"
            }
    
    async def _create_batch_log(
        self, 
        results: List[Dict], 
        input_dir: str, 
        output_dir: str,
        output_formats: List[str]
    ) -> None:
        """创建批量转换日志"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"batch_convert_{timestamp}.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"统一转换器批量转换日志\n")
                f.write(f"转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"输入目录: {input_dir}\n")
                f.write(f"输出目录: {output_dir}\n")
                f.write(f"输出格式: {', '.join(output_formats)}\n")
                f.write(f"{'='*80}\n\n")
                
                for result in results:
                    status = "✅ 成功" if result['success'] else "❌ 失败"
                    f.write(f"{status} | {result['format'].upper()} | {result['input_file']} -> {result['output_file']}\n")
                    f.write(f"    消息: {result['message']}\n")
                    f.write(f"    耗时: {result['duration']}s\n")
                    f.write(f"    文件大小: {result['file_size']} bytes\n\n")
            
            self.logger.info(f"批量转换日志已创建: {log_file}")
        
        except Exception as e:
            self.logger.error(f"创建日志失败: {str(e)}")
    
    async def list_markdown_files(
        self, 
        directory: str, 
        recursive: bool = False
    ) -> Dict[str, Union[int, List[str]]]:
        """
        列出目录中的 Markdown 文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归搜索
        
        Returns:
            文件列表结果
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                raise ConversionError(f"目录不存在: {directory}")
            
            if not dir_path.is_dir():
                raise ConversionError(f"路径不是目录: {directory}")
            
            # 搜索文件
            md_files = []
            extensions = self.config.file_settings.supported_extensions
            
            if recursive:
                for ext in extensions:
                    md_files.extend(dir_path.rglob(f"*{ext}"))
            else:
                for ext in extensions:
                    md_files.extend(dir_path.glob(f"*{ext}"))
            
            # 转换为字符串列表并排序
            file_list = [str(f) for f in md_files]
            file_list.sort()
            
            return {
                'count': len(file_list),
                'files': file_list,
                'directory': directory,
                'recursive': recursive
            }
        
        except Exception as e:
            self.logger.error(f"列出文件失败: {str(e)}")
            return {
                'count': 0,
                'files': [],
                'directory': directory,
                'recursive': recursive,
                'error': str(e)
            }


# 全局统一转换管理器实例
_unified_converter_manager = None

def get_unified_converter_manager() -> UnifiedConverterManager:
    """获取统一转换管理器实例"""
    global _unified_converter_manager
    if _unified_converter_manager is None:
        _unified_converter_manager = UnifiedConverterManager()
    return _unified_converter_manager
