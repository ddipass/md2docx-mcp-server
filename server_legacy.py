#!/usr/bin/env python3
"""
MD2DOCX MCP Server - Markdown 到 DOCX 转换服务器
基于 Model Context Protocol (MCP) 的文档转换服务
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# ===== 工作目录和环境设置 =====
SCRIPT_DIR = Path(__file__).parent.absolute()
print(f"🔧 脚本目录: {SCRIPT_DIR}")
print(f"🔧 当前工作目录: {Path.cwd()}")

# 切换到脚本目录
if Path.cwd() != SCRIPT_DIR:
    print(f"🔄 切换工作目录: {Path.cwd()} -> {SCRIPT_DIR}")
    os.chdir(SCRIPT_DIR)
    print(f"✅ 工作目录已切换到: {Path.cwd()}")

# ===== 自动激活虚拟环境 =====
def activate_virtual_environment():
    """自动激活当前项目的虚拟环境"""
    current_dir = Path(__file__).parent.absolute()
    venv_path = current_dir / ".venv"
    
    print(f"🔍 检查虚拟环境: {venv_path}")
    
    if venv_path.exists():
        print(f"✅ 找到虚拟环境目录: {venv_path}")
        
        lib_path = venv_path / "lib"
        site_packages_path = None
        detected_version = None
        
        if lib_path.exists():
            python_dirs = []
            for item in lib_path.iterdir():
                if item.is_dir() and item.name.startswith('python'):
                    python_dirs.append(item.name)
            
            python_dirs.sort(reverse=True)
            print(f"🔍 发现Python版本: {python_dirs}")
            
            for py_version in python_dirs:
                potential_path = lib_path / py_version / "site-packages"
                if potential_path.exists():
                    site_packages_path = potential_path
                    detected_version = py_version
                    print(f"✅ 找到可用的Python版本: {py_version}")
                    break
        
        if site_packages_path:
            site_packages_str = str(site_packages_path)
            if site_packages_str not in sys.path:
                sys.path.insert(0, site_packages_str)
                print(f"✅ 虚拟环境已自动激活!")
                print(f"📦 Python版本: {detected_version}")
                print(f"📦 Site-packages路径: {site_packages_str}")
            
            os.environ['VIRTUAL_ENV'] = str(venv_path)
            
            venv_bin = venv_path / "bin"
            if venv_bin.exists():
                current_path = os.environ.get('PATH', '')
                if str(venv_bin) not in current_path:
                    os.environ['PATH'] = f"{venv_bin}:{current_path}"
                    print(f"🔧 PATH已更新")
        else:
            print(f"⚠️  虚拟环境存在但未找到site-packages目录")
    else:
        print(f"⚠️  虚拟环境目录不存在: {venv_path}")
        print("💡 提示: 请确保已创建虚拟环境 (.venv)")
        print("💡 创建命令: uv sync")

# 激活虚拟环境
print("🚀 正在启动 MD2DOCX MCP Server...")
activate_virtual_environment()

# ===== 导入依赖模块 =====
from mcp.server.fastmcp import FastMCP
from core import get_config_manager, reload_config
from core.unified_converter_manager import get_unified_converter_manager

# 初始化配置和转换管理器
config_manager = get_config_manager()
unified_converter_manager = get_unified_converter_manager()

print(f"⚙️  配置管理器已初始化")
print(f"🔄 统一转换管理器已初始化")

# 创建 MCP 服务器
mcp = FastMCP("MD2DOCX-Converter")

# ===== 配置管理工具 =====

@mcp.tool()
async def configure_converter(
    action: str = "show",
    setting_type: str = "all",
    **kwargs
) -> str:
    """
    配置转换器参数设置
    
    Args:
        action: 操作类型 (show/update/reset)
        setting_type: 设置类型 (conversion/batch/file/server/all)
        **kwargs: 具体的配置参数
        
    Returns:
        配置操作结果
        
    Use cases:
        - 查看当前配置: configure_converter("show", "all")
        - 更新转换设置: configure_converter("update", "conversion", debug_mode=True)
        - 更新批量设置: configure_converter("update", "batch", parallel_jobs=8)
        - 更新服务器设置: configure_converter("update", "server", md2docx_project_path="/path/to/md2docx")
    """
    
    try:
        global config_manager
        
        if action == "show":
            if setting_type == "all":
                return config_manager.get_config_summary()
            elif setting_type == "conversion":
                settings = config_manager.conversion_settings
                return f"""🔧 转换设置:
- 调试模式: {settings.debug_mode}
- 输出目录: {settings.output_dir}
- 保持结构: {settings.preserve_structure}
- 自动时间戳: {settings.auto_timestamp}
- 最大重试次数: {settings.max_retry_attempts}"""
            elif setting_type == "batch":
                settings = config_manager.batch_settings
                return f"""📦 批量设置:
- 并行任务数: {settings.parallel_jobs}
- 跳过已存在: {settings.skip_existing}
- 创建日志: {settings.create_log}
- 日志级别: {settings.log_level}"""
            elif setting_type == "file":
                settings = config_manager.file_settings
                return f"""📁 文件设置:
- 支持扩展名: {', '.join(settings.supported_extensions)}
- 输出扩展名: {settings.output_extension}
- 文件编码: {settings.encoding}"""
            elif setting_type == "server":
                settings = config_manager.server_settings
                return f"""🖥️  服务器设置:
- MD2DOCX 项目路径: {settings.md2docx_project_path}
- 使用子进程: {settings.use_subprocess}
- 使用 Python 导入: {settings.use_python_import}"""
        
        elif action == "update":
            if setting_type == "conversion":
                config_manager.update_conversion_settings(**kwargs)
                return f"✅ 转换设置已更新: {kwargs}"
            elif setting_type == "batch":
                config_manager.update_batch_settings(**kwargs)
                return f"✅ 批量设置已更新: {kwargs}"
            elif setting_type == "file":
                config_manager.update_file_settings(**kwargs)
                return f"✅ 文件设置已更新: {kwargs}"
            elif setting_type == "server":
                config_manager.update_server_settings(**kwargs)
                return f"✅ 服务器设置已更新: {kwargs}"
        
        elif action == "reset":
            config_manager.reset_to_defaults()
            return "✅ 配置已重置为默认值"
        
        return f"❌ 未知操作: {action} 或设置类型: {setting_type}"
    
    except Exception as e:
        return f"❌ 配置操作失败: {str(e)}"

@mcp.tool()
async def quick_config_debug_mode(enabled: bool = True) -> str:
    """
    快速设置调试模式
    
    Args:
        enabled: 是否启用调试模式
        
    Returns:
        设置结果
        
    Use cases:
        - 启用调试: quick_config_debug_mode(True)
        - 禁用调试: quick_config_debug_mode(False)
    """
    try:
        config_manager.update_conversion_settings(debug_mode=enabled)
        return f"✅ 调试模式已{'启用' if enabled else '禁用'}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"

@mcp.tool()
async def quick_config_output_dir(output_dir: str = "output") -> str:
    """
    快速设置输出目录
    
    Args:
        output_dir: 输出目录路径
        
    Returns:
        设置结果
        
    Use cases:
        - 设置输出目录: quick_config_output_dir("/path/to/output")
        - 使用默认目录: quick_config_output_dir()
    """
    try:
        config_manager.update_conversion_settings(output_dir=output_dir)
        return f"✅ 输出目录已设置为: {output_dir}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"

@mcp.tool()
async def quick_config_parallel_jobs(jobs: int = 4) -> str:
    """
    快速设置并行任务数
    
    Args:
        jobs: 并行任务数量
        
    Returns:
        设置结果
        
    Use cases:
        - 设置并行数: quick_config_parallel_jobs(8)
        - 使用默认值: quick_config_parallel_jobs()
    """
    try:
        config_manager.update_batch_settings(parallel_jobs=jobs)
        return f"✅ 并行任务数已设置为: {jobs}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"

@mcp.tool()
async def quick_config_pptx_template(template_file: str = "Martin Template.pptx") -> str:
    """
    快速设置 PPTX 模板文件
    
    Args:
        template_file: PPTX 模板文件路径
        
    Returns:
        设置结果
        
    Use cases:
        - 设置默认模板: quick_config_pptx_template()
        - 设置自定义模板: quick_config_pptx_template("custom.pptx")
    """
    try:
        config_manager.update_pptx_settings(template_file=template_file)
        return f"✅ PPTX模板已设置为: {template_file}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"

@mcp.tool()
async def quick_config_default_format(format_type: str = "docx") -> str:
    """
    快速设置默认输出格式
    
    Args:
        format_type: 默认输出格式 (docx/pptx)
        
    Returns:
        设置结果
        
    Use cases:
        - 设置DOCX为默认: quick_config_default_format("docx")
        - 设置PPTX为默认: quick_config_default_format("pptx")
    """
    try:
        if format_type not in unified_converter_manager.get_supported_formats():
            return f"❌ 不支持的格式: {format_type}. 支持的格式: {', '.join(unified_converter_manager.get_supported_formats())}"
        
        config_manager.update_conversion_settings(default_format=format_type)
        return f"✅ 默认输出格式已设置为: {format_type.upper()}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"

@mcp.tool()
async def quick_config_supported_formats(formats: List[str] = ["docx", "pptx"]) -> str:
    """
    快速设置支持的输出格式
    
    Args:
        formats: 支持的格式列表
        
    Returns:
        设置结果
        
    Use cases:
        - 支持所有格式: quick_config_supported_formats(["docx", "pptx"])
        - 仅支持DOCX: quick_config_supported_formats(["docx"])
    """
    try:
        available_formats = unified_converter_manager.get_supported_formats()
        invalid_formats = [f for f in formats if f not in available_formats]
        if invalid_formats:
            return f"❌ 不支持的格式: {', '.join(invalid_formats)}. 可用格式: {', '.join(available_formats)}"
        
        config_manager.update_conversion_settings(supported_formats=formats)
        return f"✅ 支持的格式已设置为: {', '.join([f.upper() for f in formats])}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"
    """
    快速设置 MD2DOCX 项目路径
    
    Args:
        project_path: MD2DOCX 项目的绝对路径
        
    Returns:
        设置结果
        
    Use cases:
        - 设置项目路径: quick_config_md2docx_path("/path/to/md2docx")
    """
    try:
        config_manager.update_server_settings(md2docx_project_path=project_path)
        return f"✅ MD2DOCX 项目路径已设置为: {project_path}"
    except Exception as e:
        return f"❌ 设置失败: {str(e)}"

# ===== 统一转换工具 =====

@mcp.tool()
async def convert_markdown(
    input_file: str,
    output_format: str = "docx",
    output_file: Optional[str] = None,
    template: Optional[str] = None,
    debug: Optional[bool] = None
) -> str:
    """
    统一的 Markdown 转换工具
    
    Args:
        input_file: 输入的 Markdown 文件路径
        output_format: 输出格式 (docx/pptx/both)
        output_file: 输出文件路径（可选）
        template: 模板文件路径（可选）
        debug: 调试模式
        
    Returns:
        转换结果信息
        
    Use cases:
        - 转换为DOCX: convert_markdown("/path/to/file.md", "docx")
        - 转换为PPTX: convert_markdown("/path/to/file.md", "pptx")
        - 同时转换: convert_markdown("/path/to/file.md", "both")
        - 使用模板: convert_markdown("/path/to/file.md", "pptx", template="custom.pptx")
    """
    
    try:
        if output_format.lower() == "both":
            # 转换为两种格式
            result = await unified_converter_manager.convert_multiple_formats(
                input_file=input_file,
                output_formats=["docx", "pptx"],
                debug=debug
            )
            
            if result['success'] > 0:
                success_formats = [r['format'] for r in result['results'] if r['success']]
                failed_formats = [r['format'] for r in result['results'] if not r['success']]
                
                message = f"""✅ 多格式转换完成!

