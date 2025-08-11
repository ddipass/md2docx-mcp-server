#!/usr/bin/env python3
"""
测试统一转换器功能
"""
import asyncio
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from core.unified_converter_manager import get_unified_converter_manager
from core.config_manager import get_config_manager

async def test_unified_converter():
    """测试统一转换器"""
    print("🧪 开始测试统一转换器...")
    
    # 获取管理器实例
    config_manager = get_config_manager()
    unified_converter = get_unified_converter_manager()
    
    print(f"✅ 配置管理器初始化完成")
    print(f"✅ 统一转换器初始化完成")
    print(f"📊 支持的格式: {unified_converter.get_supported_formats()}")
    
    # 测试文件路径
    test_file = Path(__file__).parent / "README.md"
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"📄 测试文件: {test_file}")
    
    # 测试 DOCX 转换
    print("\n🔄 测试 DOCX 转换...")
    try:
        result = await unified_converter.convert_single_file(
            input_file=str(test_file),
            output_format="docx",
            debug=True
        )
        
        if result['success']:
            print(f"✅ DOCX 转换成功: {result['output_file']}")
            print(f"⏱️  耗时: {result['duration']}秒")
        else:
            print(f"❌ DOCX 转换失败: {result['message']}")
    except Exception as e:
        print(f"❌ DOCX 转换异常: {e}")
    
    # 测试 PPTX 转换
    print("\n🔄 测试 PPTX 转换...")
    try:
        result = await unified_converter.convert_single_file(
            input_file=str(test_file),
            output_format="pptx",
            debug=True
        )
        
        if result['success']:
            print(f"✅ PPTX 转换成功: {result['output_file']}")
            print(f"⏱️  耗时: {result['duration']}秒")
        else:
            print(f"❌ PPTX 转换失败: {result['message']}")
    except Exception as e:
        print(f"❌ PPTX 转换异常: {e}")
    
    # 测试多格式转换
    print("\n🔄 测试多格式转换...")
    try:
        result = await unified_converter.convert_multiple_formats(
            input_file=str(test_file),
            output_formats=["docx", "pptx"],
            debug=True
        )
        
        print(f"📊 多格式转换结果: 成功 {result['success']}, 失败 {result['failed']}")
        for res in result['results']:
            status = "✅" if res['success'] else "❌"
            print(f"{status} {res['format'].upper()}: {res['message']}")
    except Exception as e:
        print(f"❌ 多格式转换异常: {e}")
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    asyncio.run(test_unified_converter())
