#!/usr/bin/env python
"""
前后端端点同步检查脚本

比较后端 Django URL 配置和前端 TypeScript 端点常量，
输出不匹配的端点列表，确保前后端 API 路径一致。

用法:
    python .windsurf/specs/api-optimization/scripts/check_endpoint_sync.py

Requirements: 8.1 - 检查前端是否存在对应的路径更新
"""
import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, NamedTuple
from dataclasses import dataclass, field

# 项目根目录 (从 .windsurf/specs/api-optimization/scripts/ 向上 4 层)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
BACKEND_ROOT = PROJECT_ROOT / "HRM2-Django-Backend"
FRONTEND_ROOT = PROJECT_ROOT / "HRM2-Vue-Frontend_new"


@dataclass
class EndpointInfo:
    """端点信息"""
    path: str
    method: str = ""
    name: str = ""
    module: str = ""
    
    def normalized_path(self) -> str:
        """规范化路径，将参数占位符统一为 {param} 格式以便比较"""
        # Django: <uuid:xxx> -> {param}
        path = re.sub(r'<uuid:\w+>', '{param}', self.path)
        # Django: <int:xxx> -> {param}
        path = re.sub(r'<int:\w+>', '{param}', path)
        # Django: <str:xxx> -> {param}
        path = re.sub(r'<str:\w+>', '{param}', path)
        # 前端: ${xxx} -> {param}
        path = re.sub(r'\$\{\w+\}', '{param}', path)
        return path


class SyncCheckResult(NamedTuple):
    """同步检查结果"""
    backend_only: List[EndpointInfo]
    frontend_only: List[EndpointInfo]
    matched: List[Tuple[EndpointInfo, EndpointInfo]]


def parse_backend_urls() -> Dict[str, List[EndpointInfo]]:
    """
    解析后端 Django URL 配置
    
    Returns:
        模块名 -> 端点列表的映射
    """
    endpoints: Dict[str, List[EndpointInfo]] = {}
    
    # URL 模块映射
    url_modules = {
        'positions': BACKEND_ROOT / 'apps' / 'position_settings' / 'urls.py',
        'library': BACKEND_ROOT / 'apps' / 'resume_library' / 'urls.py',
        'screening': BACKEND_ROOT / 'apps' / 'resume_screening' / 'urls.py',
        'videos': BACKEND_ROOT / 'apps' / 'video_analysis' / 'urls.py',
        'recommend': BACKEND_ROOT / 'apps' / 'final_recommend' / 'urls.py',
        'interviews': BACKEND_ROOT / 'apps' / 'interview_assist' / 'urls.py',
    }
    
    for module_name, url_file in url_modules.items():
        if not url_file.exists():
            print(f"警告: URL 文件不存在: {url_file}")
            continue
            
        content = url_file.read_text(encoding='utf-8')
        endpoints[module_name] = []
        
        # 匹配 path('...', ..., name='...')
        path_pattern = r"path\(['\"]([^'\"]*)['\"].*?name=['\"]([^'\"]+)['\"]"
        
        for match in re.finditer(path_pattern, content, re.DOTALL):
            path_str = match.group(1)
            name = match.group(2)
            
            # 构建完整路径
            full_path = f"/api/{module_name}/{path_str}"
            # 去除双斜杠
            full_path = re.sub(r'//+', '/', full_path)
            
            endpoints[module_name].append(EndpointInfo(
                path=full_path,
                name=name,
                module=module_name
            ))
    
    return endpoints


def parse_frontend_endpoints() -> Dict[str, List[EndpointInfo]]:
    """
    解析前端 TypeScript 端点常量
    
    Returns:
        模块名 -> 端点列表的映射
    """
    endpoints: Dict[str, List[EndpointInfo]] = {}
    
    endpoint_file = FRONTEND_ROOT / 'src' / 'api' / 'endpoints.ts'
    if not endpoint_file.exists():
        print(f"错误: 前端端点文件不存在: {endpoint_file}")
        return endpoints
    
    content = endpoint_file.read_text(encoding='utf-8')
    
    # 模块映射
    module_mapping = {
        '岗位管理': 'positions',
        '简历库': 'library',
        '简历筛选': 'screening',
        '视频分析': 'videos',
        '最终推荐': 'recommend',
        '面试辅助': 'interviews',
    }
    
    # 初始化所有模块
    for module in module_mapping.values():
        endpoints[module] = []
    
    # 先用正则匹配所有端点定义（处理多行情况）
    # 将换行和多余空格合并
    normalized = re.sub(r'\s+', ' ', content)
    
    # 匹配简单端点: ENDPOINT_NAME: '/path/',
    simple_pattern = r"(\w+):\s*['\"](/[^'\"]+)['\"]"
    for match in re.finditer(simple_pattern, normalized):
        name = match.group(1)
        path = match.group(2)
        # 根据路径确定模块
        module = _get_module_from_path(path)
        if module:
            endpoints[module].append(EndpointInfo(
                path=f"/api{path}",
                name=name,
                module=module
            ))
    
    # 匹配函数端点: ENDPOINT_NAME: (xxx) => `/path/${xxx}/`,
    func_pattern = r"(\w+):\s*\([^)]*\)\s*=>\s*`(/[^`]+)`"
    for match in re.finditer(func_pattern, normalized):
        name = match.group(1)
        path = match.group(2)
        module = _get_module_from_path(path)
        if module:
            endpoints[module].append(EndpointInfo(
                path=f"/api{path}",
                name=name,
                module=module
            ))
    
    return endpoints


