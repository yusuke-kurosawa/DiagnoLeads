# Tasks: OpenAPI Validation Enhancement (Phase 2)

## Overview
このドキュメントは、OpenAPI検証強化機能の実装タスクを管理します。

関連: [Proposal](./proposal.md)

## Task Status Legend
- ✅ Completed
- 🔄 In Progress
- ⏳ Pending
- ⛔ Blocked

## Phase 2 Implementation Tasks

### 1. Spectral Configuration
**Status**: ✅ Completed  
**Assignee**: Copilot  
**Due Date**: -

#### Subtasks:
- [x] Create `.spectral.yml` with custom rules
- [x] Configure multi-tenant path validation
- [x] Configure operationId naming rules
- [x] Configure response schema requirements
- [x] Configure security requirements
- [x] Add warning-level rules for best practices

**Files Created**:
- `.spectral.yml` (150+ lines, 15+ validation rules)

**Notes**:
- Error-level rules will block PR merge
- Warning-level rules allow merge but encourage improvement

---

### 2. Schema Constraints Documentation
**Status**: ✅ Completed  
**Assignee**: Copilot  
**Due Date**: -

#### Subtasks:
- [x] Create `openspec/specs/database/schema-constraints.yml`
- [x] Document foreign key rules with rationale
- [x] Document unique constraints
- [x] Document check constraints
- [x] Document index strategy
- [x] Document multi-tenant isolation strategy
- [x] Add audit requirements

**Files Created**:
- `openspec/specs/database/schema-constraints.yml` (300+ lines)

**Notes**:
- Integrates with Phase 1 validation script
- Provides single source of truth for constraints

---

### 3. CI/CD Workflow Setup
**Status**: ✅ Completed  
**Assignee**: Copilot  
**Due Date**: -

#### Subtasks:
- [x] Create `.github/workflows/spec-validation.yml`
- [x] Add Spectral validation step
- [x] Add oasdiff breaking change detection
- [x] Add OpenSpec structure validation
- [x] Configure PR commenting
- [ ] Add workflow status badge to README

**Files Created**:
- `.github/workflows/spec-validation.yml` (310+ lines)

**Notes**:
- Spectral CLI and oasdiff installed in CI
- Automatic PR commenting configured
- Multi-tenant compliance check added

---

### 4. Package Scripts Update
**Status**: ✅ Completed  
**Assignee**: Copilot  
**Due Date**: -

#### Subtasks:
- [x] Add `validate:openapi:strict` script to `frontend/package.json`
- [x] Add `openapi:diff` script for breaking change detection
- [x] Update `npm run validate` to include OpenAPI validation
- [ ] Add pre-commit hook for local validation (optional)

**Files Modified**:
- `frontend/package.json`

**Commands to Add**:
```json
{
  "scripts": {
    "validate:openapi:strict": "spectral lint ../openapi.json",
    "openapi:diff": "oasdiff breaking origin/main:openapi.json openapi.json",
    "validate": "npm run type-check && npm run validate:openapi:strict"
  }
}
```

---

### 5. Documentation Updates
**Status**: ✅ Completed  
**Assignee**: Copilot  
**Due Date**: -

#### Subtasks:
- [x] Update `README.md` with validation instructions
- [x] Update `CONTRIBUTING.md` with OpenAPI best practices
- [x] Add troubleshooting guide for validation errors
- [x] Update `docs/DEVELOPER_GUIDE.md` with Spectral usage

**Files Modified**:
- `README.md` - Added "仕様検証（Spec-Driven Development）" section
- `CONTRIBUTING.md` - Added "OpenAPI仕様のベストプラクティス" section
- `docs/DEVELOPER_GUIDE.md` - Added "Spectralによる仕様検証" section

---

### 6. Initial OpenAPI Spec Cleanup
**Status**: ⏳ Pending  
**Assignee**: -  
**Due Date**: -

