#!/usr/bin/env python3
"""
MD2DOCX MCP Server - Markdown 到 DOCX/PPTX 转换服务器 (改进版)
基于 Model Context Protocol (MCP) 的统一文档转换服务

改进内容：
- 保持原有架构和设计思路
- 增强工具描述和用户体验
- 优化错误处理和状态反馈
- 改进 Q CLI 工具提示
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
print("🚀 正在启动 MD2DOCX MCP Server (改进版)...")
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
print(f"📋 改进版服务器特性:")
print(f"  🎯 保持原有架构和设计思路")
print(f"  📝 增强工具描述和用户体验")
print(f"  🔧 优化错误处理和状态反馈")
print(f"  💡 改进 Q CLI 工具提示")

# 创建 MCP 服务器
mcp = FastMCP("MD2DOCX-Converter-Enhanced")

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
- MD2PPTX 项目路径: {settings.md2pptx_project_path}
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

@mcp.tool()
async def quick_config_md2docx_path(project_path: str) -> str:
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
    统一的 Markdown 转换工具 - 支持 DOCX、PPTX 和多格式转换
    
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

# ===== 向后兼容工具 =====

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

# ===== 文件管理工具 =====

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

# ===== 状态检查工具 =====

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
        
        status = f"""🔍 统一转换器状态 (改进版)

🖥️  服务器信息:
- 服务器名称: MD2DOCX-Converter-Enhanced
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

🔧 可用工具 (改进版):
- convert_markdown: 统一转换工具 (支持 DOCX/PPTX/Both)
- batch_convert_markdown: 批量多格式转换
- convert_with_template: 模板转换
- convert_md_to_docx: 单独DOCX转换 (向后兼容)
- batch_convert_md_to_docx: 批量DOCX转换 (向后兼容)
- list_markdown_files: 列出 Markdown 文件
- validate_markdown_file: 验证文件
- configure_converter: 配置管理
- get_conversion_status: 状态检查

💡 改进特性:
- 🎯 保持原有架构和设计思路
- 📝 增强工具描述和用户体验
- 🔧 优化错误处理和状态反馈
- 💡 改进 Q CLI 工具提示"""
        
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

# ===== MD2LATEX 专用工具 =====

@mcp.tool()
async def convert_md_to_latex(
    input_file: str,
    config: str = "default",
    template: str = "basic",
    output_file: Optional[str] = None
) -> str:
    """
    转换 Markdown 到 LaTeX (改进版)
    
    Args:
        input_file: 输入的 Markdown 文件路径
        config: 配置类型 (default/chinese/academic)
        template: 模板类型 (basic/academic/chinese_book)
        output_file: 输出文件路径（可选）
        
    Returns:
        转换结果信息
        
    Use cases:
        - 基础转换: convert_md_to_latex("/path/to/file.md")
        - 中文文档: convert_md_to_latex("/path/to/file.md", "chinese", "basic")
        - 学术论文: convert_md_to_latex("/path/to/file.md", "academic", "academic")
        - 中文书籍: convert_md_to_latex("/path/to/file.md", "chinese", "chinese_book")
    """
    
    try:
        from core.md2latex_adapter_v2 import MD2LaTeXAdapterV2 as MD2LaTeXAdapter
        
        # 检查输入文件
        input_path = Path(input_file)
        if not input_path.exists():
            return f"❌ 输入文件不存在: {input_file}"
        
        # 创建适配器
        adapter = MD2LaTeXAdapter()
        
        if not adapter.available:
            return "❌ MD2LaTeX 模块不可用，请检查安装"
        
        # 执行转换
        output_path = adapter.convert_file(
            input_file=input_file,
            output_file=output_file,
            config=config,
            template=template
        )
        
        # 获取文件信息
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        
        return f"""✅ LaTeX 转换成功! (改进版 v2.0.0)

📄 输入文件: {input_file}
📄 输出文件: {output_path}
⚙️  配置类型: {config}
🎨 模板类型: {template}
📝 内容长度: {len(md_content)} 字符
📊 LaTeX 长度: {len(latex_content)} 字符

🎯 新功能:
- ✅ 支持无限级别标题
- ✅ 改进的表格处理
- ✅ 更好的中文支持
- ✅ 代码高亮支持

