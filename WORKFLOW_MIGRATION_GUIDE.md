# GitHub Actions Workflow Migration Guide

## 🚨 IMPORTANT: Follow this guide exactly to avoid breaking deployments

## Current State
- `ci.yml` - 521 lines, handles both CI and deployment
- `deploy.yml` - Manual deployment workflow
- Both workflows have duplicate deployment logic

## Target State
- `ci-improved.yml` - Pure CI with deployment triggers
- `deploy-improved.yml` - Unified deployment workflow
- `reusable-deploy.yml` - Reusable deployment logic

## Migration Steps

### Phase 1: Backup & Preparation ⏱️ 5 mins

1. **Create backup branch:**
   ```bash
   git checkout -b workflow-migration-backup
   git push origin workflow-migration-backup
   ```

2. **Document current workflow files:**
   ```bash
   cp .github/workflows/ci.yml .github/workflows/ci-backup.yml
   cp .github/workflows/deploy.yml .github/workflows/deploy-backup.yml
   git add .github/workflows/*-backup.yml
   git commit -m "backup: Save current workflows before migration"
   ```

### Phase 2: Test New Workflows ⏱️ 15 mins

1. **Create feature branch:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/improve-workflows
   ```

2. **Remove improved workflow files (they're already created):**
   ```bash
   rm .github/workflows/ci-improved.yml
   rm .github/workflows/deploy-improved.yml  
   rm .github/workflows/reusable-deploy.yml
   ```

3. **Rename current workflows temporarily:**
   ```bash
   mv .github/workflows/ci.yml .github/workflows/ci-old.yml
   mv .github/workflows/deploy.yml .github/workflows/deploy-old.yml
   ```

4. **Add new workflows with correct names:**
   - Copy content from `ci-improved.yml` → `ci.yml`
   - Copy content from `deploy-improved.yml` → `deploy.yml`
   - Copy content from `reusable-deploy.yml` → `reusable-deploy.yml`

5. **Test commit (won't trigger deployment):**
   ```bash
   git add .
   git commit -m "test: Add improved workflows for testing"
   git push origin feature/improve-workflows
   ```

### Phase 3: Validate Workflows ⏱️ 10 mins

1. **Check workflow syntax:**
   - Go to GitHub Actions tab
   - Look for syntax errors in new workflows
   - Fix any YAML issues

2. **Test manual deployment:**
   - Go to Actions → Deploy workflow
   - Click "Run workflow"
   - Select: environment=dev, service=auth
   - Verify it runs without errors

### Phase 4: Safe Migration ⏱️ 5 mins

1. **Create pull request:**
   ```bash
   # From feature branch
   gh pr create --title "Improve GitHub Actions workflows" --body "Separates CI from deployment, adds reusable workflows"
   ```

2. **Merge to dev first:**
   - Merge PR to dev branch
   - Monitor dev deployments for 24 hours

3. **Merge to main:**
   - Create PR from dev to main
   - Merge after dev validation

### Phase 5: Cleanup ⏱️ 2 mins

1. **Remove old workflow files:**
   ```bash
   git rm .github/workflows/ci-old.yml
   git rm .github/workflows/deploy-old.yml
   git commit -m "cleanup: Remove old workflow files"
   ```

## Rollback Plan (if needed)

If something breaks:

1. **Immediate rollback:**
   ```bash
   git checkout main
   cp .github/workflows/ci-backup.yml .github/workflows/ci.yml
   cp .github/workflows/deploy-backup.yml .github/workflows/deploy.yml
   git add .github/workflows/ci.yml .github/workflows/deploy.yml
   git commit -m "rollback: Restore original workflows"
   git push origin main
   ```

2. **Remove new files:**
   ```bash
   git rm .github/workflows/reusable-deploy.yml
   git commit -m "rollback: Remove new workflow files"
   git push origin main
   ```

## Validation Checklist

After migration, verify:

- [ ] Push to dev triggers CI and auto-deployment
- [ ] Push to main triggers CI and auto-deployment to staging
- [ ] Manual deployment works for all environments
- [ ] All services deploy successfully
- [ ] No duplicate workflow runs
- [ ] Proper error handling and notifications

## Key Differences

### Before (Current)
- CI workflow does everything (521 lines)
- Duplicate deployment code
- Only dev gets auto-deployed
- Complex, hard to maintain

### After (Improved)
- CI only does CI, triggers deployments
- Single deployment workflow (DRY)
- All environments get auto-deployed
- Modular, maintainable, reusable

## Environment Setup Required

Ensure these secrets exist for each environment (dev, staging, prod):
- `KUBE_CONFIG` - Base64 encoded kubeconfig
- `GHCR_USERNAME` - GitHub Container Registry username
- `GHCR_TOKEN` - GitHub Container Registry token

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Compare with backup workflows
3. Use rollback plan if needed
4. Test in feature branch first