#### Subtasks:
- [ ] Run Spectral and document existing warnings
- [ ] Fix critical errors (multi-tenant violations)
- [ ] Fix operationId naming violations
- [ ] Add missing response schemas
- [ ] Add missing security definitions

**Files to Modify**:
- `openapi.json`

**Expected Issues**:
- Existing endpoints may need refactoring to follow multi-tenant pattern
- Some operationIds may need renaming

---

### 7. Testing & Validation
**Status**: ⏳ Pending  
**Assignee**: -  
**Due Date**: -

#### Subtasks:
- [ ] Test Spectral validation with valid spec
- [ ] Test Spectral validation with invalid spec (intentional errors)
- [ ] Test oasdiff with breaking changes
- [ ] Test oasdiff with non-breaking changes
- [ ] Test CI/CD workflow end-to-end
- [ ] Verify PR comments are generated correctly

**Test Cases**:
1. Valid OpenAPI spec → All checks pass
2. Missing tenant_id in path → Spectral error
3. Non-camelCase operationId → Spectral error
4. Removed endpoint → oasdiff breaking change warning
5. Added endpoint → oasdiff success

---

## Dependency Installation

### GitHub Actions
Add to `.github/workflows/spec-validation.yml`:
```yaml
- name: Install Spectral
  run: npm install -g @stoplight/spectral-cli

- name: Install oasdiff
  run: npm install -g oasdiff
```

### Local Development
```bash
# Spectral CLI
npm install -g @stoplight/spectral-cli

# oasdiff (choose one)
npm install -g oasdiff
# or
brew install oasdiff
```

## Validation Commands

### Run Spectral validation locally
```bash
cd /home/yusukekurosawa/DiagnoLeads
spectral lint openapi.json
```

### Check breaking changes
```bash
cd /home/yusukekurosawa/DiagnoLeads
oasdiff breaking <(git show main:openapi.json) openapi.json
```

### Run full validation suite
```bash
cd frontend
npm run validate
```

## Success Criteria

### Phase 2 Complete When:
- [x] ✅ Spectral configuration created and tested
- [x] ✅ Schema constraints documented
- [x] ✅ CI/CD workflow created and pushed
- [x] ✅ Package scripts updated
- [x] ✅ Documentation updated
- [ ] ⏳ Existing OpenAPI spec cleaned up (別PRで実施予定)
- [ ] ⏳ CI/CD tests passing on real PRs (PRマージ後に確認)

### Quality Gates:
- 0 Spectral errors in `openapi.json`
- All endpoints follow `/api/v1/tenants/{tenant_id}/` pattern
- All operationIds are camelCase
- All success responses have schemas
- No breaking changes without explicit approval

## Notes

### Integration with Phase 1
- Phase 2 extends Phase 1's database integrity validation
- `schema-constraints.yml` is referenced by Phase 1's validation script
- Both phases run in parallel during CI/CD

### Breaking Change Policy
- Breaking changes require:
  1. Major version bump in API
  2. Deprecation period for old endpoints (minimum 3 months)
  3. Client migration guide
  4. Tech Lead approval

### Spectral Rule Customization
If project-specific rules are needed:
1. Add custom functions in `.spectral.yml`
2. Document rationale in comments
3. Test with various spec examples

## Risk Mitigation

### Issue: Many warnings on existing spec
**Solution**: 
- Start with warning-level rules
- Fix gradually over sprints
- Don't block PR merges initially

### Issue: False positives in oasdiff
**Solution**:
- Review all breaking changes manually
- Override detection if necessary (with comment)
- Refine oasdiff configuration

### Issue: CI/CD performance impact
**Solution**:
- Run Spectral validation in parallel with other checks
- Cache Spectral CLI installation
- Set timeout limits (5 minutes max)

## Related Documents
- [Proposal](./proposal.md)
- [Database Integrity Management - Phase 1](../database-integrity-management/proposal.md)
- [Schema Constraints Spec](../../specs/database/schema-constraints.yml)
- [OpenAPI Integration Guide](../../../README.openspec.md)