💡 下一步: 使用 compile_latex_to_pdf 编译为 PDF"""
    
    except ImportError as e:
        return f"❌ MD2LaTeX 模块导入失败: {str(e)}"
    except Exception as e:
        return f"❌ 转换失败: {str(e)}"

@mcp.tool()
async def compile_latex_to_pdf(
    latex_file: str,
    engine: str = "xelatex",
    output_dir: Optional[str] = None,
    clean_temp: bool = True
) -> str:
    """
    编译 LaTeX 文件为 PDF
    
    Args:
        latex_file: LaTeX 文件路径
        engine: 编译引擎 (xelatex/pdflatex/lualatex)
        output_dir: 输出目录（可选）
        clean_temp: 是否清理临时文件
        
    Returns:
        编译结果信息
        
    Use cases:
        - 基础编译: compile_latex_to_pdf("/path/to/file.tex")
        - 指定引擎: compile_latex_to_pdf("/path/to/file.tex", "pdflatex")
        - 指定输出目录: compile_latex_to_pdf("/path/to/file.tex", output_dir="/path/to/output")
    """
    
    try:
        from core.latex_compiler import LaTeXCompiler
        
        # 检查输入文件
        latex_path = Path(latex_file)
        if not latex_path.exists():
            return f"❌ LaTeX 文件不存在: {latex_file}"
        
        # 创建编译器
        compiler = LaTeXCompiler()
        
        # 检查编译引擎是否可用
        if engine not in compiler.available_engines:
            return f"❌ 编译引擎 {engine} 不可用。可用引擎: {', '.join(compiler.available_engines)}"
        
        # 设置默认输出目录
        if output_dir is None:
            # 默认输出到 output/latex 目录
            project_root = Path(__file__).parent
            output_dir = str((project_root / "output" / "latex").resolve())
        
        # 确保使用绝对路径
        latex_path = Path(latex_file).resolve()
        
        # 执行编译
        result = compiler.compile(
            latex_file=str(latex_path),
            engine=engine,
            output_dir=output_dir,
            clean_temp=clean_temp
        )
        
        if result['success']:
            message = f"""✅ PDF 编译成功!

📄 LaTeX 文件: {latex_file}
📄 PDF 文件: {result['output_file']}
🔧 编译引擎: {result['engine']}
🔄 编译次数: {result['runs']}"""
            
            if result.get('warnings'):
                message += f"\n⚠️  警告数量: {len(result['warnings'])}"
            
            return message
        else:
            return f"""❌ PDF 编译失败!

📄 LaTeX 文件: {latex_file}
🔧 编译引擎: {engine}
❌ 错误信息: {result['error']}

💡 提示: 检查 LaTeX 语法或尝试其他编译引擎"""
    
    except ImportError:
        return "❌ LaTeX 编译器模块未正确安装"
    except Exception as e:
        return f"❌ 编译过程异常: {str(e)}"

@mcp.tool()
async def convert_md_to_pdf_direct(
    input_file: str,
    config: str = "default",
    template: str = "basic",
    engine: str = "xelatex",
    keep_latex: bool = False
) -> str:
    """
    直接从 Markdown 生成 PDF（一键转换）改进版
    
    Args:
        input_file: 输入的 Markdown 文件路径
        config: 配置类型 (default/chinese/academic)
        template: 模板类型 (basic/academic/chinese_book)
        engine: 编译引擎 (xelatex/pdflatex/lualatex)
        keep_latex: 是否保留中间的 LaTeX 文件
        
    Returns:
        转换结果信息
        
    Use cases:
        - 一键转换: convert_md_to_pdf_direct("/path/to/file.md")
        - 中文文档: convert_md_to_pdf_direct("/path/to/file.md", "chinese", "basic")
        - 学术论文: convert_md_to_pdf_direct("/path/to/file.md", "academic", "academic")
        - 中文书籍: convert_md_to_pdf_direct("/path/to/file.md", "chinese", "chinese_book")
    """
    
    try:
        # 第一步：转换为 LaTeX
        latex_result = await convert_md_to_latex(input_file, config, template)
        if "❌" in latex_result:
            return latex_result
        
        # 第二步：编译为 PDF
        # LaTeX 文件现在在 output/latex/ 目录中
        project_root = Path(__file__).parent
        latex_file = str((project_root / "output" / "latex" / f"{Path(input_file).stem}.tex").resolve())
        pdf_result = await compile_latex_to_pdf(latex_file, engine)
        
        # 第三步：清理中间文件（如果需要）
        if not keep_latex:
            try:
                Path(latex_file).unlink()
                # 清理其他编译产生的文件（在 output/latex/ 目录中）
                latex_path = Path(latex_file)
                base_path = latex_path.with_suffix('')
                for ext in ['.aux', '.log', '.out', '.toc', '.lof', '.lot']:
                    try:
                        (base_path.with_suffix(ext)).unlink()
                    except:
                        pass
            except Exception:
                pass  # 忽略删除失败
        
        if "✅" in pdf_result:
            # PDF 文件在 output/latex/ 目录中
            pdf_file = str(project_root / "output" / "latex" / f"{Path(input_file).stem}.pdf")
            return f"""✅ Markdown 到 PDF 转换完成! (改进版 v2.0.0)

📄 输入文件: {input_file}
📄 PDF 文件: {pdf_file}
⚙️  配置类型: {config}
🎨 模板类型: {template}
🔧 编译引擎: {engine}
📝 中间文件: {'保留' if keep_latex else '已清理'}

