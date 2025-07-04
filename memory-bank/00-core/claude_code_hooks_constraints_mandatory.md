# Claude Code Hooks Constraints (MANDATORY)

**KEYWORDS**: hooks, claude-code, posix, sh, bash, constraints, mandatory
**DOMAIN**: claude-code-system
**PRIORITY**: MANDATORY
**WHEN**: Any hooks script creation, modification, or troubleshooting

## 🚨 ABSOLUTE CONSTRAINT (絶対制約)

**RULE**: Claude Code hooks scripts MUST be written in POSIX sh-compatible format ONLY.

**ENFORCEMENT**: Claude Code executes ALL hooks scripts using `/bin/sh`, NOT user's `$SHELL` or script shebang.

## 📋 Technical Analysis (技術的分析)

### Execution Environment
- **Actual Executor**: `/bin/sh` (typically `dash` on Ubuntu)
- **User's SHELL**: `/bin/bash` 
- **Script Shebang**: `#!/bin/bash` (IGNORED by Claude Code)
- **Result**: Shebang mismatch → Compatibility errors

### Why /bin/sh is Used by Claude Code

**Design Rationale** (Claude Code developers' choice):

1. **Compatibility**: `/bin/sh` exists on ALL Unix systems (POSIX standard)
2. **Security**: Limited shell features reduce security risks
3. **Performance**: `dash` is lighter and faster than `bash`
4. **Predictability**: Avoids user-specific bash configurations (.bashrc)
5. **Portability**: Same behavior across different environments

## ❌ FORBIDDEN in Hooks Scripts

**Bash-specific Features** (Will FAIL in /bin/sh):

```bash
# ❌ FORBIDDEN - Double brackets
if [[ "$var" == "value" ]]; then

# ❌ FORBIDDEN - Arrays  
array=(a b c)
echo "${array[0]}"

# ❌ FORBIDDEN - Bash regex operator
if [[ "$string" =~ pattern ]]; then

# ❌ FORBIDDEN - Process substitution
while read line; do echo "$line"; done < <(command)

# ❌ FORBIDDEN - Brace expansion
echo {1..10}

# ❌ FORBIDDEN - Bash-specific variables
echo "$BASH_VERSION"
```

## ✅ REQUIRED POSIX sh Format

**Correct Format** (POSIX compatible):

```bash
#!/bin/sh

# ✅ CORRECT - Single brackets
if [ "$var" = "value" ]; then
    echo "OK"
fi

# ✅ CORRECT - Traditional test
if [ -f "$file" ] && [ -r "$file" ]; then
    echo "File exists and readable"
fi

# ✅ CORRECT - Case statement for pattern matching
case "$string" in
    *pattern*) echo "Match found" ;;
    *) echo "No match" ;;
esac

# ✅ CORRECT - POSIX variable expansion
echo "${var:-default_value}"
```

## 🔧 Current Problem Status

**Problem Identified** (2025-07-05):
- ALL existing hooks scripts use bash syntax (`[[ ]]`, arrays, etc.)
- Error: `/bin/sh: 1: script.sh: not found` due to compatibility issues
- **Required Action**: Rewrite ALL hooks scripts in POSIX sh format

**Affected Scripts Count**: 15+ scripts in `.claude/hooks/`

## 📋 Conversion Checklist

**Before Hooks Script Deployment**:

1. **Shebang**: Use `#!/bin/sh` (not `#!/bin/bash`)
2. **Test Command**: Replace `[[ ]]` with `[ ]`
3. **String Comparison**: Use `=` instead of `==`
4. **Arrays**: Avoid or use space-separated strings
5. **Regex**: Use `case` patterns instead of `=~`
6. **Variables**: Use POSIX-compliant expansions only

**Validation Process**:
```bash
# Test script in sh environment
/bin/sh -n script.sh                    # Syntax check
/bin/sh script.sh                       # Execution test
shellcheck -s sh script.sh              # Static analysis
```

## 🎯 Future Maintenance Protocol

**MANDATORY Check** before any hooks modification:

1. **Constraint Verification**: Confirm POSIX sh compatibility
2. **Syntax Validation**: Test with `/bin/sh -n`
3. **Execution Test**: Run in `/bin/sh` environment  
4. **Cross-Reference**: Check this document for forbidden patterns

**Integration Points**:
- Pre-commit validation for `.claude/hooks/` changes
- Documentation updates for new team members
- CI/CD pipeline checks for hooks syntax

## 🔗 Related Knowledge

**See Also**:
- `/memory-bank/00-core/user_authorization_mandatory.md` - Security context
- `/memory-bank/02-organization/tmux_claude_agent_organization.md` - Hooks usage context
- Claude Code Documentation: Hooks configuration

**Reference Links**:
- POSIX Shell Standard: IEEE Std 1003.1
- Bash vs POSIX sh differences
- shellcheck tool for validation

## 📊 Impact Assessment

**Risk if Ignored**:
- 🚨 Hooks execution failures
- 🚨 Development workflow disruption  
- 🚨 Inconsistent behavior across environments
- 🚨 Time waste on troubleshooting

**Benefit of Compliance**:
- ✅ Reliable hooks execution
- ✅ Cross-platform compatibility
- ✅ Predictable behavior
- ✅ Reduced maintenance overhead

---

**ENFORCEMENT NOTE**: This constraint is NON-NEGOTIABLE. Any hooks script using bash-specific features WILL fail in Claude Code environment.

**LAST UPDATED**: 2025-07-05 (Investigation completed)
**NEXT REVIEW**: When Claude Code hooks implementation changes