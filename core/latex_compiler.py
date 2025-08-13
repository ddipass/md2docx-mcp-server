"""
LaTeX 编译器
处理 LaTeX 到 PDF 的编译过程
"""

import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, List, Any
import logging
import tempfile

logger = logging.getLogger(__name__)

class LaTeXCompiler:
    """
    LaTeX 编译器：处理 LaTeX 到 PDF 的编译
    - 支持多种编译引擎 (pdflatex, xelatex, lualatex)
    - 自动处理多次编译（参考文献、索引等）
    - 错误处理和日志分析
    - 临时文件清理
    """
    
    def __init__(self):
        self.supported_engines = ["xelatex", "pdflatex", "lualatex"]
        self.default_engine = "xelatex"  # 对中文支持更好
        
        # 检查可用的编译引擎
        self.available_engines = self._check_available_engines()
        
    def _check_available_engines(self) -> List[str]:
        """检查系统中可用的 LaTeX 编译引擎"""
        available = []
        
        for engine in self.supported_engines:
            try:
                result = subprocess.run(
                    [engine, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    available.append(engine)
                    logger.info(f"发现可用的 LaTeX 引擎: {engine}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning(f"LaTeX 引擎不可用: {engine}")
        
        return available
    
    def compile(self, 
                latex_file: str,
                engine: str = None,
                output_dir: Optional[str] = None,
                clean_temp: bool = True,
                max_runs: int = 3) -> Dict[str, Any]:
        """
        编译 LaTeX 文件为 PDF
        
        Args:
            latex_file: LaTeX 文件路径
            engine: 编译引擎 (xelatex, pdflatex, lualatex)
            output_dir: 输出目录（可选）
            clean_temp: 是否清理临时文件
            max_runs: 最大编译次数（处理交叉引用）
            
        Returns:
            编译结果信息
        """
        
        latex_path = Path(latex_file)
        if not latex_path.exists():
            return {
                "success": False,
                "error": f"LaTeX 文件不存在: {latex_file}",
                "output_file": None
            }
        
        # 选择编译引擎
        if engine is None:
            engine = self.default_engine
        
        if engine not in self.available_engines:
            return {
                "success": False,
                "error": f"编译引擎 {engine} 不可用。可用引擎: {', '.join(self.available_engines)}",
                "output_file": None
            }
        
        # 设置输出目录
        if output_dir is None:
            output_dir = latex_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 输出文件路径
        output_file = output_dir / f"{latex_path.stem}.pdf"
        
        try:
            # 执行编译
            compile_result = self._compile_latex(
                latex_path, 
                engine, 
                output_dir, 
                max_runs
            )
            
            if compile_result["success"]:
                # 清理临时文件
                if clean_temp:
                    self._clean_temp_files(latex_path, output_dir)
                
                return {
                    "success": True,
                    "output_file": str(output_file),
                    "engine": engine,
                    "runs": compile_result["runs"],
                    "warnings": compile_result.get("warnings", []),
                    "log_file": compile_result.get("log_file")
                }
            else:
                return {
                    "success": False,
                    "error": compile_result["error"],
                    "output_file": None,
                    "log_file": compile_result.get("log_file")
                }
        
        except Exception as e:
            logger.error(f"编译过程异常: {e}")
            return {
                "success": False,
                "error": f"编译过程异常: {str(e)}",
                "output_file": None
            }
    
    def _compile_latex(self, 
                      latex_path: Path, 
                      engine: str, 
                      output_dir: Path, 
                      max_runs: int) -> Dict[str, Any]:
        """执行 LaTeX 编译"""
        
        compile_runs = 0
        warnings = []
        log_content = ""
        
        # 切换到 LaTeX 文件目录（处理相对路径）
        original_cwd = os.getcwd()
        os.chdir(latex_path.parent)
        
        try:
            for run in range(max_runs):
                compile_runs += 1
                
                # 构建编译命令
                cmd = [
                    engine,
                    "-interaction=nonstopmode",
                    f"-output-directory={output_dir}",
                    str(latex_path.name)
                ]
                
                logger.info(f"执行编译 (第{run+1}次): {' '.join(cmd)}")
                
                # 执行编译
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                # 读取日志文件
                log_file = output_dir / f"{latex_path.stem}.log"
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                
                # 分析编译结果
                # 先检查是否有严重错误（以 ! 开头的行）
                has_fatal_errors = False
                if log_content:
                    for line in log_content.split('\n'):
                        if line.strip().startswith('!'):
                            has_fatal_errors = True
                            break
                
                # 如果有严重错误且返回码非零，则认为编译失败
                if result.returncode != 0 and has_fatal_errors:
                    error_msg = self._parse_latex_errors(log_content, result.stderr)
                    return {
                        "success": False,
                        "error": error_msg,
                        "runs": compile_runs,
                        "log_file": str(log_file) if log_file.exists() else None
                    }
                
                # 检查是否需要再次编译
                if not self._needs_recompile(log_content):
                    break
                
                # 解析警告
                run_warnings = self._parse_latex_warnings(log_content)
                warnings.extend(run_warnings)
            
            # 检查 PDF 是否生成成功
            pdf_file = output_dir / f"{latex_path.stem}.pdf"
            if not pdf_file.exists():
                return {
                    "success": False,
                    "error": "PDF 文件未生成，可能存在编译错误",
                    "runs": compile_runs,
                    "log_file": str(log_file) if log_file.exists() else None
                }
            
            return {
                "success": True,
                "runs": compile_runs,
                "warnings": warnings,
                "log_file": str(log_file) if log_file.exists() else None
            }
        
        finally:
            # 恢复原始工作目录
            os.chdir(original_cwd)
    
    def _needs_recompile(self, log_content: str) -> bool:
        """检查是否需要重新编译"""
        recompile_indicators = [
            "Rerun to get cross-references right",
            "There were undefined references",
            "Label(s) may have changed",
            "Rerun LaTeX"
        ]
        
        return any(indicator in log_content for indicator in recompile_indicators)
    
    def _parse_latex_errors(self, log_content: str, stderr: str) -> str:
        """解析 LaTeX 编译错误"""
        
        error_lines = []
        
        # 从日志中提取错误信息
        if log_content:
            lines = log_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('!'):
                    error_lines.append(line)
                    # 添加上下文
                    if i + 1 < len(lines):
                        error_lines.append(lines[i + 1])
        
        # 从 stderr 中提取错误信息
        if stderr:
            error_lines.extend(stderr.split('\n'))
        
        if error_lines:
            return '\n'.join(error_lines[:10])  # 限制错误信息长度
        else:
            return "编译失败，但未找到具体错误信息"
    
    def _parse_latex_warnings(self, log_content: str) -> List[str]:
        """解析 LaTeX 编译警告"""
        
        warnings = []
        
        if log_content:
            lines = log_content.split('\n')
            for line in lines:
                if 'Warning:' in line or 'warning:' in line:
                    warnings.append(line.strip())
        
        return warnings
    
    def _clean_temp_files(self, latex_path: Path, output_dir: Path):
        """清理临时文件"""
        
        temp_extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', 
                          '.bbl', '.blg', '.idx', '.ind', '.ilg', '.fls', 
                          '.fdb_latexmk', '.synctex.gz']
        
        base_name = latex_path.stem
        
        for ext in temp_extensions:
            temp_file = output_dir / f"{base_name}{ext}"
            if temp_file.exists():
                try:
                    temp_file.unlink()
                    logger.debug(f"删除临时文件: {temp_file}")
                except Exception as e:
                    logger.warning(f"无法删除临时文件 {temp_file}: {e}")
    
    def compile_with_bibliography(self, 
                                 latex_file: str,
                                 bib_file: Optional[str] = None,
                                 engine: str = None,
                                 output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        编译包含参考文献的 LaTeX 文件
        
        Args:
            latex_file: LaTeX 文件路径
            bib_file: BibTeX 文件路径（可选）
            engine: 编译引擎
            output_dir: 输出目录
            
        Returns:
            编译结果信息
        """
        
        latex_path = Path(latex_file)
        if not latex_path.exists():
            return {
                "success": False,
                "error": f"LaTeX 文件不存在: {latex_file}",
                "output_file": None
            }
        
        # 选择编译引擎
        if engine is None:
            engine = self.default_engine
        
        if engine not in self.available_engines:
            return {
                "success": False,
                "error": f"编译引擎 {engine} 不可用",
                "output_file": None
            }
        
        # 设置输出目录
        if output_dir is None:
            output_dir = latex_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 切换到 LaTeX 文件目录
        original_cwd = os.getcwd()
        os.chdir(latex_path.parent)
        
        try:
            # 第一次编译
            result1 = self._run_latex_command(engine, latex_path, output_dir)
            if not result1["success"]:
                return result1
            
            # 运行 BibTeX（如果有参考文献）
            if bib_file or self._has_bibliography(latex_path):
                bibtex_result = self._run_bibtex(latex_path.stem, output_dir)
                if not bibtex_result["success"]:
                    logger.warning(f"BibTeX 处理失败: {bibtex_result['error']}")
            
            # 第二次编译（处理参考文献）
            result2 = self._run_latex_command(engine, latex_path, output_dir)
            if not result2["success"]:
                return result2
            
            # 第三次编译（处理交叉引用）
            result3 = self._run_latex_command(engine, latex_path, output_dir)
            
            return result3
        
        finally:
            os.chdir(original_cwd)
    
    def _run_latex_command(self, engine: str, latex_path: Path, output_dir: Path) -> Dict[str, Any]:
        """运行单次 LaTeX 编译命令"""
        
        cmd = [
            engine,
            "-interaction=nonstopmode",
            f"-output-directory={output_dir}",
            str(latex_path.name)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            log_file = output_dir / f"{latex_path.stem}.log"
            log_content = ""
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
            
            error_msg = self._parse_latex_errors(log_content, result.stderr)
            return {
                "success": False,
                "error": error_msg,
                "log_file": str(log_file) if log_file.exists() else None
            }
        
        return {"success": True}
    
    def _run_bibtex(self, base_name: str, output_dir: Path) -> Dict[str, Any]:
        """运行 BibTeX"""
        
        try:
            cmd = ["bibtex", base_name]
            result = subprocess.run(
                cmd,
                cwd=output_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"BibTeX 错误: {result.stderr}"
                }
            
            return {"success": True}
        
        except Exception as e:
            return {
                "success": False,
                "error": f"BibTeX 执行异常: {str(e)}"
            }
    
    def _has_bibliography(self, latex_path: Path) -> bool:
        """检查 LaTeX 文件是否包含参考文献"""
        
        try:
            with open(latex_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            bibliography_commands = [
                '\\bibliography{',
                '\\bibliographystyle{',
                '\\cite{',
                '\\citep{',
                '\\citet{'
            ]
            
            return any(cmd in content for cmd in bibliography_commands)
        
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取编译器状态"""
        
        return {
            "available_engines": self.available_engines,
            "default_engine": self.default_engine,
            "supported_engines": self.supported_engines,
            "latex_available": len(self.available_engines) > 0
        }