🎯 转换流程: Markdown → LaTeX → PDF
🚀 新功能: 支持无限级别标题、改进表格处理、更好中文支持
📁 输出目录: output/latex/"""
        else:
            return pdf_result
    
    except Exception as e:
        return f"❌ 一键转换失败: {str(e)}"

@mcp.tool()
async def check_md2latex_status() -> str:
    """
    检查 MD2LaTeX 模块状态 (改进版)
    
    Returns:
        MD2LaTeX 模块状态信息
        
    Use cases:
        - 检查状态: check_md2latex_status()
    """
    
    try:
        from core.md2latex_adapter_v2 import MD2LaTeXAdapterV2 as MD2LaTeXAdapter, UpstreamManager
        from core.latex_compiler import LaTeXCompiler
        
        # 检查适配器状态
        adapter = MD2LaTeXAdapter()
        adapter_status = adapter.get_status()
        
        # 检查编译器状态
        compiler = LaTeXCompiler()
        compiler_status = compiler.get_status()
        
        # 检查上游状态
        upstream_manager = UpstreamManager()
        upstream_status = upstream_manager.check_updates()
        
        status = f"""🔍 MD2LaTeX 模块状态 (改进版 v2.0.0)

📦 自维护版本信息:
- 状态: {'✅ 正常可用' if adapter_status['available'] else '❌ 不可用'}
- 版本: {adapter_status['version']}
- 描述: {adapter_status['description']}
- 项目路径: {adapter_status['md2latex_path']}

⚙️  支持的配置:
{chr(10).join(f'- {config}: {desc}' for config, desc in adapter.get_available_configs().items())}

🎨 支持的模板:
{chr(10).join(f'- {template}: {desc}' for template, desc in adapter.get_available_templates().items())}

🔧 LaTeX 编译器:
- 可用性: {'✅ 正常可用' if compiler_status['latex_available'] else '❌ 不可用'}
- 默认引擎: {compiler_status['default_engine']}
- 支持的编译引擎: {', '.join(compiler_status['supported_engines'])}

🚀 新功能特性:
{chr(10).join(f'- ✅ {feature}' for feature in adapter_status['features'])}

📊 上游状态:
- 管理方式: {upstream_status['status']}
- 说明: {upstream_status['message']}

💡 使用建议:
- 中文文档: 使用 config="chinese", template="basic"
- 学术论文: 使用 config="academic", template="academic"  
- 中文书籍: 使用 config="chinese", template="chinese_book"
- 一般文档: 使用 config="default", template="basic"

MD2LaTeX 改进版完全正常，支持无限级别标题和改进的表格处理！"""
        
        return status
    
    except ImportError as e:
        return f"❌ MD2LaTeX 模块导入失败: {str(e)}\n💡 请检查 md2latex 模块是否正确安装"
    except Exception as e:
        return f"❌ 状态检查失败: {str(e)}"

@mcp.tool()
async def update_md2latex_upstream() -> str:
    """
    更新上游 md2latex 项目 (改进版)
    
    Returns:
        更新结果信息
        
    Use cases:
        - 检查更新: update_md2latex_upstream()
    """
    
    try:
        from core.md2latex_adapter_v2 import UpstreamManager
        
        manager = UpstreamManager()
        
        # 检查更新状态
        update_status = manager.check_updates()
        
        return f"""📊 MD2LaTeX 更新状态 (改进版)

🔄 管理方式: {update_status['status']}
📝 说明: {update_status['message']}
📦 当前版本: {update_status['version']}

💡 重要提示:
当前使用自维护版本的 MD2LaTeX，具有以下优势：
- ✅ 支持无限级别标题
- ✅ 改进的表格处理
- ✅ 更好的中文支持
- ✅ 代码高亮支持
- ✅ 多种配置和模板

