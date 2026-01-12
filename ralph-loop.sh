#!/bin/bash
# Ralph Loop - Autonomous AI development with deliberate context rotation
# Based on Geoffrey Huntley's Ralph Wiggum technique
# https://ghuntley.com/ralph/

set -e

# Configuration
MAX_ITERATIONS=${MAX_ITERATIONS:-20}
TASK_FILE="RALPH_TASK.md"
PROGRESS_FILE=".ralph/progress.md"
GUARDRAILS_FILE=".ralph/guardrails.md"
ACTIVITY_LOG=".ralph/activity.log"
ERRORS_LOG=".ralph/errors.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure we're in project root
cd "$(dirname "$0")"

# Initialize Ralph files if they don't exist
init_ralph() {
    mkdir -p .ralph

    if [ ! -f "$TASK_FILE" ]; then
        echo -e "${RED}Error: $TASK_FILE not found${NC}"
        echo "Create RALPH_TASK.md with your task definition and success criteria"
        exit 1
    fi

    if [ ! -f "$GUARDRAILS_FILE" ]; then
        echo "# Ralph Guardrails" > "$GUARDRAILS_FILE"
        echo "Add learned constraints here as Signs." >> "$GUARDRAILS_FILE"
    fi

    if [ ! -f "$PROGRESS_FILE" ]; then
        echo "# Progress Log" > "$PROGRESS_FILE"
        echo "Last updated: $(date '+%Y-%m-%d')" >> "$PROGRESS_FILE"
    fi
}

# Log activity
log_activity() {
    echo "[$(date '+%Y-%m-%d %H:%M')] $1" >> "$ACTIVITY_LOG"
}

# Log error
log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M')] ERROR: $1" >> "$ERRORS_LOG"
}

# Check if all success criteria are met
check_completion() {
    # Count unchecked boxes [ ] vs checked [x]
    local unchecked=$(grep -c '\[ \]' "$TASK_FILE" 2>/dev/null || echo "0")
    if [ "$unchecked" -eq 0 ]; then
        return 0  # Complete
    fi
    return 1  # Not complete
}

# Build the prompt for Claude
build_prompt() {
    cat << EOF
# Ralph Iteration $(($iteration + 1))

Read these files to understand current state:
1. RALPH_TASK.md - Task definition and success criteria
2. .ralph/progress.md - What's been done
3. .ralph/guardrails.md - Learned constraints (MUST follow these)
4. .ralph/errors.log - Past errors to avoid

Your job:
1. Read the current state from files
2. Identify the next unchecked [ ] item in RALPH_TASK.md
3. Complete that item
4. Update .ralph/progress.md with what you did
5. Mark the item as [x] in RALPH_TASK.md when done
6. If you encounter an error, add a Sign to .ralph/guardrails.md

Important:
- Work on ONE item at a time
- Test your changes before marking complete
- Commit progress to git after each significant change
- If stuck, add a Sign explaining the blocker

Current working directory: $(pwd)
EOF
}

# Main loop
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Ralph Loop - CyraSoul Content Agent  ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    init_ralph

    iteration=0

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        echo -e "${YELLOW}--- Iteration $((iteration + 1)) of $MAX_ITERATIONS ---${NC}"
        log_activity "ITERATION: Starting iteration $((iteration + 1))"

        # Check if task is complete
        if check_completion; then
            echo -e "${GREEN}All success criteria met! Task complete.${NC}"
            log_activity "COMPLETE: All criteria met"
            exit 0
        fi

        # Build and run prompt
        echo -e "${BLUE}Running Claude Code...${NC}"

        # The core Ralph loop - pipe prompt to Claude
        prompt=$(build_prompt)

        # Run Claude Code with the prompt
        # Note: Adjust this command based on your Claude Code installation
        echo "$prompt" | claude --dangerously-skip-permissions 2>&1 | tee -a "$ACTIVITY_LOG"

        exit_code=$?

        if [ $exit_code -ne 0 ]; then
            echo -e "${RED}Claude exited with error code $exit_code${NC}"
            log_error "Claude exit code $exit_code"
        fi

        # Commit progress after each iteration
        if git status --porcelain | grep -q .; then
            echo -e "${BLUE}Committing progress...${NC}"
            git add -A
            git commit -m "Ralph iteration $((iteration + 1)): $(date '+%Y-%m-%d %H:%M')" || true
        fi

        iteration=$((iteration + 1))

        # Brief pause between iterations
        echo -e "${YELLOW}Rotating context... (fresh start)${NC}"
        sleep 2
    done

    echo -e "${RED}Max iterations ($MAX_ITERATIONS) reached${NC}"
    echo "Review .ralph/progress.md for current state"
    log_activity "LIMIT: Max iterations reached"
    exit 1
}

# Handle arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: ./ralph-loop.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help"
        echo "  --status       Show current progress"
        echo "  --reset        Reset Ralph state (keeps guardrails)"
        echo ""
        echo "Environment variables:"
        echo "  MAX_ITERATIONS  Maximum loop iterations (default: 20)"
        ;;
    --status)
        echo "=== Current Progress ==="
        cat "$PROGRESS_FILE" 2>/dev/null || echo "No progress file"
        echo ""
        echo "=== Unchecked Items ==="
        grep '\[ \]' "$TASK_FILE" 2>/dev/null || echo "All items complete!"
        ;;
    --reset)
        echo "Resetting Ralph state..."
        rm -f "$PROGRESS_FILE" "$ACTIVITY_LOG"
        echo "# Progress Log" > "$PROGRESS_FILE"
        echo "Last updated: $(date '+%Y-%m-%d')" >> "$PROGRESS_FILE"
        echo "Reset complete. Guardrails preserved."
        ;;
    *)
        main
        ;;
esac