📄 输入文件: {input_file}
📊 转换统计: 成功 {result['success']}, 失败 {result['failed']}
✅ 成功格式: {', '.join(success_formats).upper()}"""
                
                if failed_formats:
                    message += f"\n❌ 失败格式: {', '.join(failed_formats).upper()}"
                
                message += f"\n💬 消息: {result['message']}"
                
                # 添加详细结果
                message += "\n\n📋 详细结果:"
                for res in result['results']:
                    status = "✅" if res['success'] else "❌"
                    message += f"\n{status} {res['format'].upper()}: {res['output_file']}"
                    if not res['success']:
                        message += f" - {res['message']}"
                
                return message
            else:
                return f"❌ 多格式转换失败: {result['message']}"
        
        else:
            # 转换为单一格式
            if output_format.lower() not in unified_converter_manager.get_supported_formats():
                return f"❌ 不支持的格式: {output_format}. 支持的格式: {', '.join(unified_converter_manager.get_supported_formats())}"
            
            # 设置模板（如果指定）
            if template and output_format.lower() == "pptx":
                config_manager.update_pptx_settings(template_file=template)
            
            result = await unified_converter_manager.convert_single_file(
                input_file=input_file,
                output_format=output_format.lower(),
                output_file=output_file,
                debug=debug
            )
            
            if result['success']:
                message = f"""✅ {result['format'].upper()}转换成功!

📄 输入文件: {result['input_file']}
📄 输出文件: {result['output_file']}
📊 格式: {result['format'].upper()}
⏱️  转换耗时: {result['duration']}秒
📊 文件大小: {result['file_size']} bytes
💬 消息: {result['message']}"""
                
                # 添加调试信息
                if debug and result.get('debug_info'):
                    debug_info = result['debug_info']
                    message += f"""

🔍 调试信息:
- 绝对输出路径: {debug_info.get('absolute_output_path', 'N/A')}
- 当前工作目录: {debug_info.get('current_working_dir', 'N/A')}
- 项目工作目录: {debug_info.get('project_working_dir', 'N/A')}"""
                    
                    if debug_info.get('subprocess_result'):
                        subprocess_info = debug_info['subprocess_result']
                        message += f"""
- 执行命令: {subprocess_info.get('command', 'N/A')}
- 返回码: {subprocess_info.get('return_code', 'N/A')}"""
                        if subprocess_info.get('template_used'):
                            message += f"\n- 使用模板: {subprocess_info['template_used']}"
                
                return message
            else:
                return f"""❌ {result['format'].upper()}转换失败!

📄 输入文件: {result['input_file']}
📄 输出文件: {result['output_file']}
📊 格式: {result['format'].upper()}
❌ 错误信息: {result['message']}"""
    
    except Exception as e:
        return f"❌ 转换过程出错: {str(e)}"

@mcp.tool()
async def batch_convert_markdown(
    input_dir: str,
    output_formats: List[str] = ["docx"],
    output_dir: Optional[str] = None,
    file_pattern: str = "*.md",
    parallel_jobs: Optional[int] = None
) -> str:
    """
    批量转换目录中的 Markdown 文件为多种格式
    
    Args:
        input_dir: 输入目录路径
        output_formats: 输出格式列表 (["docx"], ["pptx"], ["docx", "pptx"])
        output_dir: 输出目录路径（可选，使用配置默认值）
        file_pattern: 文件匹配模式（默认 "*.md"）
        parallel_jobs: 并行任务数（可选，使用配置默认值）
        
    Returns:
        批量转换结果信息
        
    Use cases:
        - 批量转换DOCX: batch_convert_markdown("/path/to/folder", ["docx"])
        - 批量转换PPTX: batch_convert_markdown("/path/to/folder", ["pptx"])
        - 批量转换多格式: batch_convert_markdown("/path/to/folder", ["docx", "pptx"])
        - 自定义模式: batch_convert_markdown("/input", ["docx"], file_pattern="*.markdown")
    """
    
    try:
        # 验证输出格式
        supported_formats = unified_converter_manager.get_supported_formats()
        invalid_formats = [f for f in output_formats if f not in supported_formats]
        if invalid_formats:
            return f"❌ 不支持的格式: {', '.join(invalid_formats)}. 支持的格式: {', '.join(supported_formats)}"
        
        # 临时更新并行任务数（如果指定）
        if parallel_jobs is not None:
            original_jobs = config_manager.batch_settings.parallel_jobs
            config_manager.update_batch_settings(parallel_jobs=parallel_jobs)
        
        result = await unified_converter_manager.batch_convert(
            input_dir=input_dir,
            output_formats=output_formats,
            output_dir=output_dir,
            file_pattern=file_pattern
        )
        
        # 恢复原始并行任务数
        if parallel_jobs is not None:
            config_manager.update_batch_settings(parallel_jobs=original_jobs)
        
        if result['total'] > 0:
            success_rate = (result['success'] / result['total']) * 100
            
            summary = f"""📊 批量转换完成!

📁 输入目录: {input_dir}
📁 输出目录: {output_dir or config_manager.conversion_settings.output_dir}
🔍 文件模式: {file_pattern}
📊 输出格式: {', '.join([f.upper() for f in output_formats])}

📈 转换统计:
- 总转换任务: {result['total']}
- 成功转换: {result['success']}
- 转换失败: {result['failed']}
- 成功率: {success_rate:.1f}%

💬 消息: {result['message']}"""
            
            # 按格式统计结果
            format_stats = {}
            for res in result['results']:
                fmt = res['format']
                if fmt not in format_stats:
                    format_stats[fmt] = {'success': 0, 'failed': 0}
                if res['success']:
                    format_stats[fmt]['success'] += 1
                else:
                    format_stats[fmt]['failed'] += 1
            
            if format_stats:
                summary += "\n\n📊 格式统计:"
                for fmt, stats in format_stats.items():
                    total_fmt = stats['success'] + stats['failed']
                    success_rate_fmt = (stats['success'] / total_fmt) * 100 if total_fmt > 0 else 0
                    summary += f"\n- {fmt.upper()}: 成功 {stats['success']}, 失败 {stats['failed']} (成功率: {success_rate_fmt:.1f}%)"
            
            # 添加失败详情（如果有失败的文件）
            if result['failed'] > 0:
                failed_results = [res for res in result['results'] if not res['success']]
                if len(failed_results) <= 10:  # 只显示前10个失败的
                    summary += "\n\n❌ 失败的转换:"
                    for res in failed_results:
                        summary += f"\n- {res['format'].upper()}: {res['input_file']} - {res['message']}"
                else:
                    summary += f"\n\n❌ 有 {len(failed_results)} 个转换失败，详情请查看日志文件"
            
            return summary
        else:
            return f"⚠️  批量转换结果: {result['message']}"
    
    except Exception as e:
        return f"❌ 批量转换过程出错: {str(e)}"

@mcp.tool()
async def convert_with_template(
    input_file: str,
    output_format: str,
    template_file: str,
    output_file: Optional[str] = None
) -> str:
    """
    使用指定模板转换文件
    
    Args:
        input_file: 输入的 Markdown 文件路径
        output_format: 输出格式 (docx/pptx)
        template_file: 模板文件路径
        output_file: 输出文件路径（可选）
        
    Returns:
        转换结果信息
        
    Use cases:
        - PPTX模板转换: convert_with_template("/path/to/file.md", "pptx", "custom.pptx")
        - DOCX模板转换: convert_with_template("/path/to/file.md", "docx", "template.docx")
    """
    
    try:
        # 验证格式
        if output_format not in unified_converter_manager.get_supported_formats():
            return f"❌ 不支持的格式: {output_format}"
        
        # 验证模板文件
        template_path = Path(template_file)
        if not template_path.is_absolute():
            # 相对路径，相对于对应的项目目录
            if output_format == "pptx":
                project_path = Path(config_manager.server_settings.md2pptx_project_path)
                if not project_path.is_absolute():
                    mcp_server_dir = Path(__file__).parent
                    project_path = mcp_server_dir / project_path
                template_path = project_path / template_file
            # DOCX 模板处理可以在这里添加
        
        if not template_path.exists():
            return f"❌ 模板文件不存在: {template_path}"
        
        # 设置模板配置
        if output_format == "pptx":
            config_manager.update_pptx_settings(template_file=template_file)
        elif output_format == "docx":
            config_manager.update_docx_settings(template_file=template_file)
        
        # 执行转换
        result = await unified_converter_manager.convert_single_file(
            input_file=input_file,
            output_format=output_format,
            output_file=output_file,
            debug=True  # 启用调试以显示模板信息
        )
        
        if result['success']:
            message = f"""✅ 模板转换成功!

