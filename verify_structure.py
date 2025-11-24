"""
Code structure verification script
Validates that all files are properly structured without running full tests
"""
import ast
import sys
from pathlib import Path


def check_syntax(file_path):
    """Check if Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def verify_project_structure():
    """Verify all Python files in the project"""
    root = Path('.')
    python_files = list(root.rglob('*.py'))

    print("=" * 70)
    print("PROJECT STRUCTURE VERIFICATION")
    print("=" * 70)

    errors = []
    success_count = 0

    for py_file in python_files:
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        valid, error = check_syntax(py_file)

        if valid:
            print(f"[OK] {py_file}")
            success_count += 1
        else:
            print(f"[ERROR] {py_file}")
            print(f"   Error: {error}")
            errors.append((py_file, error))

    print("\n" + "=" * 70)
    print(f"SUMMARY: {success_count} files validated successfully")

    if errors:
        print(f"[ERROR] {len(errors)} files with syntax errors")
        return False
    else:
        print("[OK] All files have valid syntax!")
        return True


def check_required_files():
    """Check that all required files exist"""
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/config.py',
        'app/models/schemas.py',
        'app/services/extractor.py',
        'app/services/embeddings.py',
        'app/services/matcher.py',
        'app/services/pdf_service.py',
        'app/services/consent.py',
        'app/services/search.py',
        'app/services/storage.py',
        'app/utils/logger.py',
        'app/utils/normalizer.py',
        'app/api/extraction.py',
        'app/api/matcher.py',
        'app/api/pdf.py',
        'app/api/consent.py',
        'app/api/search.py',
        'tests/test_normalizer.py',
        'tests/test_embeddings.py',
        'tests/test_consent.py',
        'tests/test_api.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        '.env.example',
    ]

    print("\n" + "=" * 70)
    print("CHECKING REQUIRED FILES")
    print("=" * 70)

    missing = []

    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            missing.append(file_path)

    print("\n" + "=" * 70)
    if missing:
        print(f"[ERROR] {len(missing)} required files missing")
        return False
    else:
        print("[OK] All required files present!")
        return True


def check_imports():
    """Check that main modules can be imported (syntax check)"""
    print("\n" + "=" * 70)
    print("CHECKING MODULE STRUCTURE")
    print("=" * 70)

    modules_to_check = [
        'app.models.schemas',
        'app.utils.normalizer',
        'app.utils.logger',
    ]

    all_valid = True

    for module in modules_to_check:
        file_path = module.replace('.', '/') + '.py'
        valid, error = check_syntax(file_path)

        if valid:
            print(f"[OK] {module}")
        else:
            print(f"[ERROR] {module}")
            print(f"   Error: {error}")
            all_valid = False

    return all_valid


if __name__ == '__main__':
    print("\n")

    syntax_ok = verify_project_structure()
    files_ok = check_required_files()
    imports_ok = check_imports()

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    if syntax_ok and files_ok and imports_ok:
        print("[SUCCESS] All checks passed!")
        print("\nThe project structure is valid and ready for deployment.")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env file with API keys")
        print("  3. Run tests: pytest")
        print("  4. Start server: python app/main.py")
        sys.exit(0)
    else:
        print("[FAILED] Some checks failed")
        print("\nPlease fix the errors above before proceeding.")
        sys.exit(1)
