# Runbook: Deployment Rollback

## When to Use
- New deployment caused issues
- Critical bug in production
- Need to revert quickly

## Quick Rollback (Railway)

```bash
# In Railway dashboard:
# 1. Go to Deployments
# 2. Find last working deployment
# 3. Click "Rollback"
```

## Git Rollback

### Find Last Good Commit
```bash
git log --oneline -10
```

### Rollback Locally
```bash
# Revert to specific commit
git revert HEAD

# Or reset (destructive)
git reset --hard <commit-hash>
```

### Deploy Rollback
```bash
git push origin main --force  # Use with caution!
```

## Verify Rollback

1. Check server status: `/api/status`
2. Test critical paths
3. Monitor logs

## Post-Rollback

1. Document what went wrong
2. Create fix in separate branch
3. Test thoroughly before re-deploying