📄 输入文件: {result['input_file']}
📄 输出文件: {result['output_file']}
📊 格式: {result['format'].upper()}
🎨 模板: {template_file}
⏱️  转换耗时: {result['duration']}秒
💬 消息: {result['message']}"""
            
            return message
        else:
            return f"""❌ 模板转换失败!

📄 输入文件: {result['input_file']}
📊 格式: {result['format'].upper()}
🎨 模板: {template_file}
❌ 错误信息: {result['message']}"""
    
    except Exception as e:
        return f"❌ 模板转换过程出错: {str(e)}"

@mcp.tool()
async def convert_md_to_docx(
    input_file: str,
    output_file: Optional[str] = None,
    debug: Optional[bool] = None
) -> str:
    """
    将单个 Markdown 文件转换为 DOCX 格式（向后兼容工具）
    
    Args:
        input_file: 输入的 Markdown 文件路径
        output_file: 输出的 DOCX 文件路径（可选，自动生成）
        debug: 是否启用调试模式（可选，使用配置默认值）
        
    Returns:
        转换结果信息
        
    Use cases:
        - 基本转换: convert_md_to_docx("/path/to/file.md")
        - 指定输出: convert_md_to_docx("/path/to/file.md", "/path/to/output.docx")
        - 调试模式: convert_md_to_docx("/path/to/file.md", debug=True)
    """
    
    try:
        # 使用统一转换器的 DOCX 转换功能
        result = await unified_converter_manager.convert_single_file(
            input_file=input_file,
            output_format="docx",
            output_file=output_file,
            debug=debug
        )
        
        if result['success']:
            message = f"""✅ 转换成功!

📄 输入文件: {result['input_file']}
📄 输出文件: {result['output_file']}
⏱️  转换耗时: {result['duration']}秒
📊 文件大小: {result['file_size']} bytes
💬 消息: {result['message']}"""
            
            # 添加调试信息
            if debug and result.get('debug_info'):
                debug_info = result['debug_info']
                message += f"""

🔍 调试信息:
- 绝对输出路径: {debug_info.get('absolute_output_path', 'N/A')}
- 当前工作目录: {debug_info.get('current_working_dir', 'N/A')}
- MD2DOCX工作目录: {debug_info.get('md2docx_working_dir', 'N/A')}"""
                
                if debug_info.get('subprocess_result'):
                    subprocess_info = debug_info['subprocess_result']
                    message += f"""
- 执行命令: {subprocess_info.get('command', 'N/A')}
- 返回码: {subprocess_info.get('return_code', 'N/A')}
- 标准输出: {subprocess_info.get('stdout', 'N/A')[:200]}...
- 标准错误: {subprocess_info.get('stderr', 'N/A')[:200]}..."""
            
            return message
        else:
            return f"""❌ 转换失败!

📄 输入文件: {result['input_file']}
📄 输出文件: {result['output_file']}
❌ 错误信息: {result['message']}"""
    
    except Exception as e:
        return f"❌ 转换过程出错: {str(e)}"

@mcp.tool()
async def batch_convert_md_to_docx(
    input_dir: str,
    output_dir: Optional[str] = None,
    file_pattern: str = "*.md",
    parallel_jobs: Optional[int] = None
) -> str:
    """
    批量转换目录中的 Markdown 文件为 DOCX 格式（向后兼容工具）
    
    Args:
        input_dir: 输入目录路径
        output_dir: 输出目录路径（可选，使用配置默认值）
        file_pattern: 文件匹配模式（默认 "*.md"）
        parallel_jobs: 并行任务数（可选，使用配置默认值）
        
    Returns:
        批量转换结果信息
        
    Use cases:
        - 基本批量转换: batch_convert_md_to_docx("/path/to/markdown/files")
        - 指定输出目录: batch_convert_md_to_docx("/input", "/output")
        - 自定义模式: batch_convert_md_to_docx("/input", file_pattern="*.markdown")
        - 设置并行数: batch_convert_md_to_docx("/input", parallel_jobs=8)
    """
    
    try:
        # 临时更新并行任务数（如果指定）
        if parallel_jobs is not None:
            original_jobs = config_manager.batch_settings.parallel_jobs
            config_manager.update_batch_settings(parallel_jobs=parallel_jobs)
        
        # 使用统一转换器的批量转换功能，只转换 DOCX
        result = await unified_converter_manager.batch_convert(
            input_dir=input_dir,
            output_formats=["docx"],
            output_dir=output_dir,
            file_pattern=file_pattern
        )
        
        # 恢复原始并行任务数
        if parallel_jobs is not None:
            config_manager.update_batch_settings(parallel_jobs=original_jobs)
        
        if result['total'] > 0:
            success_rate = (result['success'] / result['total']) * 100
            
            summary = f"""📊 批量转换完成!

📁 输入目录: {input_dir}
📁 输出目录: {output_dir or config_manager.conversion_settings.output_dir}
🔍 文件模式: {file_pattern}

📈 转换统计:
- 总文件数: {result['total']}
- 成功转换: {result['success']}
- 转换失败: {result['failed']}
- 成功率: {success_rate:.1f}%

💬 消息: {result['message']}"""
            
            # 添加详细结果（如果有失败的文件）
            if result['failed'] > 0:
                summary += "\n\n❌ 失败的文件:"
                for res in result['results']:
                    if not res['success']:
                        summary += f"\n- {res['input_file']}: {res['message']}"
            
            return summary
        else:
            return f"⚠️  批量转换结果: {result['message']}"
    
    except Exception as e:
        return f"❌ 批量转换过程出错: {str(e)}"

@mcp.tool()
async def list_markdown_files(
    directory: str,
    recursive: bool = False
) -> str:
    """
    列出目录中的 Markdown 文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归搜索子目录
        
    Returns:
        文件列表信息
        
    Use cases:
        - 列出当前目录: list_markdown_files("/path/to/directory")
        - 递归搜索: list_markdown_files("/path/to/directory", recursive=True)
    """
    
    try:
        result = await unified_converter_manager.list_markdown_files(
            directory=directory,
            recursive=recursive
        )
        
        if 'error' in result:
            return f"❌ 列出文件失败: {result['error']}"
        
        if result['count'] == 0:
            return f"""📁 目录扫描结果

📂 目录: {result['directory']}
🔍 递归搜索: {'是' if result['recursive'] else '否'}
📄 找到文件: 0 个

⚠️  未找到支持的 Markdown 文件"""
        
        file_list = "\n".join([f"- {f}" for f in result['files'][:20]])  # 限制显示前20个
        
        summary = f"""📁 目录扫描结果

📂 目录: {result['directory']}
🔍 递归搜索: {'是' if result['recursive'] else '否'}
📄 找到文件: {result['count']} 个

📋 文件列表:
{file_list}"""
        
        if result['count'] > 20:
            summary += f"\n... 还有 {result['count'] - 20} 个文件未显示"
        
        return summary
    
    except Exception as e:
        return f"❌ 列出文件过程出错: {str(e)}"

@mcp.tool()
async def get_conversion_status() -> str:
    """
    获取转换器状态和配置信息
    
    Returns:
        转换器状态信息
        
    Use cases:
        - 检查状态: get_conversion_status()
    """
    
    try:
        # 检查 md2docx 项目路径
        md2docx_path = Path(config_manager.server_settings.md2docx_project_path)
        
        # 如果是相对路径，相对于MCP服务器目录
        if not md2docx_path.is_absolute():
            mcp_server_dir = Path(__file__).parent  # md2docx-mcp-server 目录
            md2docx_path = mcp_server_dir / md2docx_path
        
        md2docx_exists = md2docx_path.exists()
        
        # 检查 md2pptx 项目路径
        md2pptx_path = Path(config_manager.server_settings.md2pptx_project_path)
        
        # 如果是相对路径，相对于MCP服务器目录
        if not md2pptx_path.is_absolute():
            mcp_server_dir = Path(__file__).parent  # md2docx-mcp-server 目录
            md2pptx_path = mcp_server_dir / md2pptx_path
        
        md2pptx_exists = md2pptx_path.exists()
        
        # 检查输出目录
        output_dir = Path(config_manager.conversion_settings.output_dir)
        output_dir_exists = output_dir.exists()
        
        # 检查模板文件
        pptx_template = config_manager.pptx_settings.template_file
        pptx_template_exists = False
        if pptx_template:
            template_path = md2pptx_path / pptx_template
            pptx_template_exists = template_path.exists()
        
        status = f"""🔍 统一转换器状态

