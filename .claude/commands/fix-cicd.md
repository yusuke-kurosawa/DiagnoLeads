# Fix CI/CD Errors

Analyze and fix errors from the latest failed CI/CD run.

## Steps

1. Check if there are any error analysis reports in `cicd-errors/`
2. If reports exist, read the latest one
3. If no reports exist, prompt the user to run: `./scripts/analyze-cicd-errors.sh`
4. Analyze the errors and categorize them:
   - Syntax errors
   - Type errors
   - Test failures
   - Linter violations
   - Build errors
5. For each error:
   - Identify the file and line number
   - Explain the root cause
   - Propose a fix
   - Implement the fix if appropriate
6. After fixing all errors:
   - Ask if the user wants to run tests locally
   - Suggest committing and pushing changes

## Important Notes

- Always read the full error log before making changes
- Check for related errors (cascading failures)
- Verify fixes don't break other parts of the codebase
- Run appropriate tests before committing
- Use the existing code style and patterns

## Quick Commands

After analyzing errors, you can use these commands to verify fixes:

### Backend
```bash
cd backend
ruff check --fix .
ruff format .
mypy app/
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm run lint -- --fix
npx tsc --noEmit
npm run build
npm test
```
