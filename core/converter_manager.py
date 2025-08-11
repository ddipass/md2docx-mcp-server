"""
转换管理器 - 管理 Markdown 到 DOCX 的转换操作
"""
import os
import sys
import subprocess
import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .config_manager import get_config_manager


class ConversionError(Exception):
    """转换错误"""
    pass


class ConverterManager:
    """转换管理器"""
    
    def __init__(self):
        self.config = get_config_manager()
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("md2docx_converter")
        logger.setLevel(getattr(logging, self.config.batch_settings.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def convert_single_file(
        self, 
        input_file: str, 
        output_file: Optional[str] = None,
        debug: bool = None
    ) -> Dict[str, Union[str, bool]]:
        """
        转换单个 Markdown 文件为 DOCX
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            debug: 调试模式（可选，使用配置默认值）
        
        Returns:
            转换结果字典
        """
        try:
            # 验证输入文件
            input_path = Path(input_file)
            if not input_path.exists():
                raise ConversionError(f"输入文件不存在: {input_file}")
            
            if not input_path.suffix.lower() in self.config.file_settings.supported_extensions:
                raise ConversionError(f"不支持的文件类型: {input_path.suffix}")
            
            # 确定输出文件路径
            if output_file is None:
                output_dir = Path(self.config.conversion_settings.output_dir)
                if not output_dir.is_absolute():
                    # 如果是相对路径，相对于 MCP 服务器的工作目录，而不是当前工作目录
                    mcp_server_dir = Path(__file__).parent.parent  # md2docx-mcp-server 目录
                    output_dir = mcp_server_dir / output_dir
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = str(output_dir / f"{input_path.stem}.docx")
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
                result = await self._convert_via_subprocess(input_file, output_file, debug)
            else:
                result = await self._convert_via_import(input_file, output_file, debug)
            
            end_time = time.time()
            
            return {
                'success': result['success'],
                'input_file': input_file,
                'output_file': str(Path(output_file).absolute()),  # 显示实际使用的绝对路径
                'message': result['message'],
                'duration': round(end_time - start_time, 2),
                'file_size': input_path.stat().st_size if input_path.exists() else 0,
                'debug_info': {
                    'absolute_output_path': str(Path(output_file).absolute()),
                    'current_working_dir': str(Path.cwd()),
                    'md2docx_working_dir': str(Path(self.config.server_settings.md2docx_project_path)),
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
                'message': str(e),
                'duration': 0,
                'file_size': 0
            }
    
    async def _convert_via_subprocess(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool
    ) -> Dict[str, Union[str, bool]]:
        """通过子进程调用 md2docx 转换器"""
        try:
            md2docx_path = Path(self.config.server_settings.md2docx_project_path)
            
            # 如果是相对路径，相对于MCP服务器目录
            if not md2docx_path.is_absolute():
                mcp_server_dir = Path(__file__).parent.parent  # md2docx-mcp-server 目录
                md2docx_path = mcp_server_dir / md2docx_path
            
            if not md2docx_path.exists():
                raise ConversionError(f"MD2DOCX 项目路径不存在: {md2docx_path}")
            
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
                self.logger.info(f"Working directory: {md2docx_path}")
                self.logger.info(f"Input file (abs): {abs_input_file}")
                self.logger.info(f"Output file (abs): {abs_output_file}")
            
            # 设置环境变量，添加 src 目录到 PYTHONPATH
            env = os.environ.copy()
            src_path = str(md2docx_path / "src")
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{src_path}:{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = src_path
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(md2docx_path),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # 调试信息
            if debug:
                self.logger.info(f"Command: {' '.join(cmd)}")
                self.logger.info(f"Working directory: {md2docx_path}")
                self.logger.info(f"Return code: {process.returncode}")
                self.logger.info(f"Stdout: {stdout.decode('utf-8') if stdout else 'None'}")
                self.logger.info(f"Stderr: {stderr.decode('utf-8') if stderr else 'None'}")
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'message': f"转换成功: {abs_output_file}",  # 显示绝对路径
                    'debug_info': {
                        'command': ' '.join(cmd),
                        'stdout': stdout.decode('utf-8') if stdout else '',
                        'stderr': stderr.decode('utf-8') if stderr else '',
                        'return_code': process.returncode,
                        'abs_input': abs_input_file,
                        'abs_output': abs_output_file
                    } if debug else None
                }
            else:
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                return {
                    'success': False,
                    'message': f"转换失败: {error_msg}",
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
                'message': f"子进程调用失败: {str(e)}"
            }
    
    async def _convert_via_import(
        self, 
        input_file: str, 
        output_file: str, 
        debug: bool
    ) -> Dict[str, Union[str, bool]]:
        """通过直接导入 Python 模块转换"""
        try:
            # 添加 md2docx 项目路径到 sys.path
            md2docx_path = Path(self.config.server_settings.md2docx_project_path)
            
            # 如果是相对路径，相对于MCP服务器目录
            if not md2docx_path.is_absolute():
                mcp_server_dir = Path(__file__).parent.parent  # md2docx-mcp-server 目录
                md2docx_path = mcp_server_dir / md2docx_path
            
            if str(md2docx_path) not in sys.path:
                sys.path.insert(0, str(md2docx_path))
            
            # 导入转换器
            from src.converter import BaseConverter
            
            # 读取输入文件
            with open(input_file, 'r', encoding=self.config.file_settings.encoding) as f:
                content = f.read()
            
            # 执行转换
            converter = BaseConverter(debug=debug)
            doc = converter.convert(content)
            
            # 保存文档（处理文件占用情况）
            await self._save_document_with_retry(doc, output_file)
            
            return {
                'success': True,
                'message': f"转换成功: {output_file}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Python 模块调用失败: {str(e)}"
            }
    
    async def _save_document_with_retry(self, doc, output_file: str) -> None:
        """带重试机制的文档保存"""
        output_path = Path(output_file)
        final_output_file = output_file
        
        for attempt in range(self.config.conversion_settings.max_retry_attempts):
            try:
                doc.save(final_output_file)
                return
            except PermissionError:
                if self.config.conversion_settings.auto_timestamp:
                    timestamp = int(time.time())
                    new_filename = f"{output_path.stem}_{timestamp}{output_path.suffix}"
                    final_output_file = str(output_path.parent / new_filename)
                    self.logger.warning(f"文件被占用，尝试保存为: {final_output_file}")
                else:
                    raise
            except Exception as e:
                raise ConversionError(f"保存文档失败: {str(e)}")
        
        raise ConversionError(f"多次尝试后仍无法保存文件: {output_file}")
    
    async def batch_convert(
        self, 
        input_dir: str, 
        output_dir: Optional[str] = None,
        file_pattern: str = "*.md"
    ) -> Dict[str, Union[int, List[Dict]]]:
        """
        批量转换目录中的 Markdown 文件
        
        Args:
            input_dir: 输入目录路径
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
            
            self.logger.info(f"找到 {len(md_files)} 个文件待转换")
            
            # 并行转换
            results = []
            success_count = 0
            failed_count = 0
            
            # 使用线程池进行并行处理
            with ThreadPoolExecutor(max_workers=self.config.batch_settings.parallel_jobs) as executor:
                # 提交任务
                future_to_file = {}
                for md_file in md_files:
                    output_file = str(output_path / f"{md_file.stem}.docx")
                    
                    # 检查是否跳过已存在的文件
                    if self.config.batch_settings.skip_existing and Path(output_file).exists():
                        results.append({
                            'success': True,
                            'input_file': str(md_file),
                            'output_file': output_file,
                            'message': '文件已存在，跳过转换',
                            'duration': 0,
                            'file_size': md_file.stat().st_size
                        })
                        success_count += 1
                        continue
                    
                    future = executor.submit(
                        asyncio.run,
                        self.convert_single_file(str(md_file), output_file)
                    )
                    future_to_file[future] = md_file
                
                # 收集结果
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        success_count += 1
                    else:
                        failed_count += 1
            
            # 创建日志文件
            if self.config.batch_settings.create_log:
                await self._create_batch_log(results, input_dir, output_dir)
            
            return {
                'total': len(md_files),
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
        output_dir: str
    ) -> None:
        """创建批量转换日志"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"batch_convert_{timestamp}.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"MD2DOCX 批量转换日志\n")
                f.write(f"转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"输入目录: {input_dir}\n")
                f.write(f"输出目录: {output_dir}\n")
                f.write(f"{'='*80}\n\n")
                
                for result in results:
                    status = "✅ 成功" if result['success'] else "❌ 失败"
                    f.write(f"{status} | {result['input_file']} -> {result['output_file']}\n")
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


# 全局转换管理器实例
_converter_manager = None

def get_converter_manager() -> ConverterManager:
    """获取转换管理器实例"""
    global _converter_manager
    if _converter_manager is None:
        _converter_manager = ConverterManager()
    return _converter_manager