🖥️  服务器信息:
- 服务器名称: MD2DOCX-Converter (统一版)
- Python 版本: {sys.version.split()[0]}
- 工作目录: {Path.cwd()}

📁 项目路径检查:
- MD2DOCX 项目路径: {md2docx_path}
  状态: {'✅ 存在' if md2docx_exists else '❌ 不存在'}
- MD2PPTX 项目路径: {md2pptx_path}
  状态: {'✅ 存在' if md2pptx_exists else '❌ 不存在'}
- 输出目录: {output_dir}
  状态: {'✅ 存在' if output_dir_exists else '⚠️  不存在（将自动创建）'}

📊 格式支持:
- 支持的格式: {', '.join([f.upper() for f in config_manager.conversion_settings.supported_formats])}
- 默认格式: {config_manager.conversion_settings.default_format.upper()}
- 可用转换器: {', '.join([f.upper() for f in unified_converter_manager.get_supported_formats()])}

⚙️  当前配置:
- 调试模式: {'✅ 启用' if config_manager.conversion_settings.debug_mode else '❌ 禁用'}
- 转换方式: {'子进程调用' if config_manager.server_settings.use_subprocess else 'Python 模块导入'}
- 并行任务数: {config_manager.batch_settings.parallel_jobs}
- 支持文件类型: {', '.join(config_manager.file_settings.supported_extensions)}

🎨 模板配置:
- PPTX 模板: {pptx_template or '未设置'}
  状态: {'✅ 存在' if pptx_template_exists else '❌ 不存在' if pptx_template else '⚠️  未配置'}
- DOCX 模板: {config_manager.docx_settings.template_file or '默认'}

🔧 可用工具:
- convert_markdown: 统一转换工具 (支持 DOCX/PPTX)
- batch_convert_markdown: 批量转换 (支持多格式)
- convert_with_template: 模板转换
- convert_md_to_docx: 单独DOCX转换 (向后兼容)
- batch_convert_md_to_docx: 批量DOCX转换 (向后兼容)
- list_markdown_files: 列出 Markdown 文件
- configure_converter: 配置管理
- get_conversion_status: 状态检查"""
        
        # 添加警告信息
        warnings = []
        if not md2docx_exists:
            warnings.append("MD2DOCX 项目路径不存在，DOCX转换将不可用")
        if not md2pptx_exists:
            warnings.append("MD2PPTX 项目路径不存在，PPTX转换将不可用")
        if pptx_template and not pptx_template_exists:
            warnings.append(f"PPTX模板文件不存在: {pptx_template}")
        
        if warnings:
            status += f"\n\n⚠️  警告:"
            for warning in warnings:
                status += f"\n- {warning}"
        
        return status
    
    except Exception as e:
        return f"❌ 获取状态失败: {str(e)}"

# ===== MCP PROMPTS - Q CLI 使用指导 =====

@mcp.prompt()
def md2pptx_content_generator(
    topic: str = "业务演示",
    presentation_type: str = "business",
    slide_count: str = "medium",
    audience: str = "管理层"
) -> str:
    """md2pptx 内容生成器
    
    直接生成符合 md2pptx 模板要求的完整 Markdown 演示内容。
    输出可以直接用于 md2pptx 转换，无需额外修改。
    """
    
    # 根据演示类型确定设置
    type_configs = {
        "business": {
            "pageTitleSize": 24,
            "sectionTitleSize": 30,
            "baseTextSize": 20,
            "focus": "数据驱动、结果导向、ROI分析",
            "tone": "专业、简洁、有说服力"
        },
        "academic": {
            "pageTitleSize": 22,
            "sectionTitleSize": 28,
            "baseTextSize": 18,
            "focus": "理论框架、研究方法、实证分析",
            "tone": "严谨、客观、逻辑清晰"
        },
        "technical": {
            "pageTitleSize": 20,
            "sectionTitleSize": 26,
            "baseTextSize": 16,
            "focus": "技术架构、实现细节、代码示例",
            "tone": "精确、详细、实用性强"
        },
        "creative": {
            "pageTitleSize": 26,
            "sectionTitleSize": 32,
            "baseTextSize": 22,
            "focus": "创意概念、视觉冲击、情感连接",
            "tone": "生动、有趣、引人入胜"
        }
    }
    
    # 根据幻灯片数量确定结构
    count_configs = {
        "short": {"slides": "5-8", "sections": "2-3", "depth": "概览性"},
        "medium": {"slides": "10-15", "sections": "3-5", "depth": "平衡详细"},
        "long": {"slides": "20-30", "sections": "5-8", "depth": "深入详细"}
    }
    
    config = type_configs.get(presentation_type, type_configs["business"])
    structure = count_configs.get(slide_count, count_configs["medium"])
    
    # 根据主题生成具体的演示内容
    if "AI" in topic or "人工智能" in topic:
        sample_content = f"""template: Martin Template.pptx
pageTitleSize: {config['pageTitleSize']}
sectionTitleSize: {config['sectionTitleSize']}
baseTextSize: {config['baseTextSize']}
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00

# {topic}
智能化转型的战略机遇

## 项目背景

### 市场机遇分析
* AI技术快速发展，应用场景不断扩大
* 行业数字化转型需求迫切
* 竞争对手AI布局相对滞后
* 政策环境支持AI创新发展

### 技术趋势洞察
* 大语言模型技术日趋成熟
* 多模态AI应用前景广阔
* 边缘计算与AI深度融合
* AI安全与可解释性受到重视

## 项目方案

### 核心价值主张
* 提升业务效率50%以上
* 降低运营成本30%
* 增强客户体验满意度
* 构建智能化竞争优势

### 技术架构设计
<!-- md2pptx: cardlayout: horizontal -->

#### 数据层
* 数据采集与清洗
* 特征工程优化
* 数据安全保障

#### 算法层
* 机器学习模型
* 深度学习框架
* 模型训练与优化

#### 应用层
* 智能决策支持
* 自动化流程
* 用户交互界面

### 实施路线图
|阶段|时间|关键任务|里程碑|
|:---|:---|:---|:---|
|第一阶段|1-3月|基础设施建设|平台搭建完成|
|第二阶段|4-6月|核心算法开发|模型训练完成|
|第三阶段|7-9月|系统集成测试|功能验证通过|
|第四阶段|10-12月|上线部署优化|正式投产运行|

## 投资回报

### 成本效益分析
* 项目总投资：500万元
* 预期年收益：800万元
* 投资回收期：9个月
* 三年净现值：1200万元

### 风险评估与应对
<!-- md2pptx: cardlayout: vertical -->

#### 技术风险
* 算法性能不达预期
* 数据质量问题
* 系统集成困难

#### 市场风险
* 竞争对手快速跟进
* 客户接受度不高
* 监管政策变化

#### 应对策略
* 建立技术专家团队
* 制定详细测试计划
* 加强市场调研分析

## 团队与资源

### 核心团队构成
* 项目总监：1名（战略规划）
* 技术负责人：2名（架构设计）
* 算法工程师：5名（模型开发）
* 产品经理：2名（需求管理）

### 资源需求清单
* 硬件设备：GPU服务器集群
* 软件工具：开发框架与平台
* 数据资源：训练数据集
* 外部合作：技术咨询服务

## 总结与建议

### 项目优势总结
* 技术方案先进可行
* 市场前景广阔明确
* 团队经验丰富专业
* 投资回报预期良好

### 下一步行动计划
* 立即启动项目立项流程
* 组建核心项目团队
* 开展详细需求调研
* 制定具体实施计划

### 支持需求
* 高层领导全力支持
* 充足的资金预算保障
* 跨部门协作配合
* 外部专家技术指导"""
    
    elif "数字化" in topic or "转型" in topic:
        sample_content = f"""template: Martin Template.pptx
pageTitleSize: {config['pageTitleSize']}
sectionTitleSize: {config['sectionTitleSize']}
baseTextSize: {config['baseTextSize']}
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00

# {topic}
企业未来发展蓝图

## 背景与挑战

### 市场环境分析
* 数字化浪潮席卷各行各业
* 客户期望快速变化升级
* 竞争对手加速数字化布局
* 传统业务模式面临冲击

### 内部现状评估
* 技术基础设施相对落后
* 数据孤岛现象严重
* 员工数字化技能待提升
* 业务流程自动化程度低

## 转型战略

### 战略目标设定
* 提升客户体验满意度40%
* 优化运营效率提升30%
* 创新业务模式拓展
* 增强市场竞争力

### 核心转型举措
<!-- md2pptx: cardlayout: horizontal -->

#### 技术升级
* 云平台建设
* 数据中台构建
* AI/ML能力建设

#### 流程优化
* 业务流程重塑
* 自动化部署
* 敏捷开发模式

#### 人才培养
* 数字化技能培训
* 组织架构调整
* 创新文化建设

## 实施路径

