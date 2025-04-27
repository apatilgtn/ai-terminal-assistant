# Zsh setup script for AI Terminal Assistant

# --- Configuration ---
# Try to automatically determine the directory containing this script
# If this fails, manually set the path:
# export AI_ASSISTANT_DIR="/path/to/your/ai-terminal-assistant"
if [[ -z "$AI_ASSISTANT_DIR" ]]; then
    export AI_ASSISTANT_DIR="${${(%):-%x}:A:h}" # Zsh magic to get script dir
fi

# Path to the main Python script
local AI_ASSISTANT_SCRIPT="$AI_ASSISTANT_DIR/ai_assistant.py"
# Path to the Python interpreter (use 'python3' or path from venv if active)
local AI_PYTHON_EXEC="python3"
if [[ -n "$VIRTUAL_ENV" ]]; then
    AI_PYTHON_EXEC="$VIRTUAL_ENV/bin/python"
    # echo "[AI Setup] Using Python from venv: $AI_PYTHON_EXEC" # Optional debug
fi


# --- Check if script exists ---
if [[ ! -x "$AI_ASSISTANT_SCRIPT" ]]; then
    echo "[AI Assistant Setup] Warning: Script not found or not executable at $AI_ASSISTANT_SCRIPT" >&2
    return 1
fi
# Check if Python interpreter exists
if ! command -v "$AI_PYTHON_EXEC" > /dev/null; then
     echo "[AI Assistant Setup] Warning: Python interpreter '$AI_PYTHON_EXEC' not found." >&2
     return 1
fi


# --- Main `ai` command alias/function ---
# This function acts as the entry point for the user
ai() {
    # Just pass all arguments directly to the Python script
    "$AI_PYTHON_EXEC" "$AI_ASSISTANT_SCRIPT" "$@"
}

# --- Automatic Error Fix Hook ---
# This function runs before each prompt (precmd)
_ai_assistant_error_hook() {
    local exit_code=$? # Capture the exit code of the last command

    # Only proceed if the last command failed (non-zero exit code)
    # And the exit code is not 130 (Ctrl+C interrupt)
    if [[ $exit_code -eq 0 || $exit_code -eq 130 ]]; then
        return
    fi

    # Get the last command from history (most recent entry)
    # `fc -ln -1` gets the last command line
    # `sed 's/^[[:space:]]*//'` removes leading whitespace often added by fc
    local last_cmd=$(fc -ln -1 | sed 's/^[[:space:]]*//')

    # Avoid triggering the hook on the assistant's own commands or internal calls
    # Check if last command starts with 'ai ' or the internal call itself
    # Needs refinement if python script path is complex
    if [[ "$last_cmd" == ai* ]] || [[ "$last_cmd" == "$AI_PYTHON_EXEC $AI_ASSISTANT_SCRIPT --internal-fix-error"* ]]; then
       # echo "[AI Hook Debug] Ignoring assistant's own command: $last_cmd" >&2 # Optional Debug
        return
    fi

    # Call the Python script with internal flags to handle the error analysis
    # This allows the Python script to check its own config (e.g., auto_fix_errors)
    # Run in background (&) to avoid blocking the prompt, but output might interleave weirdly.
    # Run synchronously for simpler output handling:
    "$AI_PYTHON_EXEC" "$AI_ASSISTANT_SCRIPT" --internal-fix-error --command "$last_cmd" --exit_code "$exit_code"

}

# --- Register Hook ---
# Load Zsh add-zsh-hook function if not already available
autoload -Uz add-zsh-hook

# Register the function to run before the prompt is displayed
add-zsh-hook precmd _ai_assistant_error_hook

# Optional: Print a message when setup is sourced
# echo "[AI Assistant] Loaded. Type 'ai --help' for usage."