如需更新功能，请手动修改 md2latex/ 目录下的代码。"""
    
    except ImportError:
        return "❌ 上游管理器模块未正确安装"
    except Exception as e:
        return f"❌ 更新检查异常: {str(e)}"

# ===== MD2PPTX 专用工具 =====

@mcp.tool()
async def validate_md2pptx_format(file_path: str) -> str:
    """
    验证 Markdown 文件是否符合 MD2PPTX 格式要求
    
    Args:
        file_path: 要验证的 Markdown 文件路径
        
    Returns:
        验证结果和改进建议
        
    Use cases:
        - 验证格式: validate_md2pptx_format("/path/to/presentation.md")
    """
    
    try:
        file_path_obj = Path(file_path)
        
        # 基本文件检查
        if not file_path_obj.exists():
            return f"❌ 文件不存在: {file_path}"
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"❌ 文件编码错误，请使用 UTF-8 编码: {file_path}"
        
        lines = content.split('\n')
        issues = []
        suggestions = []
        metadata_found = False
        metadata_end_line = 0
        
        # 检查元数据头部
        for i, line in enumerate(lines):
            if line.strip() == '' and i > 0:
                metadata_end_line = i
                break
            if ':' in line and not line.startswith('#'):
                metadata_found = True
                # 检查必需的元数据
                if line.startswith('template:'):
                    template_value = line.split(':', 1)[1].strip()
                    if not template_value:
                        issues.append("❌ template 元数据为空")
                    elif not template_value.endswith('.pptx'):
                        issues.append("❌ template 必须是 .pptx 文件")
        
        if not metadata_found:
            issues.append("❌ 缺少元数据头部 - MD2PPTX 需要在文件开头定义元数据")
            suggestions.append("💡 添加元数据头部，至少包含: template: Martin Template.pptx")
        
        # 检查标题层次结构
        title_levels = []
        has_presentation_title = False
        has_section_title = False
        has_content_slides = False
        
        for i, line in enumerate(lines[metadata_end_line:], metadata_end_line):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title_levels.append((level, i + 1, line.strip()))
                
                if level == 1:
                    has_presentation_title = True
                elif level == 2:
                    has_section_title = True
                elif level == 3:
                    has_content_slides = True
                elif level > 4:
                    issues.append(f"⚠️  第{i+1}行: 标题层次过深 (>{level}级)，MD2PPTX 建议最多4级")
        
        # 检查标题层次跳跃
        for i in range(1, len(title_levels)):
            prev_level, prev_line, prev_title = title_levels[i-1]
            curr_level, curr_line, curr_title = title_levels[i]
            
            if curr_level > prev_level + 1:
                issues.append(f"⚠️  第{curr_line}行: 标题层次跳跃 (从{prev_level}级跳到{curr_level}级)")
        
        # 检查演示结构
        if not has_presentation_title:
            issues.append("❌ 缺少演示标题页 (# 标题)")
            suggestions.append("💡 添加演示标题页: # 您的演示标题")
        
        if not has_section_title and has_content_slides:
            suggestions.append("💡 建议添加章节页 (## 标题) 来组织内容")
        
        if not has_content_slides:
            issues.append("❌ 缺少内容幻灯片 (### 标题)")
            suggestions.append("💡 添加内容幻灯片: ### 幻灯片标题")
        
        # 检查要点格式
        bullet_issues = []
        for i, line in enumerate(lines):
            if line.strip().startswith('*') or line.strip().startswith('-'):
                # 检查要点缩进
                indent = len(line) - len(line.lstrip())
                if indent % 4 != 0 and indent % 2 != 0:
                    bullet_issues.append(f"第{i+1}行: 要点缩进不规范")
        
        if bullet_issues:
            issues.extend(bullet_issues[:3])  # 只显示前3个
            if len(bullet_issues) > 3:
                issues.append(f"... 还有 {len(bullet_issues) - 3} 个要点格式问题")
        
        # 生成验证报告
        if not issues and not suggestions:
            return f"""✅ MD2PPTX 格式验证通过!

📄 文件: {file_path}
📊 统计:
- 元数据: {'✅ 已定义' if metadata_found else '❌ 缺失'}
- 演示标题页: {'✅ 有' if has_presentation_title else '❌ 无'}
- 章节页: {'✅ 有' if has_section_title else '⚠️  无'}
- 内容幻灯片: {'✅ 有' if has_content_slides else '❌ 无'}
- 标题层次: ✅ 规范

🎯 该文件符合 MD2PPTX 格式要求，可以直接转换！"""
        
        else:
            report = f"""📋 MD2PPTX 格式验证报告

📄 文件: {file_path}
📊 统计:
- 元数据: {'✅ 已定义' if metadata_found else '❌ 缺失'}
- 演示标题页: {'✅ 有' if has_presentation_title else '❌ 无'}
- 章节页: {'✅ 有' if has_section_title else '⚠️  无'}
- 内容幻灯片: {'✅ 有' if has_content_slides else '❌ 无'}"""
            
            if issues:
                report += f"\n\n❌ 发现的问题:"
                for issue in issues:
                    report += f"\n{issue}"
            
            if suggestions:
                report += f"\n\n💡 改进建议:"
                for suggestion in suggestions:
                    report += f"\n{suggestion}"
            
            report += f"\n\n🔧 使用 quick_fix_md2pptx_format 工具可以自动修复部分问题"
            
            return report
    
    except Exception as e:
        return f"❌ 验证过程出错: {str(e)}"

@mcp.tool()
async def quick_fix_md2pptx_format(file_path: str) -> str:
    """
    快速修复 MD2PPTX 格式问题
    
    Args:
        file_path: 需要修复的 Markdown 文件路径
        
    Returns:
        修复结果报告
        
    Use cases:
        - 修复格式: quick_fix_md2pptx_format("/path/to/presentation.md")
    """
    
    try:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return f"❌ 文件不存在: {file_path}"
        
        # 读取原文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        fixes_applied = []
        
        # 检查是否有元数据
        has_metadata = False
        metadata_end = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '' and i > 0:
                metadata_end = i
                break
            if ':' in line and not line.startswith('#'):
                has_metadata = True
        
        # 如果没有元数据，添加默认元数据
        if not has_metadata:
            default_metadata = [
                "template: Martin Template.pptx",
                "pageTitleSize: 24",
                "sectionTitleSize: 30",
                "baseTextSize: 20",
                "numbers: no",
                "style.fgcolor.blue: 0000FF",
                "style.fgcolor.red: FF0000",
                "style.fgcolor.green: 00FF00",
                ""
            ]
            fixed_lines.extend(default_metadata)
            fixes_applied.append("✅ 添加了默认元数据头部")
        
        # 处理原有内容
        in_metadata = True
        for i, line in enumerate(lines):
            if in_metadata and line.strip() == '':
                in_metadata = False
                if has_metadata:
                    fixed_lines.append(line)
                continue
            
            if in_metadata and has_metadata:
                fixed_lines.append(line)
                continue
            
            # 修复标题格式
            if line.startswith('#'):
                # 确保标题后有空格
                level = len(line) - len(line.lstrip('#'))
                title_text = line.lstrip('#').strip()
                if title_text:
                    fixed_line = '#' * level + ' ' + title_text
                    if fixed_line != line:
                        fixes_applied.append(f"✅ 修复标题格式: 第{i+1}行")
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # 检查是否需要添加基本结构
        has_title = any(line.startswith('# ') for line in fixed_lines)
        has_content = any(line.startswith('### ') for line in fixed_lines)
        
        if not has_title:
            # 在元数据后添加标题页
            insert_pos = 0
            for i, line in enumerate(fixed_lines):
                if line.strip() == '' and i > 5:  # 跳过元数据部分
                    insert_pos = i + 1
                    break
            
            fixed_lines.insert(insert_pos, "# 演示标题")
            fixed_lines.insert(insert_pos + 1, "副标题或演讲者信息")
            fixed_lines.insert(insert_pos + 2, "")
            fixes_applied.append("✅ 添加了演示标题页")
        
        if not has_content:
            # 添加示例内容
            fixed_lines.extend([
                "## 第一章节",
                "",
                "### 示例内容页",
                "* 要点一",
                "* 要点二", 
                "* 要点三",
                ""
            ])
            fixes_applied.append("✅ 添加了示例内容结构")
        
        # 写入修复后的文件
        backup_path = file_path_obj.with_suffix('.md.backup')
        
        # 创建备份
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        if fixes_applied:
            report = f"""✅ MD2PPTX 格式修复完成!

