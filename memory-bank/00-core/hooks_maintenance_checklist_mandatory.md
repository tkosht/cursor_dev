# Claude Code Hooks Maintenance Checklist (MANDATORY)

**KEYWORDS**: hooks, maintenance, checklist, claude-code, validation, posix
**DOMAIN**: claude-code-system
**PRIORITY**: MANDATORY
**WHEN**: Before creating, modifying, or deploying ANY hooks script

## 🚨 PRE-WORK MANDATORY VALIDATION

**CRITICAL**: Execute EVERY step before hooks script changes

### Phase 1: Constraint Verification (絶対実行)

```bash
# 1. Load hooks constraints knowledge
echo "📚 Loading: memory-bank/00-core/claude_code_hooks_constraints_mandatory.md"
[ -f "memory-bank/00-core/claude_code_hooks_constraints_mandatory.md" ] || {
    echo "🚨 CRITICAL: Hooks constraints file missing!"
    exit 1
}

# 2. Verify /bin/sh execution environment
echo "🔍 Verifying execution environment:"
echo "System sh: $(readlink -f /bin/sh)"
echo "User shell: $SHELL"
ls -la /bin/sh

# 3. Check available validation tools
echo "🛠️ Validation tools check:"
which shellcheck && echo "✅ shellcheck available"
which bash && echo "✅ bash available for testing"
```

### Phase 2: Script Analysis (新規・修正前)

```bash
# 4. Identify bash-specific patterns in existing/new script
SCRIPT_PATH="$1"  # Pass script path as argument

echo "🔍 Scanning for bash-specific patterns in: $SCRIPT_PATH"

# Check for forbidden patterns
echo "❌ Forbidden pattern check:"
grep -n '\[\[' "$SCRIPT_PATH" && echo "FOUND: Double brackets [[ ]]"
grep -n '==' "$SCRIPT_PATH" && echo "FOUND: Bash comparison =="  
grep -n 'array=' "$SCRIPT_PATH" && echo "FOUND: Array assignment"
grep -n '=~' "$SCRIPT_PATH" && echo "FOUND: Regex operator =~"
grep -n '\${.*\[.*\]}' "$SCRIPT_PATH" && echo "FOUND: Array access"
grep -n 'declare\|local' "$SCRIPT_PATH" && echo "FOUND: Bash-specific declarations"
grep -n '\$BASH_' "$SCRIPT_PATH" && echo "FOUND: Bash-specific variables"

if [ $? -eq 0 ]; then
    echo "🚨 BASH-SPECIFIC PATTERNS DETECTED - CONVERSION REQUIRED"
else
    echo "✅ No obvious bash-specific patterns detected"
fi
```

### Phase 3: Syntax Validation (修正後)

```bash
# 5. POSIX sh syntax check
echo "🔧 POSIX sh syntax validation:"
/bin/sh -n "$SCRIPT_PATH"
if [ $? -eq 0 ]; then
    echo "✅ POSIX sh syntax valid"
else
    echo "🚨 SYNTAX ERROR - Fix required before deployment"
    exit 1
fi

# 6. shellcheck validation (if available)
if which shellcheck >/dev/null 2>&1; then
    echo "🔍 shellcheck analysis:"
    shellcheck -s sh "$SCRIPT_PATH"
    if [ $? -eq 0 ]; then
        echo "✅ shellcheck validation passed"
    else
        echo "⚠️ shellcheck warnings detected - Review recommended"
    fi
else
    echo "⚠️ shellcheck not available - manual review required"
fi
```

### Phase 4: Execution Testing (デプロイ前)

```bash
# 7. Test execution in /bin/sh environment
echo "🧪 Execution test in /bin/sh:"

# Create test environment variables
export TEST_VAR="test_value"
export FILE_PATH="/tmp/test_file"
touch "$FILE_PATH"

# Execute script in sh environment
echo "Running: /bin/sh $SCRIPT_PATH"
/bin/sh "$SCRIPT_PATH"
EXIT_CODE=$?

# Cleanup
rm -f "$FILE_PATH"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Execution test passed in /bin/sh"
else
    echo "🚨 EXECUTION FAILED in /bin/sh - Fix required"
    exit 1
fi
```

