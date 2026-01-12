# Ralph Guardrails - Learned Constraints

This file contains "Signs" - lessons learned from failures that prevent the same mistake from happening twice.

---

## Infrastructure Signs

### Sign: Qdrant API version compatibility
- **Trigger**: Using Qdrant client search methods
- **Instruction**: Use `query_points()` instead of deprecated `search()`. Access results via `results.points` not `results` directly.
- **Added after**: Iteration 1 - AttributeError on 'search' method

### Sign: Environment variable inline comments
- **Trigger**: Writing .env files
- **Instruction**: NEVER put inline comments in .env files. Comments on same line as values get parsed as part of the value. Use separate lines for comments.
- **Added after**: Iteration 1 - SSL error caused by `QDRANT_API_KEY=  # comment` being read as non-empty

### Sign: Qdrant local connection
- **Trigger**: Connecting to local Qdrant
- **Instruction**: For local Docker Qdrant, explicitly use `url=f"http://{host}:{port}"` not just host/port. Empty API key should be `None`, not empty string.
- **Added after**: Iteration 1 - SSL WRONG_VERSION_NUMBER error

### Sign: Voyage AI rate limits
- **Trigger**: Embedding multiple chunks
- **Instruction**: Free tier has 3 RPM limit. Add delays between requests or batch carefully. Consider chunking indexing into smaller batches.
- **Added after**: Iteration 1 - 429 rate limit errors during indexing

---

## Code Quality Signs

### Sign: Read files before editing
- **Trigger**: Modifying any existing file
- **Instruction**: ALWAYS read the file first to understand current state. Never assume file contents.
- **Added after**: Best practice

### Sign: Test after changes
- **Trigger**: Making code changes
- **Instruction**: Run relevant tests after each significant change. Don't batch multiple changes before testing.
- **Added after**: Best practice

---

## Content Generation Signs

### Sign: Turkish character handling
- **Trigger**: Processing Turkish text
- **Instruction**: Ensure UTF-8 encoding everywhere. Turkish has special characters: ş, ğ, ü, ö, ç, ı, İ
- **Added after**: Anticipated issue

### Sign: Health claims verification
- **Trigger**: Writing wellness content
- **Instruction**: HIPPOCRATES must verify all health claims before publishing. Add "Bir sağlık uzmanına danışın" for medical advice.
- **Added after**: From content guardrails

---

## Git Signs

### Sign: Never commit .env
- **Trigger**: Running git add
- **Instruction**: Verify .gitignore excludes .env before any commit. API keys must never be in git history.
- **Added after**: Security best practice

### Sign: Check git status before commit
- **Trigger**: Creating commits
- **Instruction**: Always run `git status` and `git diff` before committing to verify what's being committed.
- **Added after**: Best practice

---

## Adding New Signs

When Ralph makes a mistake:
1. Identify the root cause
2. Add a new Sign here with:
   - Clear trigger condition
   - Specific instruction to prevent recurrence
   - Context of when it was added
3. Commit the updated guardrails

Format:
```markdown
### Sign: [Short description]
- **Trigger**: [When this applies]
- **Instruction**: [What to do instead]
- **Added after**: [Context/iteration]
```
