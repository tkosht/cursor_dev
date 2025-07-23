# .env File Security Violation Prevention Rules

**Created**: 2025-07-22
**Context**: Security violation occurred when AI displayed .env file contents containing API keys

## 🚨 ABSOLUTE RULES

### 1. FORBIDDEN ACTIONS
```bash
# NEVER execute these commands
FORBIDDEN_ENV_COMMANDS=(
    "cat .env"
    "cat */.env"
    "head .env"
    "tail .env"
    "less .env"
    "more .env"
    "vim .env"
    "nano .env"
    "code .env"
    "grep -v '^#' .env"  # Even filtered output is forbidden
)
```

### 2. ALLOWED VERIFICATION METHODS
```bash
# ONLY these methods are permitted for .env verification
ALLOWED_ENV_CHECKS=(
    "ls -la .env"                    # Check file existence only
    "test -f .env && echo 'exists'"  # Boolean existence check
    "wc -l .env"                      # Line count only
    "stat .env"                       # File metadata only
)
```

### 3. API KEY VERIFICATION
```bash
# Verify API key presence WITHOUT exposing values
function verify_api_keys() {
    # Method 1: Check if set (boolean only)
    python -c "import os; print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
    
    # Method 2: Check key length
    python -c "import os; key = os.getenv('GOOGLE_API_KEY', ''); print(f'Key length: {len(key)}')"
    
    # Method 3: Masked display (first/last chars only)
    python -c "
import os
key = os.getenv('GOOGLE_API_KEY', '')
if key and len(key) > 10:
    print(f'Key: {key[:6]}...{key[-4:]}')
else:
    print('Key: NOT SET or TOO SHORT')
"
}
```

## 🔒 SECURITY PRINCIPLES

1. **Never Display Full Secrets**: Even partial display should be minimal
2. **Verify Functionality, Not Content**: Test that APIs work, not what keys contain
3. **Use Exit Codes**: Prefer boolean checks over value display
4. **Audit Trail**: All .env access attempts should be logged

## ✅ CORRECT PATTERNS

### Pattern 1: Functional Verification
```python
# Test LLM connection without showing keys
async def verify_llm_connection():
    try:
        llm = create_llm()
        response = await llm.ainvoke("test")
        print("✅ LLM connection successful")
        return True
    except Exception as e:
        print(f"❌ LLM connection failed: {type(e).__name__}")
        return False
```

### Pattern 2: Environment Validation
```bash
# Validate environment setup
function validate_env_setup() {
    local missing=()
    
    # Check required variables
    for var in GOOGLE_API_KEY OPENAI_API_KEY; do
        if [[ -z "${!var}" ]]; then
            missing+=("$var")
        fi
    done
    
    if [[ ${#missing[@]} -eq 0 ]]; then
        echo "✅ All required environment variables are set"
        return 0
    else
        echo "❌ Missing variables: ${missing[*]}"
        return 1
    fi
}
```

### Pattern 3: Safe Configuration Display
```python
# Display configuration without secrets
def show_safe_config():
    config = get_config()
    safe_config = {
        "provider": config.llm.provider,
        "model": config.llm.gemini_model,
        "api_key_set": bool(config.llm.google_api_key),
        "api_key_length": len(config.llm.google_api_key or ""),
    }
    print(json.dumps(safe_config, indent=2))
```

## 🚫 VIOLATION CONSEQUENCES

1. **Immediate Task Termination**: Stop all work if violation detected
2. **Security Incident Report**: Document in memory-bank/07-security/
3. **User Notification**: Inform user of security breach
4. **Review Required**: Cannot proceed without security review

## 📋 IMPLEMENTATION CHECKLIST

When working with sensitive configuration:

1. ✓ Check file existence without reading content
2. ✓ Verify API functionality through actual calls
3. ✓ Use masked/hashed representations if display needed
4. ✓ Implement try-except blocks to catch errors
5. ✓ Log successes/failures without exposing secrets
6. ✓ Document security considerations in code comments

## 🔍 MONITORING

Add to pre-commit hooks:
```bash
# Detect potential .env exposure in commits
if git diff --cached --name-only | xargs grep -l "\.env" | grep -v ".example"; then
    echo "⚠️  Warning: Potential .env file reference detected"
    echo "Verify no secrets are being exposed"
fi
```

## 📚 REFERENCES

- CLAUDE.md Section 2: SECURITY ABSOLUTE
- memory-bank/07-security/security_rules_enhancement.md
- memory-bank/00-core/code_quality_anti_hacking.md

---

**Remember**: Security is not just about following rules, but understanding the principles behind them. When in doubt, err on the side of caution and never expose sensitive information.