## 📋 Conversion Guidelines (bash → POSIX sh)

### Common Conversions Required

```bash
# ❌ BASH (Forbidden)           →  ✅ POSIX sh (Required)

# Double brackets              →  Single brackets
[[ "$var" == "value" ]]       →  [ "$var" = "value" ]
[[ -n "$var" ]]               →  [ -n "$var" ]

# String comparison            →  Use single =
if [[ "$a" == "$b" ]]         →  if [ "$a" = "$b" ]

# Regex matching               →  Use case statement
[[ "$str" =~ pattern ]]       →  case "$str" in *pattern*) ;; esac

# Arrays                       →  Use space-separated strings
arr=(a b c)                   →  arr="a b c"
echo "${arr[0]}"              →  set -- $arr; echo "$1"

# Local variables              →  Use global or function args
local var="value"             →  var="value"  # or use $1, $2, etc.

# Process substitution         →  Use temp files
while read line; do           →  command > /tmp/file
  echo "$line"                →  while read line; do
done < <(command)             →    echo "$line"
                              →  done < /tmp/file; rm /tmp/file
```

## 🔧 Deployment Checklist (Final Validation)

**MANDATORY** before committing hooks changes:

- [ ] **Constraint Review**: Read `claude_code_hooks_constraints_mandatory.md`
- [ ] **Shebang Check**: Use `#!/bin/sh` (not `#!/bin/bash`)
- [ ] **Syntax Validation**: `/bin/sh -n script.sh` passes
- [ ] **Pattern Scan**: No bash-specific patterns detected
- [ ] **Execution Test**: Script runs successfully in `/bin/sh`
- [ ] **shellcheck**: No critical errors (if available)
- [ ] **Functionality**: Script performs intended function
- [ ] **Error Handling**: Proper exit codes and error messages
- [ ] **Environment**: Script doesn't depend on bash-specific env vars

## 🚨 Emergency Procedures

### If Hooks Fail After Deployment

```bash
# 1. Immediate diagnosis
echo "🚨 Hooks failure diagnosed - checking constraints"

# 2. Quick syntax check
for script in /home/devuser/workspace/.claude/hooks/*.sh; do
    echo "Checking: $script"
    /bin/sh -n "$script" || echo "SYNTAX ERROR: $script"
done

# 3. Check execution environment
echo "Environment check:"
echo "Executing shell: $(readlink -f /bin/sh)"
echo "Current shell: $0"

# 4. Test individual script
FAILING_SCRIPT="$1"
echo "Testing: $FAILING_SCRIPT"
/bin/sh -x "$FAILING_SCRIPT"  # Debug mode
```

### Recovery Process

1. **Identify failing script** from error message
2. **Run syntax check**: `/bin/sh -n script.sh`
3. **Apply conversion guidelines** above
4. **Re-test with validation checklist**
5. **Deploy corrected version**

## 📊 Success Metrics

**Validation Success Criteria**:
- ✅ 0 syntax errors in `/bin/sh -n`
- ✅ 0 bash-specific patterns detected
- ✅ Script executes successfully in `/bin/sh`
- ✅ Intended functionality preserved
- ✅ No Claude Code hooks execution errors

**Performance Targets**:
- Validation time: <2 minutes per script
- Zero deployment failures due to syntax
- 100% POSIX sh compatibility

---

**USAGE EXAMPLE**:
```bash
# Full validation workflow
./hooks_maintenance_checklist_mandatory.md /path/to/new_hook.sh
# Follow all steps in order - NO SHORTCUTS
```

**ENFORCEMENT**: Any hooks script deployed without completing this checklist is a PROTOCOL VIOLATION.

**LAST UPDATED**: 2025-07-05 (Initial creation)