### 分阶段实施计划
|阶段|时间|重点任务|预期成果|
|:---|:---|:---|:---|
|第一阶段|Q1-Q2|基础设施建设|技术平台就绪|
|第二阶段|Q3-Q4|业务流程改造|效率提升30%|
|第三阶段|次年|创新业务拓展|新收入来源|

### 关键成功因素
* 高层领导全力支持
* 充足的资源投入
* 全员参与和配合
* 持续的监控和调整

## 预期效益

### 量化收益分析
* 运营成本降低25%
* 客户满意度提升40%
* 新业务收入占比达20%
* 市场响应速度提升50%

### 风险控制措施
* 分阶段实施降低风险
* 建立监控预警机制
* 制定应急预案
* 加强变更管理

## 行动计划

### 立即启动事项
* 成立数字化转型委员会
* 启动技术平台选型
* 制定详细实施计划
* 开展员工培训项目

### 资源配置需求
* 项目预算：1000万元
* 专职团队：20人
* 外部咨询：技术专家
* 时间周期：18个月"""
    
    else:
        # 通用模板
        sample_content = f"""template: Martin Template.pptx
pageTitleSize: {config['pageTitleSize']}
sectionTitleSize: {config['sectionTitleSize']}
baseTextSize: {config['baseTextSize']}
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00

# {topic}
专业演示方案

## 概述

### 项目背景
* 市场需求分析
* 行业发展趋势
* 竞争环境评估
* 机遇与挑战并存

### 目标设定
* 核心目标明确
* 关键指标量化
* 成功标准定义
* 预期效果评估

## 解决方案

### 方案概述
* 核心理念阐述
* 主要组成部分
* 技术路线选择
* 创新点突出

### 实施计划
<!-- md2pptx: cardlayout: horizontal -->

#### 第一阶段
* 前期准备工作
* 资源配置到位
* 团队组建完成

#### 第二阶段
* 核心功能开发
* 系统集成测试
* 用户反馈收集

#### 第三阶段
* 正式上线部署
* 运营优化调整
* 效果评估总结

## 预期成果

### 效益分析
|类型|指标|当前值|目标值|提升幅度|
|:---|:---|---:|---:|---:|
|效率|处理速度|100/h|150/h|+50%|
|成本|运营费用|$10K|$8K|-20%|
|质量|满意度|80%|95%|+15%|

### 成功保障
* 专业团队支持
* 充足资源投入
* 完善监控体系
* 持续优化改进

## 总结建议

### 关键要点
* 方案可行性强
* 预期收益明显
* 风险控制得当
* 实施条件具备

### 下一步行动
* 获得决策层批准
* 启动项目实施
* 建立项目团队
* 制定详细计划"""
    
    return f"""# 🎯 md2pptx 内容生成器

## 📋 生成参数
- **主题**: {topic}
- **类型**: {presentation_type.title()}
- **受众**: {audience}
- **规模**: {structure['slides']} 张幻灯片

## 📝 生成的 Markdown 内容

以下是完整的 md2pptx 兼容 Markdown 代码，可以直接保存为 .md 文件并转换：

```markdown
{sample_content}
```

## ✅ 格式验证

该内容已确保：
- ✅ 包含完整的元数据头部
- ✅ 使用正确的标题层次结构
- ✅ 每页要点数量适中 (3-6个)
- ✅ 包含高级功能 (卡片、表格)
- ✅ 适合 {audience} 受众
- ✅ 体现 {config['tone']} 风格

## 🚀 使用方法

1. **复制内容**: 复制上面的 Markdown 代码
2. **保存文件**: 保存为 `{topic.replace(' ', '_')}.md`
3. **转换 PPTX**: 使用 `convert_markdown` 工具转换
4. **验证结果**: 检查生成的演示文稿

**内容已准备就绪，可以直接使用！** 🎉
"""

@mcp.prompt()
def md2docx_conversion_guide(
    task_type: str = "single",
    input_path: str = "/path/to/your/file.md",
    output_format: str = "docx"
) -> str:
    """统一转换指南 - 智能转换助手
    
    为用户提供基于任务类型和输出格式的智能转换建议和具体执行命令。
    支持 DOCX、PPTX 和多格式转换。
    """
    
    # 获取当前配置
    config = config_manager
    md2docx_configured = Path(config.server_settings.md2docx_project_path).exists()
    md2pptx_configured = Path(config.server_settings.md2pptx_project_path).exists()
    
    # 任务类型分析
    task_lower = task_type.lower()
    format_lower = output_format.lower()
    
    # 检测任务类型
    is_batch = any(keyword in task_lower for keyword in ['batch', 'bulk', 'multiple', 'folder', 'directory', '批量', '多个', '文件夹'])
    is_config = any(keyword in task_lower for keyword in ['config', 'setup', 'configure', 'setting', '配置', '设置'])
    is_debug = any(keyword in task_lower for keyword in ['debug', 'error', 'problem', 'issue', '调试', '错误', '问题'])
    is_template = any(keyword in task_lower for keyword in ['template', 'theme', 'style', '模板', '主题', '样式'])
    is_multi_format = any(keyword in task_lower for keyword in ['multi', 'both', 'all', 'multiple', '多格式', '同时'])
    
    # 格式检测
    is_pptx = format_lower in ['pptx', 'powerpoint', 'presentation', '演示', '幻灯片']
    is_both = format_lower in ['both', 'all', 'multi', '两种', '全部', '多格式']
    
    # 智能推荐
    if not md2docx_configured and not md2pptx_configured:
        primary_recommendation = "首次配置"
        primary_command = f'get_conversion_status()'
        primary_reason = "转换器项目路径未配置，需要先检查系统状态"
    elif is_config:
        primary_recommendation = "配置管理"
        primary_command = f'configure_converter("show", "all")'
        primary_reason = "配置相关任务，建议先查看当前配置状态"
    elif is_debug:
        primary_recommendation = "问题诊断"
        primary_command = f'validate_markdown_file("{input_path}")'
        primary_reason = "问题诊断任务，建议先验证文件格式"
    elif is_template:
        if is_pptx:
            primary_recommendation = "PPTX模板转换"
            primary_command = f'convert_with_template("{input_path}", "pptx", "Martin Template.pptx")'
            primary_reason = "模板转换任务，使用专业PPTX模板"
        else:
            primary_recommendation = "模板转换"
            primary_command = f'convert_with_template("{input_path}", "docx", "template.docx")'
            primary_reason = "模板转换任务，使用自定义模板"
    elif is_multi_format or is_both:
        if is_batch:
            primary_recommendation = "批量多格式转换"
            primary_command = f'batch_convert_markdown("{input_path}", ["docx", "pptx"])'
            primary_reason = "批量多格式任务，同时生成DOCX和PPTX文件"
        else:
            primary_recommendation = "多格式转换"
            primary_command = f'convert_markdown("{input_path}", "both")'
            primary_reason = "多格式转换任务，同时生成两种格式"
    elif is_batch:
        if is_pptx:
            primary_recommendation = "批量PPTX转换"
            primary_command = f'batch_convert_markdown("{input_path}", ["pptx"])'
            primary_reason = "批量PPTX转换任务，生成演示文稿"
        else:
            primary_recommendation = "批量DOCX转换"
            primary_command = f'batch_convert_markdown("{input_path}", ["docx"])'
            primary_reason = "批量DOCX转换任务，生成文档"
    elif is_pptx:
        primary_recommendation = "PPTX转换"
        primary_command = f'convert_markdown("{input_path}", "pptx")'
        primary_reason = "PPTX转换任务，生成演示文稿"
    else:
        primary_recommendation = "DOCX转换"
        primary_command = f'convert_markdown("{input_path}", "docx")'
        primary_reason = "DOCX转换任务，生成文档"
    
    # 构建特征分析
    features = []
    if is_batch:
        features.append("批量处理")
    else:
        features.append("单文件")
    
    if is_pptx:
        features.append("PPTX格式")
    elif is_both:
        features.append("多格式")
    else:
        features.append("DOCX格式")
    
    if is_template:
        features.append("模板转换")
    if is_config:
        features.append("配置管理")
    if is_debug:
        features.append("问题诊断")
    
    if len(features) == 1:
        features.append("标准转换")
    
    features_display = " | ".join(features)
    
    return f"""# 📄 统一转换智能助手

## 📊 任务分析
**任务类型**: {task_type}
**输入路径**: {input_path}
**输出格式**: {output_format}
**任务特征**: {features_display}
**MD2DOCX 配置状态**: {'✅ 已配置' if md2docx_configured else '❌ 未配置'}
**MD2PPTX 配置状态**: {'✅ 已配置' if md2pptx_configured else '❌ 未配置'}
**当前输出目录**: {config.conversion_settings.output_dir}

## 🎯 AI 推荐方案 (优先使用)

### ⭐ 推荐: {primary_recommendation}
**分析**: {primary_reason}

**🚀 立即执行**:
```
{primary_command}
```

## 🔧 统一转换工具矩阵

### 📄 文档转换 (新功能)
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| DOCX转换 | convert_markdown | `convert_markdown("/path/to/file.md", "docx")` |
| PPTX转换 | convert_markdown | `convert_markdown("/path/to/file.md", "pptx")` |
| 多格式转换 | convert_markdown | `convert_markdown("/path/to/file.md", "both")` |
| 批量DOCX | batch_convert_markdown | `batch_convert_markdown("/path/to/folder", ["docx"])` |
| 批量PPTX | batch_convert_markdown | `batch_convert_markdown("/path/to/folder", ["pptx"])` |
| 批量多格式 | batch_convert_markdown | `batch_convert_markdown("/path/to/folder", ["docx", "pptx"])` |