def _get_module_from_path(path: str) -> str:
    """根据路径推断模块名"""
    path_module_mapping = {
        '/positions/': 'positions',
        '/library/': 'library',
        '/screening/': 'screening',
        '/videos/': 'videos',
        '/recommend/': 'recommend',
        '/interviews/': 'interviews',
    }
    for prefix, module in path_module_mapping.items():
        if path.startswith(prefix):
            return module
    return ""


def check_sync(
    backend: Dict[str, List[EndpointInfo]], 
    frontend: Dict[str, List[EndpointInfo]]
) -> SyncCheckResult:
    """
    检查前后端端点同步状态
    
    Args:
        backend: 后端端点
        frontend: 前端端点
    
    Returns:
        同步检查结果
    """
    backend_only: List[EndpointInfo] = []
    frontend_only: List[EndpointInfo] = []
    matched: List[Tuple[EndpointInfo, EndpointInfo]] = []
    
    # 获取所有模块
    all_modules = set(backend.keys()) | set(frontend.keys())
    
    for module in all_modules:
        backend_eps = backend.get(module, [])
        frontend_eps = frontend.get(module, [])
        
        # 规范化路径用于匹配
        backend_paths = {ep.normalized_path(): ep for ep in backend_eps}
        frontend_paths = {ep.normalized_path(): ep for ep in frontend_eps}
        
        # 找出仅后端有的
        for path, ep in backend_paths.items():
            if path not in frontend_paths:
                backend_only.append(ep)
            else:
                matched.append((ep, frontend_paths[path]))
        
        # 找出仅前端有的
        for path, ep in frontend_paths.items():
            if path not in backend_paths:
                frontend_only.append(ep)
    
    return SyncCheckResult(
        backend_only=backend_only,
        frontend_only=frontend_only,
        matched=matched
    )


def print_report(result: SyncCheckResult) -> None:
    """打印检查报告"""
    print("=" * 60)
    print("前后端端点同步检查报告")
    print("=" * 60)
    print()
    
    # 匹配的端点
    print(f"✅ 已匹配端点: {len(result.matched)} 个")
    print()
    
    # 仅后端存在
    if result.backend_only:
        print(f"⚠️  仅后端存在的端点: {len(result.backend_only)} 个")
        for ep in result.backend_only:
            print(f"   - [{ep.module}] {ep.path} (name={ep.name})")
        print()
    else:
        print("✅ 没有仅后端存在的端点")
        print()
    
    # 仅前端存在
    if result.frontend_only:
        print(f"⚠️  仅前端存在的端点: {len(result.frontend_only)} 个")
        for ep in result.frontend_only:
            print(f"   - [{ep.module}] {ep.path} (name={ep.name})")
        print()
    else:
        print("✅ 没有仅前端存在的端点")
        print()
    
    # 总结
    print("=" * 60)
    if result.backend_only or result.frontend_only:
        print("❌ 检查结果: 存在不同步的端点")
        sys.exit(1)
    else:
        print("✅ 检查结果: 所有端点已同步")
        sys.exit(0)


def export_json(result: SyncCheckResult, output_path: Path) -> None:
    """导出 JSON 格式的检查结果"""
    data = {
        "matched": [
            {
                "backend_path": be.path,
                "backend_name": be.name,
                "frontend_path": fe.path,
                "frontend_name": fe.name,
                "module": be.module
            }
            for be, fe in result.matched
        ],
        "backend_only": [
            {"path": ep.path, "name": ep.name, "module": ep.module}
            for ep in result.backend_only
        ],
        "frontend_only": [
            {"path": ep.path, "name": ep.name, "module": ep.module}
            for ep in result.frontend_only
        ],
        "summary": {
            "matched_count": len(result.matched),
            "backend_only_count": len(result.backend_only),
            "frontend_only_count": len(result.frontend_only),
            "is_synced": len(result.backend_only) == 0 and len(result.frontend_only) == 0
        }
    }
    
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"检查结果已导出到: {output_path}")


def main():
    """主函数"""
    print("解析后端 URL 配置...")
    backend = parse_backend_urls()
    print(f"  找到 {sum(len(eps) for eps in backend.values())} 个后端端点")
    
    print("解析前端端点常量...")
    frontend = parse_frontend_endpoints()
    print(f"  找到 {sum(len(eps) for eps in frontend.values())} 个前端端点")
    
    print()
    print("执行同步检查...")
    result = check_sync(backend, frontend)
    
    print()
    print_report(result)


if __name__ == '__main__':
    main()
