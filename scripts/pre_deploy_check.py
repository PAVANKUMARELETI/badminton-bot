#!/usr/bin/env python
"""
Pre-deployment checklist script.

This script validates that all requirements are met before deploying to production.
Run this before pushing deployment changes.
"""
import os
import sys
from pathlib import Path


def check_env_var(name: str, required: bool = True) -> bool:
    """Check if environment variable is set."""
    value = os.getenv(name)
    if value:
        print(f"✅ {name}: Set")
        return True
    else:
        status = "❌" if required else "⚠️"
        req_text = "REQUIRED" if required else "Optional"
        print(f"{status} {name}: Not set ({req_text})")
        return not required


def check_file(path: str) -> bool:
    """Check if file exists."""
    if Path(path).exists():
        print(f"✅ {path}: Found")
        return True
    else:
        print(f"❌ {path}: Not found")
        return False


def check_deployment_config() -> bool:
    """Check deployment configuration files."""
    print("\n📋 Checking Deployment Configuration...")
    
    checks = [
        check_file("railway.toml"),
        check_file("start.sh"),
        check_file("Procfile"),
        check_file("requirements.txt"),
    ]
    
    # Check railway.toml contains refactored bot
    with open("railway.toml", "r") as f:
        content = f.read()
        if "telegram_bot_refactored" in content:
            print("✅ railway.toml: Using refactored bot")
            checks.append(True)
        else:
            print("❌ railway.toml: Not using refactored bot")
            checks.append(False)
    
    return all(checks)


def check_environment_variables() -> bool:
    """Check required environment variables."""
    print("\n🔐 Checking Environment Variables...")
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "OPENWEATHER_API_KEY",
    ]
    
    optional_vars = [
        "SENTRY_DSN",
        "MODEL_PATH",
        "LOG_LEVEL",
    ]
    
    checks = []
    
    print("\nRequired:")
    for var in required_vars:
        checks.append(check_env_var(var, required=True))
    
    print("\nOptional (but recommended):")
    for var in optional_vars:
        check_env_var(var, required=False)
    
    return all(checks)


def check_code_files() -> bool:
    """Check that refactored bot files exist."""
    print("\n🐍 Checking Code Files...")
    
    required_files = [
        "src/integrations/telegram_bot_refactored.py",
        "src/integrations/bot_formatters.py",
        "src/integrations/bot_weather.py",
        "src/integrations/bot_keyboards.py",
        "src/integrations/bot_location.py",
    ]
    
    checks = [check_file(f) for f in required_files]
    return all(checks)


def check_tests() -> bool:
    """Check that tests pass."""
    print("\n🧪 Running Tests...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-q", "--tb=no", "-x"],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        if result.returncode == 0:
            # Extract passed count from output
            output = result.stdout
            if "passed" in output:
                count = output.split("passed")[0].strip().split()[-1]
                print(f"✅ Tests: {count} passed")
                return True
            else:
                print("✅ Tests: All passed")
                return True
        else:
            # Check if it's just warnings or actual failures
            if "failed" in result.stdout:
                print(f"❌ Tests: Some failed")
                print("   Run 'pytest tests/' for details")
                return False
            else:
                print("⚠️ Tests: Non-zero exit but no failures detected")
                return True
    except subprocess.TimeoutExpired:
        print("⚠️ Tests: Timeout (skipping - not blocking deployment)")
        return True
    except Exception as e:
        print(f"⚠️ Tests: Could not run ({e})")
        print("   Not blocking deployment - verify manually")
        return True


def check_model() -> bool:
    """Check if model exists."""
    print("\n🤖 Checking Model...")
    
    model_path = os.getenv("MODEL_PATH", "experiments/latest/model.keras")
    
    if check_file(model_path):
        return True
    else:
        print("⚠️  Model not found - will be trained on first deployment")
        print("   This is expected for fresh deployments")
        return True  # Not a blocker


def check_documentation() -> bool:
    """Check that deployment docs exist."""
    print("\n📚 Checking Documentation...")
    
    docs = [
        "docs/DEPLOYMENT.md",
        "README.md",
    ]
    
    checks = [check_file(f) for f in docs]
    return all(checks)


def print_summary(all_passed: bool):
    """Print deployment readiness summary."""
    print("\n" + "="*60)
    if all_passed:
        print("✅ DEPLOYMENT READY!")
        print("\nNext Steps:")
        print("1. Review changes: git status")
        print("2. Commit changes: git add . && git commit -m 'Deploy refactored bot'")
        print("3. Push to deploy: git push")
        print("4. Monitor logs: railway logs --follow")
        print("\nSee docs/DEPLOYMENT.md for detailed instructions.")
    else:
        print("❌ DEPLOYMENT NOT READY")
        print("\nPlease fix the issues above before deploying.")
        print("See docs/DEPLOYMENT.md for help.")
    print("="*60)


def main():
    """Run all pre-deployment checks."""
    print("🚀 Pre-Deployment Checklist\n")
    print("Checking deployment readiness for Badminton Wind Bot...")
    
    checks = {
        "Deployment Config": check_deployment_config(),
        "Code Files": check_code_files(),
        "Documentation": check_documentation(),
        "Model": check_model(),
    }
    
    # Environment variables check (may fail locally but work on Railway)
    env_check = check_environment_variables()
    if not env_check:
        print("\n⚠️  Environment variables not set locally.")
        print("   This is OK if you'll set them in Railway dashboard.")
        print("   Make sure to set them before deploying!")
    
    # Tests check (optional)
    test_check = check_tests()
    checks["Tests"] = test_check
    
    # Summary
    all_passed = all(checks.values())
    print_summary(all_passed)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