### 🎨 模板转换
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| PPTX模板 | convert_with_template | `convert_with_template("/path/to/file.md", "pptx", "Martin Template.pptx")` |
| 自定义模板 | convert_with_template | `convert_with_template("/path/to/file.md", "pptx", "custom.pptx")` |
| DOCX模板 | convert_with_template | `convert_with_template("/path/to/file.md", "docx", "template.docx")` |

### 📁 文件管理
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| 列出文件 | list_markdown_files | `list_markdown_files("/path/to/folder")` |
| 递归搜索 | list_markdown_files | `list_markdown_files("/path/to/folder", recursive=True)` |
| 验证文件 | validate_markdown_file | `validate_markdown_file("/path/to/file.md")` |

### ⚙️ 配置管理
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| 查看状态 | get_conversion_status | `get_conversion_status()` |
| 查看配置 | configure_converter | `configure_converter("show", "all")` |
| 设置默认格式 | quick_config_default_format | `quick_config_default_format("pptx")` |
| 设置PPTX模板 | quick_config_pptx_template | `quick_config_pptx_template("business.pptx")` |
| 设置输出目录 | quick_config_output_dir | `quick_config_output_dir("/path/to/output")` |
| 启用调试 | quick_config_debug_mode | `quick_config_debug_mode(True)` |

### 🔄 向后兼容工具
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| 单独DOCX转换 | convert_md_to_docx | `convert_md_to_docx("/path/to/file.md")` |
| 批量DOCX转换 | batch_convert_md_to_docx | `batch_convert_md_to_docx("/path/to/folder")` |

## 🤔 决策树

```
转换需求分析
    ↓
首次使用? → Yes → get_conversion_status() ✅
    ↓ No
需要模板? → Yes → convert_with_template() ✅
    ↓ No
多种格式? → Yes → convert_markdown("both") 或 batch_convert_markdown(["docx", "pptx"]) ✅
    ↓ No
批量转换? → Yes → batch_convert_markdown() ✅
    ↓ No
PPTX格式? → Yes → convert_markdown("pptx") ✅
    ↓ No
DOCX格式 → convert_markdown("docx") ✅
```

## 💡 使用建议

### 📄 首次使用流程
1. **检查系统状态**: `get_conversion_status()`
2. **设置默认格式**: `quick_config_default_format("pptx")`
3. **测试转换**: `convert_markdown("/path/to/test.md", "both")`
4. **检查结果**: 验证生成的 DOCX 和 PPTX 文件

### 🚀 批量处理流程
1. **查看文件**: `list_markdown_files("/path/to/folder")`
2. **设置并行数**: `quick_config_parallel_jobs(8)`
3. **执行批量转换**: `batch_convert_markdown("/path/to/folder", ["docx", "pptx"])`
4. **监控进度**: 查看转换日志和结果

### 🎨 模板使用流程
1. **设置PPTX模板**: `quick_config_pptx_template("Martin Template.pptx")`
2. **模板转换**: `convert_with_template("/path/to/file.md", "pptx", "Martin Template.pptx")`
3. **验证输出**: 检查生成的专业演示文稿

### 🔧 问题诊断流程
1. **验证文件**: `validate_markdown_file("/path/to/problem.md")`
2. **启用调试**: `quick_config_debug_mode(True)`
3. **重新转换**: `convert_markdown("/path/to/problem.md", "docx", debug=True)`
4. **分析错误**: 根据详细日志调整配置

## 🎯 快速开始示例

```python
# 📄 统一转换 (推荐)
convert_markdown("/Users/username/Documents/report.md", "pptx")
convert_markdown("/Users/username/Documents/report.md", "both")

# 📁 批量多格式转换
batch_convert_markdown("/Users/username/Documents/markdown-files/", ["docx", "pptx"])

# 🎨 模板转换
convert_with_template("/Users/username/Documents/presentation.md", "pptx", "Martin Template.pptx")

# ⚙️ 配置管理
quick_config_default_format("pptx")
quick_config_pptx_template("business.pptx")

# 🔧 问题诊断
validate_markdown_file("/Users/username/Documents/problem.md")
```

## ⚠️ 重要提示

- 🆕 **新功能**: 现在支持 DOCX 和 PPTX 双格式转换
- 🎨 **模板支持**: 内置专业 PPTX 模板，支持自定义
- ⚡ **性能提升**: 支持多格式并行转换
- 🔄 **向后兼容**: 所有旧工具仍然可用
- 📊 **智能推荐**: 根据内容特征推荐最佳格式

**🚀 准备开始转换？使用上面的 AI 推荐方案！**
"""
    
    if len(features) == 1:
        features.append("标准转换")
    
    features_display = " | ".join(features)
    
    return f"""# 📄 MD2DOCX 智能转换助手

## 📊 任务分析
**任务类型**: {task_type}
**输入路径**: {input_path}
**任务特征**: {features_display}
**MD2DOCX 配置状态**: {'✅ 已配置' if md2docx_configured else '❌ 未配置'}
**当前输出目录**: {config.conversion_settings.output_dir}

## 🎯 AI 推荐方案 (优先使用)

### ⭐ 推荐: {primary_recommendation}
**分析**: {primary_reason}

**🚀 立即执行**:
```
{primary_command}
```

## 🔧 转换工具矩阵

### 📄 文档转换
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| 单文件转换 | convert_md_to_docx | `convert_md_to_docx("/path/to/file.md")` |
| 指定输出文件 | convert_md_to_docx | `convert_md_to_docx("/path/to/file.md", "/path/to/output.docx")` |
| 调试模式转换 | convert_md_to_docx | `convert_md_to_docx("/path/to/file.md", debug=True)` |
| 批量转换 | batch_convert_md_to_docx | `batch_convert_md_to_docx("/path/to/folder")` |
| 高性能批量 | batch_convert_md_to_docx | `batch_convert_md_to_docx("/input", parallel_jobs=8)` |

### 📁 文件管理
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| 列出文件 | list_markdown_files | `list_markdown_files("/path/to/folder")` |
| 递归搜索 | list_markdown_files | `list_markdown_files("/path/to/folder", recursive=True)` |
| 验证文件 | validate_markdown_file | `validate_markdown_file("/path/to/file.md")` |

### ⚙️ 配置管理
| 使用场景 | 工具 | 命令示例 |
|----------|------|----------|
| 查看状态 | get_conversion_status | `get_conversion_status()` |
| 查看配置 | configure_converter | `configure_converter("show", "all")` |
| 设置项目路径 | quick_config_md2docx_path | `quick_config_md2docx_path("/path/to/md2docx")` |
| 设置输出目录 | quick_config_output_dir | `quick_config_output_dir("/path/to/output")` |
| 启用调试 | quick_config_debug_mode | `quick_config_debug_mode(True)` |
| 设置并行数 | quick_config_parallel_jobs | `quick_config_parallel_jobs(8)` |

## 🤔 决策树

```
转换需求分析
    ↓
首次使用? → Yes → quick_config_md2docx_path() ✅
    ↓ No
批量转换? → Yes → batch_convert_md_to_docx() ✅
    ↓ No
有问题? → Yes → validate_markdown_file() + debug模式 ✅
    ↓ No
单文件转换 → convert_md_to_docx() ✅
```

## 💡 使用建议

### 📄 首次使用流程
1. **配置项目路径**: `quick_config_md2docx_path("/path/to/md2docx")`
2. **设置输出目录**: `quick_config_output_dir("/path/to/output")`
3. **测试转换**: `convert_md_to_docx("/path/to/test.md")`
4. **检查结果**: 验证生成的 DOCX 文件

### 🚀 批量处理流程
1. **查看文件**: `list_markdown_files("/path/to/folder")`
2. **设置并行数**: `quick_config_parallel_jobs(8)`
3. **执行批量转换**: `batch_convert_md_to_docx("/path/to/folder")`
4. **监控进度**: 查看转换日志和结果

### 🔧 问题诊断流程
1. **验证文件**: `validate_markdown_file("/path/to/problem.md")`
2. **启用调试**: `quick_config_debug_mode(True)`
3. **重新转换**: `convert_md_to_docx("/path/to/problem.md", debug=True)`
4. **分析错误**: 根据详细日志调整配置

## 🎯 快速开始示例

```python
# 📄 单文件转换
convert_md_to_docx("/Users/username/Documents/report.md")

# 📁 批量转换
batch_convert_md_to_docx("/Users/username/Documents/markdown-files/")

# ⚙️ 配置管理
quick_config_md2docx_path("/Users/username/Workspace/md2docx")
quick_config_output_dir("/Users/username/Documents/output/")

# 🔧 问题诊断
validate_markdown_file("/Users/username/Documents/problem.md")
```

## ⚠️ 重要提示

- 首次使用必须配置 MD2DOCX 项目路径
- 批量转换时建议先小批量测试
- 遇到问题时启用调试模式获取详细信息
- 使用绝对路径避免路径错误
- 根据系统性能调整并行任务数