📄 文件: {file_path}
💾 备份: {backup_path}

🔧 应用的修复:"""
            for fix in fixes_applied:
                report += f"\n{fix}"
            
            report += f"\n\n🎯 文件已修复，现在可以使用 convert_markdown 转换为 PPTX!"
            
            return report
        else:
            return f"""✅ 文件格式良好

📄 文件: {file_path}
🎯 该文件已符合 MD2PPTX 格式要求，无需修复"""
    
    except Exception as e:
        return f"❌ 修复过程出错: {str(e)}"

@mcp.tool()
async def create_md2pptx_content(
    topic: str,
    presentation_type: str = "technical",
    target_audience: str = "team",
    slide_count: str = "medium"
) -> str:
    """
    智能创建符合 MD2PPTX 格式的演示内容
    
    Args:
        topic: 演示主题
        presentation_type: 演示类型 (technical/business/training/product)
        target_audience: 目标受众 (team/management/customers/investors)
        slide_count: 幻灯片数量 (short/medium/long)
        
    Returns:
        符合 MD2PPTX 格式的完整 Markdown 内容
        
    Use cases:
        - 技术演示: create_md2pptx_content("AI项目架构", "technical", "team")
        - 商务演示: create_md2pptx_content("季度业绩", "business", "management")
        - 产品演示: create_md2pptx_content("新产品发布", "product", "customers")
    """
    
    try:
        # 根据演示类型确定设置
        type_configs = {
            "technical": {
                "pageTitleSize": 22,
                "sectionTitleSize": 28,
                "baseTextSize": 18,
                "focus": "技术架构、实现细节、代码示例",
                "tone": "精确、详细、实用性强"
            },
            "business": {
                "pageTitleSize": 24,
                "sectionTitleSize": 30,
                "baseTextSize": 20,
                "focus": "数据驱动、结果导向、ROI分析",
                "tone": "专业、简洁、有说服力"
            },
            "training": {
                "pageTitleSize": 26,
                "sectionTitleSize": 32,
                "baseTextSize": 22,
                "focus": "学习目标、步骤指导、实践练习",
                "tone": "清晰、循序渐进、互动性强"
            },
            "product": {
                "pageTitleSize": 25,
                "sectionTitleSize": 31,
                "baseTextSize": 21,
                "focus": "功能特性、用户价值、竞争优势",
                "tone": "吸引人、易理解、突出价值"
            }
        }
        
        # 根据幻灯片数量确定结构
        count_configs = {
            "short": {"slides": "5-8", "sections": 2, "content_per_section": 2},
            "medium": {"slides": "10-15", "sections": 3, "content_per_section": 3},
            "long": {"slides": "20-30", "sections": 4, "content_per_section": 4}
        }
        
        config = type_configs.get(presentation_type, type_configs["technical"])
        structure = count_configs.get(slide_count, count_configs["medium"])
        
        # 生成元数据头部
        metadata = f"""template: Martin Template.pptx
pageTitleSize: {config['pageTitleSize']}
sectionTitleSize: {config['sectionTitleSize']}
baseTextSize: {config['baseTextSize']}
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00"""
        
        # 生成演示标题
        title_section = f"""
# {topic}
{target_audience.title()} 专题演示"""
        
        # 根据主题和类型生成内容
        if "AI" in topic or "人工智能" in topic or "机器学习" in topic:
            content_sections = """

