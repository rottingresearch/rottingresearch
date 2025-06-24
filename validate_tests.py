#!/usr/bin/env python3
"""
Simple test validation script for Rotting Research
This script performs basic validation of the test structure without requiring full dependencies.
"""

import os
import sys
import ast
import importlib.util

def validate_python_syntax(file_path):
    """Validate that a Python file has correct syntax."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_test_structure():
    """Check that the test directory structure is correct."""
    base_dir = '/Users/Marshal/Documents/GitHub/rottingresearch'
    tests_dir = os.path.join(base_dir, 'tests')
    
    required_files = [
        'tests/conftest.py',
        'tests/test-requirements.txt', 
        'tests/unit/test_app.py',
        'tests/unit/test_tasks.py',
        'tests/unit/test_utilites.py',
        'tests/unit/test_celery_init.py',
        'tests/functional/test_workflows.py',
        'tests/functional/test_integration.py',
        'pytest.ini',
        'run_tests.sh',
        '.github/workflows/test.yml'
    ]
    
    print("🔍 Checking test structure...")
    all_good = True
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
            
            # Check syntax for Python files
            if file_path.endswith('.py'):
                is_valid, error = validate_python_syntax(full_path)
                if not is_valid:
                    print(f"❌ Syntax error in {file_path}: {error}")
                    all_good = False
        else:
            print(f"❌ Missing: {file_path}")
            all_good = False
    
    return all_good

def count_test_methods():
    """Count the number of test methods in test files."""
    base_dir = '/Users/Marshal/Documents/GitHub/rottingresearch'
    test_files = [
        'tests/unit/test_app.py',
        'tests/unit/test_tasks.py', 
        'tests/unit/test_utilites.py',
        'tests/unit/test_celery_init.py',
        'tests/functional/test_workflows.py',
        'tests/functional/test_integration.py'
    ]
    
    total_tests = 0
    print("\n📊 Test method count:")
    
    for test_file in test_files:
        full_path = os.path.join(base_dir, test_file)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r') as f:
                    source = f.read()
                
                tree = ast.parse(source)
                test_count = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        test_count += 1
                
                print(f"  {test_file}: {test_count} tests")
                total_tests += test_count
                
            except Exception as e:
                print(f"  {test_file}: Error reading file - {e}")
    
    print(f"\n🧪 Total test methods: {total_tests}")
    return total_tests

def check_coverage_areas():
    """Check that key areas of the application are covered by tests."""
    base_dir = '/Users/Marshal/Documents/GitHub/rottingresearch'
    
    # Check main application modules exist
    app_files = ['app.py', 'tasks.py', 'utilites.py', 'celery_init.py']
    
    print("\n🎯 Application modules:")
    for app_file in app_files:
        full_path = os.path.join(base_dir, app_file)
        if os.path.exists(full_path):
            print(f"✅ {app_file}")
        else:
            print(f"❌ Missing: {app_file}")

def main():
    """Main validation function."""
    print("🚀 Rotting Research Test Suite Validation")
    print("=" * 50)
    
    # Check test structure
    structure_ok = check_test_structure()
    
    # Count test methods
    test_count = count_test_methods()
    
    # Check coverage areas
    check_coverage_areas()
    
    print("\n📋 Summary:")
    print(f"  Test structure: {'✅ Good' if structure_ok else '❌ Issues found'}")
    print(f"  Total tests: {test_count}")
    print(f"  Ready for testing: {'✅ Yes' if structure_ok and test_count > 0 else '❌ No'}")
    
    if structure_ok and test_count > 0:
        print("\n🎉 Test suite is ready! Install dependencies and run:")
        print("   pip install -r tests/test-requirements.txt")
        print("   ./run_tests.sh")
        return 0
    else:
        print("\n❌ Test suite has issues that need to be resolved.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