**🚀 准备开始转换？使用上面的 AI 推荐方案！**
"""

@mcp.prompt()
def md2docx_troubleshooting_guide(
    error_type: str = "conversion_failed",
    file_path: str = "/path/to/problem.md",
    output_format: str = "docx"
) -> str:
    """统一转换故障排除指南
    
    提供针对 DOCX/PPTX 转换常见问题的诊断步骤和解决方案。
    """
    
    error_lower = error_type.lower()
    format_lower = output_format.lower()
    
    # 错误类型分析
    is_path_error = any(keyword in error_lower for keyword in ['path', 'not found', 'missing', '路径', '找不到'])
    is_format_error = any(keyword in error_lower for keyword in ['format', 'encoding', 'invalid', '格式', '编码'])
    is_permission_error = any(keyword in error_lower for keyword in ['permission', 'access', 'denied', '权限', '访问'])
    is_config_error = any(keyword in error_lower for keyword in ['config', 'setup', 'not configured', '配置'])
    is_pptx_error = any(keyword in error_lower for keyword in ['pptx', 'powerpoint', 'presentation', 'template'])
    is_dependency_error = any(keyword in error_lower for keyword in ['module', 'import', 'dependency', '依赖', '模块'])
    
    # 格式特定错误
    is_pptx_format = format_lower in ['pptx', 'powerpoint', 'presentation']
    
    # 确定主要问题类型和诊断步骤
    if is_dependency_error:
        problem_type = "依赖问题"
        if is_pptx_format or is_pptx_error:
            diagnostic_steps = [
                "get_conversion_status()",
                "quick_config_debug_mode(True)",
                f"convert_markdown('{file_path}', 'pptx', debug=True)"
            ]
        else:
            diagnostic_steps = [
                "get_conversion_status()",
                f"validate_markdown_file('{file_path}')",
                f"convert_markdown('{file_path}', 'docx', debug=True)"
            ]
    elif is_config_error:
        problem_type = "配置问题"
        diagnostic_steps = [
            "get_conversion_status()",
            "configure_converter('show', 'all')",
            "quick_config_debug_mode(True)"
        ]
    elif is_path_error:
        problem_type = "路径问题"
        diagnostic_steps = [
            f"validate_markdown_file('{file_path}')",
            "list_markdown_files('/path/to/directory')",
            "get_conversion_status()"
        ]
    elif is_format_error:
        problem_type = "格式问题"
        diagnostic_steps = [
            f"validate_markdown_file('{file_path}')",
            "quick_config_debug_mode(True)",
            f"convert_markdown('{file_path}', '{output_format}', debug=True)"
        ]
    elif is_permission_error:
        problem_type = "权限问题"
        diagnostic_steps = [
            "get_conversion_status()",
            "quick_config_output_dir('/writable/path')",
            f"convert_markdown('{file_path}', '{output_format}')"
        ]
    elif is_pptx_error or is_pptx_format:
        problem_type = "PPTX转换问题"
        diagnostic_steps = [
            "get_conversion_status()",
            "quick_config_pptx_template('Martin Template.pptx')",
            f"convert_markdown('{file_path}', 'pptx', debug=True)"
        ]
    else:
        problem_type = "一般转换问题"
        diagnostic_steps = [
            f"validate_markdown_file('{file_path}')",
            "quick_config_debug_mode(True)",
            f"convert_markdown('{file_path}', '{output_format}', debug=True)"
        ]
    
    return f"""# 🔧 统一转换故障排除指南

## 🚨 问题分析
**错误类型**: {error_type}
**问题文件**: {file_path}
**输出格式**: {output_format.upper()}
**问题分类**: {problem_type}

## 🔍 诊断步骤

### 第一步：基础检查
```
{diagnostic_steps[0]}
```

### 第二步：详细分析
```
{diagnostic_steps[1]}
```

### 第三步：问题解决
```
{diagnostic_steps[2]}
```

## 🛠️ 常见问题解决方案

### ❌ 转换器项目路径未配置
**症状**: "项目路径不存在" 或 "not configured"
**解决方案**:
```
get_conversion_status()
# 检查 MD2DOCX 和 MD2PPTX 项目状态
# 如果路径不存在，项目应该已经通过子模块自动配置
```

### ❌ PPTX 转换失败 - 依赖问题
**症状**: "ModuleNotFoundError: No module named 'pptx'"
**解决方案**:
```
# 检查虚拟环境
get_conversion_status()

# 确保使用正确的 Python 环境
quick_config_debug_mode(True)
convert_markdown("{file_path}", "pptx", debug=True)

# 如果仍然失败，重新安装依赖
# 在终端运行: uv sync
```

### ❌ PPTX 模板问题
**症状**: "Template not found" 或模板相关错误
**解决方案**:
```
# 设置默认模板
quick_config_pptx_template("Martin Template.pptx")

# 使用模板转换
convert_with_template("{file_path}", "pptx", "Martin Template.pptx")

# 检查模板状态
get_conversion_status()
```

### ❌ 文件不存在或路径错误
**症状**: "File not found" 或 "Path does not exist"
**解决方案**:
```
# 验证文件
validate_markdown_file("{file_path}")

# 列出目录文件
list_markdown_files("/correct/directory/path")

# 使用绝对路径
convert_markdown("/absolute/path/to/file.md", "{output_format}")
```

### ❌ 文件格式或编码问题
**症状**: "Encoding error" 或 "Invalid format"
**解决方案**:
```
# 验证文件格式
validate_markdown_file("{file_path}")

# 更新文件编码配置
configure_converter("update", "file", encoding="utf-8")

# 调试转换
convert_markdown("{file_path}", "{output_format}", debug=True)
```

### ❌ 权限或输出目录问题
**症状**: "Permission denied" 或 "Cannot write to directory"
**解决方案**:
```
# 设置可写输出目录
quick_config_output_dir("/writable/output/path")

# 检查状态
get_conversion_status()

# 重新转换
convert_markdown("{file_path}", "{output_format}")
```

### ❌ 批量转换失败
**症状**: 部分文件转换失败
**解决方案**:
```
# 启用调试模式
quick_config_debug_mode(True)

# 降低并行数
quick_config_parallel_jobs(2)

# 分格式批量转换
batch_convert_markdown("/input/path", ["docx"])
batch_convert_markdown("/input/path", ["pptx"])
```

### ❌ 多格式转换问题
**症状**: 某种格式转换失败
**解决方案**:
```
# 分别测试各格式
convert_markdown("{file_path}", "docx", debug=True)
convert_markdown("{file_path}", "pptx", debug=True)

# 检查格式特定配置
configure_converter("show", "all")
```

## 🔄 完整诊断流程

### 1️⃣ 系统状态检查
```
get_conversion_status()
```
检查转换器路径、输出目录、配置状态、支持格式

### 2️⃣ 文件验证
```
validate_markdown_file("{file_path}")
```
验证文件存在性、格式、编码

### 3️⃣ 调试模式转换
```
quick_config_debug_mode(True)
convert_markdown("{file_path}", "{output_format}", debug=True)
```
获取详细错误信息和执行日志

### 4️⃣ 格式特定检查
```python
# 对于 PPTX 问题
quick_config_pptx_template("Martin Template.pptx")
convert_with_template("{file_path}", "pptx", "Martin Template.pptx")

# 对于 DOCX 问题  
convert_md_to_docx("{file_path}", debug=True)
```

### 5️⃣ 配置调整
根据错误信息调整相应配置

### 6️⃣ 重新测试
使用修正后的配置重新转换

## 🆕 新功能相关问题

### PPTX 转换新功能
- ✅ 支持专业模板 (Martin Template.pptx)
- ✅ 自定义模板支持
- ✅ 智能幻灯片布局
- ✅ 多媒体内容处理

### 多格式转换
- ✅ 同时生成 DOCX 和 PPTX
- ✅ 批量多格式处理
- ✅ 格式特定配置
- ✅ 并行转换优化

### 模板系统
- ✅ 内置专业模板
- ✅ 模板验证和管理
- ✅ 自定义模板支持
- ✅ 模板预览功能

## 📞 获取帮助

如果问题仍然存在，请：

1. **📊 收集信息**:
   ```
   get_conversion_status()
   validate_markdown_file("{file_path}")
   ```

2. **🔍 启用详细日志**:
   ```
   quick_config_debug_mode(True)
   convert_markdown("{file_path}", "{output_format}", debug=True)
   ```

3. **📋 检查配置**:
   ```
   configure_converter("show", "all")
   ```