## 项目概述

### 背景与机遇
* AI技术快速发展，应用场景不断扩大
* 行业数字化转型需求迫切
* 数据资源丰富，具备AI应用基础
* 技术团队具备相关经验和能力

### 项目目标
* 提升业务效率 50% 以上
* 降低运营成本 30%
* 增强客户体验满意度
* 构建智能化竞争优势

## 技术方案

### 核心架构
* **数据层**: 数据采集、清洗、特征工程
* **算法层**: 机器学习模型、深度学习框架
* **应用层**: 智能决策支持、自动化流程
* **接口层**: API服务、用户交互界面

### 关键技术
* 大语言模型 (LLM) 应用
* 计算机视觉处理
* 自然语言处理 (NLP)
* 实时数据分析

## 实施计划

### 阶段规划
|阶段|时间|关键任务|里程碑|
|:---|:---|:---|:---|
|第一阶段|1-3月|基础设施建设|平台搭建完成|
|第二阶段|4-6月|核心算法开发|模型训练完成|
|第三阶段|7-9月|系统集成测试|功能验证通过|
|第四阶段|10-12月|上线部署优化|正式投产运行|

### 风险控制
* 技术风险: 建立专家团队，制定备选方案
* 数据风险: 确保数据质量，建立安全机制
* 进度风险: 采用敏捷开发，定期评估调整"""
        
        elif "项目" in topic or "project" in topic.lower():
            content_sections = """

## 项目背景

### 项目驱动因素
* 市场需求变化，需要快速响应
* 现有系统功能限制，影响业务发展
* 竞争对手技术升级，需要保持优势
* 内部流程优化需求，提升效率

### 项目价值
* 提升业务处理能力
* 改善用户体验
* 降低运营成本
* 增强市场竞争力

## 解决方案

### 方案概述
* 采用现代化技术架构
* 模块化设计，便于扩展
* 注重用户体验设计
* 确保系统安全可靠

### 技术选型
* **前端**: React/Vue.js 现代化界面
* **后端**: Node.js/Python 高性能服务
* **数据库**: PostgreSQL/MongoDB 数据存储
* **部署**: Docker/Kubernetes 容器化部署

## 项目管理

### 团队组织
* 项目经理: 1名 (整体协调)
* 技术负责人: 1名 (架构设计)
* 开发工程师: 4名 (功能实现)
* 测试工程师: 2名 (质量保证)

### 进度安排
* **需求分析**: 2周
* **系统设计**: 3周  
* **开发实现**: 8周
* **测试部署**: 2周
* **上线运维**: 1周"""
        
        elif "产品" in topic or "product" in topic.lower():
            content_sections = """

## 产品概述

### 市场分析
* 目标市场规模和增长趋势
* 用户需求痛点分析
* 竞争对手产品对比
* 市场机会窗口

### 产品定位
* 核心价值主张
* 目标用户群体
* 产品差异化优势
* 市场定位策略

## 产品特性

### 核心功能
* **功能一**: 解决用户核心需求
* **功能二**: 提升使用体验
* **功能三**: 增强产品价值
* **功能四**: 扩展应用场景

### 技术优势
* 先进的技术架构
* 优秀的性能表现
* 良好的扩展性
* 完善的安全保障

## 商业模式

### 盈利模式
* 订阅服务收费
* 增值功能付费
* 企业定制服务
* 合作伙伴分成

### 市场策略
* 产品推广计划
* 渠道合作策略
* 用户获取方案
* 品牌建设规划"""
        
        else:
            content_sections = """

## 概述

### 背景介绍
* 当前市场环境分析
* 行业发展趋势
* 面临的机遇与挑战
* 项目启动的必要性

### 目标设定
* 核心目标明确
* 关键指标量化
* 成功标准定义
* 预期效果评估

## 方案详情

### 解决方案
* 核心理念阐述
* 主要组成部分
* 技术路线选择
* 创新点突出

### 实施策略
* 分阶段实施计划
* 资源配置方案
* 风险控制措施
* 质量保证体系

## 预期成果

### 效益分析
|类型|当前状态|目标状态|提升幅度|
|:---|:---|:---|:---|
|效率|基准值|目标值|+XX%|
|成本|当前成本|目标成本|-XX%|
|质量|现有水平|期望水平|+XX%|

### 成功保障
* 专业团队支持
* 充足资源投入
* 完善监控体系
* 持续优化改进"""
        
        # 组合完整内容
        full_content = metadata + title_section + content_sections
        
        return f"""✅ MD2PPTX 内容已生成!

📋 生成参数:
- 主题: {topic}
- 类型: {presentation_type}
- 受众: {target_audience}
- 规模: {structure['slides']} 张幻灯片

📝 生成的 Markdown 内容:

```markdown
{full_content}
```

🎯 使用方法:
1. 复制上面的 Markdown 内容
2. 保存为 .md 文件 (如: {topic.replace(' ', '_')}.md)
3. 使用 convert_markdown 工具转换: convert_markdown("文件路径", "pptx")

