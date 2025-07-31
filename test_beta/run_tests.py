#!/usr/bin/env python3
"""Test runner for MCP server functionality."""

import pytest
import sys
import argparse
import subprocess
from pathlib import Path

# Add the beta directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'beta'))

def run_main_tests():
    """Run main MCP server tests."""
    test_files = [
        "test_main.py"
    ]
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--strict-markers"
    ] + test_files
    
    return pytest.main(pytest_args)

def run_all_tests():
    """Run all tests."""
    pytest_args = [
        "-v",
        "--tb=short",
        "--strict-markers",
        str(Path(__file__).parent)
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        pytest_args.extend([
            "--cov=../beta",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        print("📊 运行测试并生成覆盖率报告...")
    except ImportError:
        print("⚠️  pytest-cov不可用，运行测试但不生成覆盖率报告")
    
    return pytest.main(pytest_args)

def run_integration_tests():
    """Run integration tests only."""
    pytest_args = [
        "-v",
        "--tb=short",
        "-k", "integration or Integration",
        str(Path(__file__).parent)
    ]
    
    return pytest.main(pytest_args)

def run_specific_test(test_file=None, test_function=None):
    """Run a specific test file or function."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    beta_dir = project_root / 'beta'
    
    # Add beta directory to Python path
    sys.path.insert(0, str(beta_dir))
    
    cmd = ['python', '-m', 'pytest', '-v']
    
    if test_file:
        test_path = test_dir / test_file
        if test_function:
            cmd.append(f"{test_path}::{test_function}")
        else:
            cmd.append(str(test_path))
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running specific test: {e}")
        return 1

def check_dependencies():
    """Check if required test dependencies are installed."""
    required_packages = ['pytest', 'pytest-asyncio']
    optional_packages = ['pytest-cov']
    
    print("Checking test dependencies...")
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} is missing (required)")
    
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} is missing (optional)")
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install " + ' '.join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("Install with: pip install " + ' '.join(missing_optional))
    
    return True

def main():
    """Main test runner with options."""
    parser = argparse.ArgumentParser(
        description="统一MCP服务器测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
测试类型:
  all        - 运行所有测试（默认）
  main       - 运行主要功能测试
  integration- 运行集成测试
  
示例:
  python run_tests.py
  python run_tests.py main
  python run_tests.py --coverage
        """
    )
    
    parser.add_argument(
        'test_type',
        nargs='?',
        choices=['all', 'main', 'integration'],
        default='all',
        help='要运行的测试类型 (默认: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='生成覆盖率报告'
    )
    
    parser.add_argument(
        '--failfast', '-x',
        action='store_true',
        help='遇到第一个失败就停止'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='检查测试依赖'
    )
    
    args = parser.parse_args()
    
    if args.check_deps:
        print("🔍 检查测试依赖...")
        if not check_dependencies():
            return 1
        return 0
    
    print(f"\n🧪 运行 {args.test_type} 测试...")
    print(f"📁 测试目录: {Path(__file__).parent}")
    print(f"📦 源码目录: {Path(__file__).parent.parent / 'beta'}")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 缺少必需的测试依赖，请先安装")
        return 1
    
    print("\n" + "="*50)
    
    # 根据测试类型运行相应测试
    if args.test_type == 'main':
        print("🔧 运行主要功能测试...")
        exit_code = run_main_tests()
    elif args.test_type == 'integration':
        print("🔗 运行集成测试...")
        exit_code = run_integration_tests()
    else:  # all
        print("📋 运行所有测试...")
        exit_code = run_all_tests()
    
    print("\n" + "="*50)
    
    # 输出结果
    if exit_code == 0:
        print("\n✅ 所有测试通过！")
        if args.coverage:
            print("📊 覆盖率报告已生成到 htmlcov/ 目录")
            print("💡 打开 htmlcov/index.html 查看详细报告")
    else:
        print(f"\n❌ 测试失败，退出码: {exit_code}")
        print("💡 使用 --verbose 查看详细信息")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())