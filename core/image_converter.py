#!/usr/bin/env python3
"""
图片格式转换工具
用于将不兼容的图片格式转换为 LaTeX 支持的格式
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ImageConverter:
    """图片格式转换器"""
    
    def __init__(self):
        self.supported_input_formats = {
            '.bmp', '.tiff', '.tif', '.gif', '.webp', 
            '.svg', '.ico', '.psd', '.raw'
        }
        self.target_format = '.png'  # 转换目标格式
        self.conversion_tools = self._detect_conversion_tools()
    
    def _detect_conversion_tools(self) -> Dict[str, bool]:
        """检测可用的图片转换工具"""
        tools = {}
        
        # 检查 ImageMagick convert
        try:
            subprocess.run(['convert', '-version'], 
                         capture_output=True, check=True)
            tools['imagemagick'] = True
            logger.info("发现 ImageMagick convert 工具")
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools['imagemagick'] = False
        
        # 检查 sips (macOS)
        try:
            subprocess.run(['sips', '--version'], 
                         capture_output=True, check=True)
            tools['sips'] = True
            logger.info("发现 macOS sips 工具")
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools['sips'] = False
        
        # 检查 rsvg-convert (SVG)
        try:
            subprocess.run(['rsvg-convert', '--version'], 
                         capture_output=True, check=True)
            tools['rsvg'] = True
            logger.info("发现 rsvg-convert 工具")
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools['rsvg'] = False
        
        return tools
    
    def needs_conversion(self, image_path: str) -> bool:
        """检查图片是否需要转换"""
        ext = Path(image_path).suffix.lower()
        return ext in self.supported_input_formats
    
    def convert_image(self, input_path: str, output_dir: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        转换图片格式
        
        Args:
            input_path: 输入图片路径
            output_dir: 输出目录（可选）
            
        Returns:
            (成功标志, 输出路径, 错误信息)
        """
        input_file = Path(input_path)
        
        if not input_file.exists():
            return False, "", f"输入文件不存在: {input_path}"
        
        # 确定输出路径
        if output_dir:
            output_path = Path(output_dir) / f"{input_file.stem}{self.target_format}"
        else:
            output_path = input_file.with_suffix(self.target_format)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 选择转换工具
        success, error = self._convert_with_available_tool(input_file, output_path)
        
        if success:
            return True, str(output_path), ""
        else:
            return False, "", error
    
    def _convert_with_available_tool(self, input_path: Path, output_path: Path) -> Tuple[bool, str]:
        """使用可用工具进行转换"""
        input_ext = input_path.suffix.lower()
        
        # SVG 优先使用 rsvg-convert
        if input_ext == '.svg' and self.conversion_tools.get('rsvg'):
            return self._convert_with_rsvg(input_path, output_path)
        
        # ImageMagick 支持最多格式
        if self.conversion_tools.get('imagemagick'):
            return self._convert_with_imagemagick(input_path, output_path)
        
        # macOS sips 作为备选
        if self.conversion_tools.get('sips'):
            return self._convert_with_sips(input_path, output_path)
        
        return False, "未找到可用的图片转换工具"
    
    def _convert_with_imagemagick(self, input_path: Path, output_path: Path) -> Tuple[bool, str]:
        """使用 ImageMagick 转换"""
        try:
            cmd = [
                'convert',
                str(input_path),
                '-quality', '90',  # 设置质量
                '-resize', '2048x2048>',  # 限制最大尺寸
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"ImageMagick 转换成功: {input_path} -> {output_path}")
                return True, ""
            else:
                error = f"ImageMagick 转换失败: {result.stderr}"
                logger.error(error)
                return False, error
                
        except subprocess.TimeoutExpired:
            return False, "ImageMagick 转换超时"
        except Exception as e:
            return False, f"ImageMagick 转换异常: {str(e)}"
    
    def _convert_with_sips(self, input_path: Path, output_path: Path) -> Tuple[bool, str]:
        """使用 macOS sips 转换"""
        try:
            cmd = [
                'sips',
                '-s', 'format', 'png',
                '-Z', '2048',  # 限制最大尺寸
                str(input_path),
                '--out', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"sips 转换成功: {input_path} -> {output_path}")
                return True, ""
            else:
                error = f"sips 转换失败: {result.stderr}"
                logger.error(error)
                return False, error
                
        except subprocess.TimeoutExpired:
            return False, "sips 转换超时"
        except Exception as e:
            return False, f"sips 转换异常: {str(e)}"
    
    def _convert_with_rsvg(self, input_path: Path, output_path: Path) -> Tuple[bool, str]:
        """使用 rsvg-convert 转换 SVG"""
        try:
            cmd = [
                'rsvg-convert',
                '-f', 'png',
                '-w', '1024',  # 设置宽度
                '-h', '1024',  # 设置高度
                str(input_path),
                '-o', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"rsvg-convert 转换成功: {input_path} -> {output_path}")
                return True, ""
            else:
                error = f"rsvg-convert 转换失败: {result.stderr}"
                logger.error(error)
                return False, error
                
        except subprocess.TimeoutExpired:
            return False, "rsvg-convert 转换超时"
        except Exception as e:
            return False, f"rsvg-convert 转换异常: {str(e)}"
    
    def batch_convert(self, input_dir: str, output_dir: Optional[str] = None) -> Dict[str, any]:
        """批量转换图片"""
        input_path = Path(input_dir)
        results = {
            'success_count': 0,
            'failed_count': 0,
            'conversions': [],
            'errors': []
        }
        
        if not input_path.exists():
            results['errors'].append(f"输入目录不存在: {input_dir}")
            return results
        
        # 查找需要转换的图片
        for ext in self.supported_input_formats:
            for image_file in input_path.glob(f"*{ext}"):
                success, output_path, error = self.convert_image(
                    str(image_file), output_dir
                )
                
                if success:
                    results['success_count'] += 1
                    results['conversions'].append({
                        'input': str(image_file),
                        'output': output_path
                    })
                else:
                    results['failed_count'] += 1
                    results['errors'].append(f"{image_file}: {error}")
        
        return results
    
    def get_status(self) -> Dict[str, any]:
        """获取转换器状态"""
        return {
            'available_tools': {
                tool: available for tool, available in self.conversion_tools.items()
            },
            'supported_input_formats': list(self.supported_input_formats),
            'target_format': self.target_format,
            'ready': any(self.conversion_tools.values())
        }

# 使用示例
if __name__ == "__main__":
    converter = ImageConverter()
    status = converter.get_status()
    print("图片转换器状态:", status)
    
    # 测试转换
    if status['ready']:
        success, output, error = converter.convert_image("test.bmp")
        if success:
            print(f"转换成功: {output}")
        else:
            print(f"转换失败: {error}")