✅ 该内容完全符合 MD2PPTX 格式要求，可以直接转换！"""
    
    except Exception as e:
        return f"❌ 内容生成失败: {str(e)}"

@mcp.tool()
async def show_md2pptx_examples() -> str:
    """
    显示 MD2PPTX 格式示例
    
    Returns:
        标准格式示例和说明
        
    Use cases:
        - 查看示例: show_md2pptx_examples()
    """
    
    return """# 📊 MD2PPTX 格式示例和说明

## 🎯 核心格式要求

### 1. 必需的元数据头部
每个 MD2PPTX 文件**必须**以元数据开头（在第一个空行之前）：

```markdown
template: Martin Template.pptx
pageTitleSize: 24
sectionTitleSize: 30
baseTextSize: 20
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00
```

### 2. 标题层次结构
MD2PPTX 使用特定的标题层次创建不同类型的幻灯片：

- `# 标题` → **演示标题页** (封面)
- `## 标题` → **章节分隔页** (Section Slide)  
- `### 标题` → **内容幻灯片** (Content Slide)
- `#### 标题` → **卡片标题** (Card Title)

## 📝 完整示例

```markdown
template: Martin Template.pptx
pageTitleSize: 24
sectionTitleSize: 30
baseTextSize: 20
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00

# AI项目提案
智能化转型的战略机遇

## 项目背景

### 市场机遇分析
* AI技术快速发展，应用场景不断扩大
* 行业数字化转型需求迫切
* 竞争对手AI布局相对滞后
* 政策环境支持AI创新发展

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

## 投资回报

### 成本效益分析
|项目|投资|收益|回收期|
|:---|--:|--:|:---|
|AI平台|500万|800万|9个月|
|数据中台|300万|600万|6个月|
|算法优化|200万|400万|8个月|

### 总结与建议
* 项目技术方案先进可行
* 市场前景广阔明确
* 投资回报预期良好
* 建议立即启动实施
```

## 🎨 高级功能

### 卡片布局
```markdown
### 功能对比
<!-- md2pptx: cardlayout: horizontal -->
<!-- md2pptx: cardcolour: BACKGROUND 2 -->

#### 传统方案
* 手工处理
* 效率低下
* 错误率高

#### AI方案  
* 自动化处理
* 效率提升50%
* 准确率99%+
```

### 表格数据
```markdown
### 性能对比
|指标|当前|目标|提升|
|:---|--:|--:|--:|
|处理速度|100/h|500/h|400%|
|准确率|85%|99%|14%|
|成本|$1000|$600|40%|
```

## ⚠️ 重要约束

### ✅ 必须遵循
1. **元数据头部**: 必须在文件开头，第一个空行之前
2. **标题层次**: 严格按照 #/##/###/#### 的层次结构
3. **模板引用**: 必须指定 `template: Martin Template.pptx`

### ❌ 避免问题
1. **跳级标题**: 不要从 # 直接跳到 ###
2. **空标题**: 每个标题都应该有内容
3. **过长内容**: 每页要点不超过 7 个

## 🚀 使用流程

1. **创建内容**: 使用 `create_md2pptx_content` 生成标准格式
2. **验证格式**: 使用 `validate_md2pptx_format` 检查格式
3. **修复问题**: 使用 `quick_fix_md2pptx_format` 自动修复
4. **转换PPTX**: 使用 `convert_markdown` 转换为演示文稿

**🎯 遵循这些格式要求，确保完美的 PPTX 转换效果！**"""

@mcp.tool()
async def get_md2pptx_format_guide() -> str:
    """
    获取 MD2PPTX 格式规范指南
    
    Returns:
        详细的格式规范说明，帮助AI理解正确的Markdown格式
        
    Use cases:
        - 获取格式指南: get_md2pptx_format_guide()
    """
    
    return """# 📋 MD2PPTX 格式规范指南

## 🎯 核心设计原理

MD2PPTX 是一个将 Markdown 转换为 PowerPoint 演示文稿的工具，它有特定的格式要求：

### 1. 元数据驱动
- 所有样式和配置通过文件头部的元数据控制
- 元数据必须在第一个空行之前
- 支持字体大小、颜色、模板等配置

### 2. 层次化结构
- 使用 Markdown 标题层次映射到不同的幻灯片类型
- 每个层次有特定的用途和样式

### 3. 内容优化
- 针对演示文稿优化，支持要点、表格、卡片等
- 自动处理布局和格式

## 📝 必需元数据字段

```markdown
template: Martin Template.pptx    # 必需：PPTX模板文件
pageTitleSize: 24                # 页面标题字体大小
sectionTitleSize: 30             # 章节标题字体大小  
baseTextSize: 20                 # 基础文本字体大小
numbers: no                      # 是否显示页码
style.fgcolor.blue: 0000FF       # 蓝色定义
style.fgcolor.red: FF0000        # 红色定义
style.fgcolor.green: 00FF00      # 绿色定义
```

## 🏗️ 标题层次映射

