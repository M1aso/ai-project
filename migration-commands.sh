#!/bin/bash
# GitHub Actions Workflow Migration Commands
# Run these commands step by step - DO NOT run as a script

echo "=== Phase 1: Backup & Preparation ==="
echo "1. Create backup branch:"
echo "git checkout -b workflow-migration-backup"
echo "git push origin workflow-migration-backup"
echo ""

echo "2. Create backup files:"
echo "cp .github/workflows/ci.yml .github/workflows/ci-backup.yml"
echo "cp .github/workflows/deploy.yml .github/workflows/deploy-backup.yml"
echo "git add .github/workflows/*-backup.yml"
echo "git commit -m 'backup: Save current workflows before migration'"
echo ""

echo "=== Phase 2: Create Feature Branch ==="
echo "3. Create feature branch:"
echo "git checkout dev"
echo "git pull origin dev"
echo "git checkout -b feature/improve-workflows"
echo ""

echo "=== Phase 3: Prepare New Workflows ==="
echo "4. Rename current workflows:"
echo "mv .github/workflows/ci.yml .github/workflows/ci-old.yml"
echo "mv .github/workflows/deploy.yml .github/workflows/deploy-old.yml"
echo ""

echo "5. You'll need to manually create these 3 new files:"
echo "   - .github/workflows/ci.yml (copy from ci-improved.yml content I provided)"
echo "   - .github/workflows/deploy.yml (copy from deploy-improved.yml content I provided)"  
echo "   - .github/workflows/reusable-deploy.yml (copy from reusable-deploy.yml content I provided)"
echo ""

echo "6. Test commit:"
echo "git add ."
echo "git commit -m 'feat: Improve GitHub Actions workflows - separate CI from deployment'"
echo "git push origin feature/improve-workflows"
echo ""

echo "=== Phase 4: Validation ==="
echo "7. Check GitHub Actions tab for syntax errors"
echo "8. Test manual deployment from Actions tab"
echo ""

echo "=== Phase 5: Safe Deployment ==="
echo "9. Create and merge PR to dev:"
echo "gh pr create --title 'Improve GitHub Actions workflows' --body 'Separates CI from deployment, adds reusable workflows'"
echo ""

echo "10. Monitor dev for 24 hours, then merge to main"
echo ""

echo "=== Phase 6: Cleanup ==="
echo "11. Remove old files:"
echo "git rm .github/workflows/ci-old.yml"
echo "git rm .github/workflows/deploy-old.yml"  
echo "git commit -m 'cleanup: Remove old workflow files'"
echo "git push"