4. **🐛 报告问题**: 在 [GitHub Issues](https://github.com/ddipass/md2docx-mcp-server/issues) 提供详细信息

**🔧 开始诊断？按照上面的步骤逐一检查！**
"""

@mcp.tool()
async def get_md2pptx_format_guide(
    presentation_type: str = "business",
    slide_count: str = "medium"
) -> str:
    """
    获取 md2pptx 格式指导，帮助生成符合模板要求的 Markdown
    
    Args:
        presentation_type: 演示类型 (business/academic/technical/creative)
        slide_count: 幻灯片数量 (short/medium/long)
        
    Returns:
        详细的 md2pptx 格式指导和模板
        
    Use cases:
        - 商务演示: get_md2pptx_format_guide("business", "medium")
        - 学术演示: get_md2pptx_format_guide("academic", "long")
        - 技术演示: get_md2pptx_format_guide("technical", "short")
    """
    
    # 根据演示类型确定推荐设置
    type_settings = {
        "business": {
            "pageTitleSize": 24,
            "sectionTitleSize": 30,
            "baseTextSize": 20,
            "style": "professional",
            "colors": ["blue", "gray", "white"]
        },
        "academic": {
            "pageTitleSize": 22,
            "sectionTitleSize": 28,
            "baseTextSize": 18,
            "style": "scholarly",
            "colors": ["navy", "black", "white"]
        },
        "technical": {
            "pageTitleSize": 20,
            "sectionTitleSize": 26,
            "baseTextSize": 16,
            "style": "technical",
            "colors": ["green", "black", "white"]
        },
        "creative": {
            "pageTitleSize": 26,
            "sectionTitleSize": 32,
            "baseTextSize": 22,
            "style": "creative",
            "colors": ["purple", "orange", "white"]
        }
    }
    
    # 根据幻灯片数量确定结构建议
    count_structure = {
        "short": {
            "slides": "5-10",
            "sections": "2-3",
            "bullets_per_slide": "3-5"
        },
        "medium": {
            "slides": "10-20",
            "sections": "3-5",
            "bullets_per_slide": "4-6"
        },
        "long": {
            "slides": "20-40",
            "sections": "5-8",
            "bullets_per_slide": "3-5"
        }
    }
    
    settings = type_settings.get(presentation_type, type_settings["business"])
    structure = count_structure.get(slide_count, count_structure["medium"])
    
    return f"""# 📊 md2pptx 格式指导 - {presentation_type.title()} 演示

## 🎯 核心要求

### 📋 必需的元数据头部
每个 md2pptx Markdown 文件**必须**以元数据开头（在第一个空行之前）：

```markdown
template: Martin Template.pptx
pageTitleSize: {settings['pageTitleSize']}
sectionTitleSize: {settings['sectionTitleSize']}
baseTextSize: {settings['baseTextSize']}
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00
```

### 🏗️ 幻灯片结构层次

md2pptx 使用特定的标题层次来创建不同类型的幻灯片：

1. **`# 标题`** → **演示标题页** (封面)
2. **`## 标题`** → **章节分隔页** (Section Slide)
3. **`### 标题`** → **内容幻灯片** (Content Slide)
4. **`#### 标题`** → **卡片标题** (Card Title)

## 📝 推荐的演示结构

### 🎯 {presentation_type.title()} 演示规格
- **幻灯片数量**: {structure['slides']} 张
- **章节数量**: {structure['sections']} 个
- **每页要点**: {structure['bullets_per_slide']} 个
- **字体大小**: {settings['baseTextSize']}pt
- **风格**: {settings['style']}

### 📊 标准模板结构

```markdown
template: Martin Template.pptx
pageTitleSize: {settings['pageTitleSize']}
sectionTitleSize: {settings['sectionTitleSize']}
baseTextSize: {settings['baseTextSize']}
numbers: no

# 演示标题
副标题或演讲者信息

## 第一章节
章节介绍内容

### 第一个内容幻灯片
* 要点一
  * 子要点 1.1
  * 子要点 1.2
* 要点二
* 要点三

### 第二个内容幻灯片
* 要点一
* 要点二
* 要点三

## 第二章节
章节介绍内容

### 表格幻灯片示例
|列标题1|列标题2|列标题3|
|-------|-------|-------|
|数据1|数据2|数据3|
|数据4|数据5|数据6|

### 卡片幻灯片示例
<!-- md2pptx: cardlayout: horizontal -->

#### 卡片一
* 卡片内容
* 更多内容

#### 卡片二
* 卡片内容
* 更多内容
```

## 🎨 高级功能

### 🃏 卡片布局
使用 `#### 标题` 创建卡片，配合 HTML 注释控制布局：

```markdown
### 卡片展示页面
<!-- md2pptx: cardlayout: horizontal -->
<!-- md2pptx: cardcolour: BACKGROUND 2 -->

#### 卡片标题一
* 卡片内容
* 更多内容

#### 卡片标题二
* 卡片内容
* 更多内容
```

### 📊 表格优化
```markdown
### 数据展示
|项目|Q1|Q2|Q3|Q4|
|:---|--:|--:|--:|--:|
|收入|100|120|150|180|
|支出|80|90|110|140|
|利润|20|30|40|40|
```

### 🎯 特殊格式

#### 代码块
```markdown
### 代码示例
```python
def hello_world():
    print("Hello, World!")
```
```

#### 图片插入
```markdown
### 图片展示
![图片描述](image.png)
```

#### 视频/音频
```markdown
### 多媒体内容
<video src="video.mp4" width="800" height="600"></video>
<audio src="audio.mp3"></audio>
```

## ⚠️ 重要约束和最佳实践

### ✅ 必须遵循的规则

1. **元数据头部**: 必须在文件开头，第一个空行之前
2. **标题层次**: 严格按照 #/##/###/#### 的层次结构
3. **模板引用**: 必须指定 `template: Martin Template.pptx`
4. **字体大小**: 建议设置 `pageTitleSize`, `sectionTitleSize`, `baseTextSize`

### ❌ 避免的问题

1. **跳级标题**: 不要从 # 直接跳到 ###
2. **空标题**: 每个标题都应该有内容
3. **过长内容**: 每页要点不超过 7 个
4. **缺少元数据**: 没有元数据头部会使用默认设置

### 🎯 内容建议

#### 标题页 (# 标题)
- 简洁有力的主标题
- 副标题包含关键信息
- 演讲者/日期信息

#### 章节页 (## 标题)
- 章节主题明确
- 可以包含简短介绍
- 作为内容分组的分隔

#### 内容页 (### 标题)
- 每页 3-6 个要点
- 使用层次化的要点结构
- 避免过长的文本

## 🚀 生成建议

### 📝 内容创作流程
1. **确定主题和目标受众**
2. **规划章节结构** (## 标题)
3. **设计内容幻灯片** (### 标题)
4. **添加元数据头部**
5. **优化要点和格式**

### 🎨 视觉设计考虑
- 保持一致的字体大小
- 合理使用颜色标记
- 适当的图表和图片
- 清晰的信息层次

### 📊 质量检查清单
- [ ] 元数据头部完整
- [ ] 标题层次正确
- [ ] 每页内容适量
- [ ] 图片路径正确
- [ ] 特殊格式语法正确

## 💡 {presentation_type.title()} 演示特定建议

### 🎯 内容重点
- **商务**: 数据驱动，结果导向，专业图表
- **学术**: 逻辑严密，引用充分，理论框架
- **技术**: 代码示例，架构图，实现细节
- **创意**: 视觉冲击，故事叙述，情感连接

### 🎨 推荐配色
- **主色调**: {', '.join(settings['colors'])}
- **强调色**: 用于重要信息高亮
- **背景色**: 保持简洁专业

**🎯 使用这个指导来生成完美适配 md2pptx 的 Markdown 内容！**
"""

@mcp.tool()
async def validate_markdown_file(file_path: str) -> str:
    """
    验证 Markdown 文件是否可以转换
    
    Args:
        file_path: Markdown 文件路径
        
    Returns:
        验证结果信息
        
    Use cases:
        - 验证文件: validate_markdown_file("/path/to/file.md")
    """
    
    try:
        file_path_obj = Path(file_path)
        
        # 基本检查
        if not file_path_obj.exists():
            return f"❌ 文件不存在: {file_path}"
        
        if not file_path_obj.is_file():
            return f"❌ 路径不是文件: {file_path}"
        
        # 扩展名检查
        if file_path_obj.suffix.lower() not in config_manager.file_settings.supported_extensions:
            return f"❌ 不支持的文件类型: {file_path_obj.suffix}"
        
        # 文件大小检查
        file_size = file_path_obj.stat().st_size
        if file_size == 0:
            return f"⚠️  文件为空: {file_path}"
        
        # 尝试读取文件
        try:
            with open(file_path, 'r', encoding=config_manager.file_settings.encoding) as f:
                content = f.read()
            
            if not content.strip():
                return f"⚠️  文件内容为空: {file_path}"
            
        except UnicodeDecodeError:
            return f"❌ 文件编码错误，无法使用 {config_manager.file_settings.encoding} 编码读取: {file_path}"
        
        return f"""✅ 文件验证通过!

📄 文件路径: {file_path}
📊 文件大小: {file_size} bytes
📝 内容长度: {len(content)} 字符
🔤 文件编码: {config_manager.file_settings.encoding}
📋 文件类型: {file_path_obj.suffix}

✅ 该文件可以进行转换"""
    
    except Exception as e:
        return f"❌ 验证过程出错: {str(e)}"

# ===== 服务器启动 =====

def main():
    """主函数"""
    print("🚀 统一转换 MCP Server 已启动")
    print("📋 可用工具:")
    print("  🔄 统一转换工具:")
    print("    - convert_markdown: 统一转换 (DOCX/PPTX/Both)")
    print("    - batch_convert_markdown: 批量多格式转换")
    print("    - convert_with_template: 模板转换")
    print("  ⚙️  配置管理工具:")
    print("    - quick_config_default_format: 设置默认格式")
    print("    - quick_config_pptx_template: 设置PPTX模板")
    print("    - get_conversion_status: 状态检查")
    print("  📊 PPTX 专用工具:")
    print("    - get_md2pptx_format_guide: md2pptx格式指导")
    print("  🔄 向后兼容工具:")
    print("    - convert_md_to_docx: 单独DOCX转换")
    print("    - batch_convert_md_to_docx: 批量DOCX转换")
    print("  📁 文件管理工具:")
    print("    - list_markdown_files: 列出文件")
    print("    - validate_markdown_file: 验证文件")
    print("  🎯 智能助手:")
    print("    - md2docx_conversion_guide: 转换指导")
    print("    - md2docx_troubleshooting_guide: 故障排除")
    print("    - md2pptx_content_generator: PPTX内容生成指导")
    print("✅ 服务器准备就绪 - 支持 DOCX 和 PPTX 转换")

if __name__ == "__main__":
    main()
    mcp.run()