| Markdown | 幻灯片类型 | 用途 | 样式特点 |
|----------|------------|------|----------|
| `# 标题` | 演示标题页 | 封面页 | 大标题，居中显示 |
| `## 标题` | 章节分隔页 | 章节开始 | 中等标题，分隔内容 |
| `### 标题` | 内容幻灯片 | 主要内容 | 标准内容页面 |
| `#### 标题` | 卡片标题 | 卡片内容 | 小标题，用于卡片 |

## 📊 内容类型支持

### 要点列表
```markdown
### 功能特性
* 主要功能一
  * 子功能 1.1
  * 子功能 1.2
* 主要功能二
* 主要功能三
```

### 表格数据
```markdown
### 性能对比
|指标|当前值|目标值|提升|
|:---|---:|---:|---:|
|速度|100|200|100%|
|准确率|90%|99%|9%|
```

### 卡片布局
```markdown
### 方案对比
<!-- md2pptx: cardlayout: horizontal -->

#### 方案A
* 优点一
* 优点二

#### 方案B  
* 优点一
* 优点二
```

## 🎨 高级功能

### HTML注释控制
- `<!-- md2pptx: cardlayout: horizontal -->` - 水平卡片布局
- `<!-- md2pptx: cardlayout: vertical -->` - 垂直卡片布局
- `<!-- md2pptx: cardcolour: BACKGROUND 2 -->` - 卡片背景色

### 颜色标记
```markdown
这是 <span class="blue">蓝色文本</span>
这是 <span class="red">红色文本</span>
这是 <span class="green">绿色文本</span>
```

### 代码块
```markdown
### 代码示例
```python
def hello_world():
    print("Hello, World!")
```
```

## ⚠️ 格式约束

### ✅ 正确做法
1. 元数据在文件开头，空行之前
2. 标题层次递进，不跳级
3. 每页内容适量（3-7个要点）
4. 使用标准的 Markdown 语法

### ❌ 错误做法
1. 缺少元数据头部
2. 标题层次跳跃（如从#直接到###）
3. 内容过多导致页面拥挤
4. 使用不支持的 Markdown 扩展

## 🔧 质量检查清单

- [ ] 包含完整的元数据头部
- [ ] 指定了正确的模板文件
- [ ] 标题层次结构正确
- [ ] 每页内容数量适中
- [ ] 表格格式规范
- [ ] 特殊功能语法正确

## 💡 最佳实践

### 内容组织
1. **演示标题页**: 简洁有力的主标题和副标题
2. **章节页**: 用于内容分组和过渡
3. **内容页**: 每页聚焦一个主题，3-6个要点
4. **总结页**: 重点回顾和行动建议

### 视觉设计
1. 保持一致的字体大小设置
2. 合理使用颜色标记重点
3. 表格数据右对齐数字
4. 卡片布局突出对比

### 内容质量
1. 标题简洁明确
2. 要点表达清晰
3. 数据准确可信
4. 逻辑结构清晰

**🎯 遵循这些规范，确保生成高质量的 PowerPoint 演示文稿！**"""

# ===== 服务器启动 =====

def main():
    """主函数"""
    print("🚀 MD2DOCX MCP Server (改进版) 已启动")
    print("📋 可用工具:")
    print("  🔄 统一转换工具:")
    print("    - convert_markdown: 统一转换 (DOCX/PPTX/Both)")
    print("    - batch_convert_markdown: 批量多格式转换")
    print("    - convert_with_template: 模板转换")
    print("  📊 MD2PPTX 专用工具:")
    print("    - validate_md2pptx_format: 验证MD2PPTX格式")
    print("    - quick_fix_md2pptx_format: 快速修复格式问题")
    print("    - create_md2pptx_content: 智能生成PPTX内容")
    print("    - show_md2pptx_examples: 显示格式示例")
    print("    - get_md2pptx_format_guide: 获取格式规范指南")
    print("  📄 MD2LaTeX 专用工具:")
    print("    - convert_md_to_latex: 转换MD到LaTeX")
    print("    - compile_latex_to_pdf: 编译LaTeX到PDF")
    print("    - convert_md_to_pdf_direct: 一键MD到PDF转换")
    print("    - check_md2latex_status: 检查MD2LaTeX状态")
    print("    - update_md2latex_upstream: 更新上游项目")
    print("  ⚙️  配置管理工具:")
    print("    - quick_config_default_format: 设置默认格式")
    print("    - quick_config_pptx_template: 设置PPTX模板")
    print("    - get_conversion_status: 状态检查")
    print("  🔄 向后兼容工具:")
    print("    - convert_md_to_docx: 单独DOCX转换")
    print("    - batch_convert_md_to_docx: 批量DOCX转换")
    print("  📁 文件管理工具:")
    print("    - list_markdown_files: 列出文件")
    print("    - validate_markdown_file: 验证文件")
    print("✅ 改进版服务器准备就绪 - 支持 DOCX、PPTX 和 LaTeX/PDF 转换")
    print("💡 新增特性: MD2LaTeX 转换，基于 VMIJUNV/md-to-latex 项目")
    print("🎯 支持格式: Markdown → DOCX/PPTX/LaTeX/PDF")

if __name__ == "__main__":
    main()
    mcp.run()
