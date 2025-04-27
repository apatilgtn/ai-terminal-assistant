#!/usr/bin/env python3

import argparse
import os
import sys
import yaml
import subprocess
from anthropic import Anthropic, APIError, APIStatusError

# --- Configuration ---
CONFIG_FILE_NAME = "config.yaml"
# Determine the script's directory to find the config file reliably
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILE_NAME)

# --- Helper Functions ---
def print_debug(message):
    """Prints debug message if debug_mode is enabled."""
    if CONFIG.get('debug_mode', False):
        print(f"\033[90m[DEBUG] {message}\033[0m", file=sys.stderr)

def load_config():
    """Loads configuration from YAML file."""
    print_debug(f"Looking for config at: {CONFIG_PATH}")
    if not os.path.exists(CONFIG_PATH):
        print(f"\033[91mError: Configuration file not found at {CONFIG_PATH}\033[0m", file=sys.stderr)
        print("Please copy config.yaml.template to config.yaml and add your API key.", file=sys.stderr)
        sys.exit(1)
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        print_debug("Config loaded successfully.")
        # Basic validation
        if not config.get('api_provider') or not config.get(config['api_provider'], {}).get('api_key'):
             raise ValueError("API provider or API key missing in config.")
        if config[config['api_provider']]['api_key'].startswith("YOUR_") or config[config['api_provider']]['api_key'] == "":
             raise ValueError(f"API key for {config['api_provider']} seems to be a placeholder. Please update config.yaml.")
        return config
    except yaml.YAMLError as e:
        print(f"\033[91mError parsing configuration file {CONFIG_PATH}: {e}\033[0m", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\033[91mConfiguration Error: {e}\033[0m", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mError loading configuration: {e}\033[0m", file=sys.stderr)
        sys.exit(1)

def call_anthropic_api(prompt):
    """Calls the Anthropic API and returns the response text."""
    provider_config = CONFIG.get('anthropic', {})
    api_key = provider_config.get('api_key')
    model = provider_config.get('model', 'claude-3-sonnet-20240229')
    max_tokens = provider_config.get('max_tokens', 500)
    temperature = provider_config.get('temperature', 0.5)

    if not api_key:
        print("\033[91mError: Anthropic API key not found in config.\033[0m", file=sys.stderr)
        return None

    try:
        print_debug(f"Calling Anthropic API. Model: {model}, Max Tokens: {max_tokens}, Temp: {temperature}")
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system="You are a helpful AI assistant integrated into a user's terminal. Provide concise and accurate explanations or shell commands. Format commands clearly, often in code blocks.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print_debug("API call successful.")
        # Accessing the response text correctly for Claude 3 messages API
        if message.content and isinstance(message.content, list) and message.content[0].type == 'text':
             return message.content[0].text.strip()
        else:
             print_debug(f"Unexpected API response structure: {message.content}")
             return "Error: Received unexpected response format from API."

    except APIStatusError as e:
        print(f"\n\033[91mAnthropic API Error (Status {e.status_code}): {e.message}\033[0m", file=sys.stderr)
        if e.status_code == 401:
            print("\033[91mCheck if your API key is correct and has permissions.\033[0m", file=sys.stderr)
        return None
    except APIError as e:
        print(f"\n\033[91mAnthropic API Error: {e}\033[0m", file=sys.stderr)
        return None
    except Exception as e:
        print(f"\n\033[91mAn unexpected error occurred during API call: {e}\033[0m", file=sys.stderr)
        return None

def call_ai_api(prompt):
    """Dispatcher function to call the configured AI provider."""
    provider = CONFIG.get('api_provider', 'anthropic') # Default to anthropic
    print_debug(f"Using API provider: {provider}")

    if provider == "anthropic":
        return call_anthropic_api(prompt)
    elif provider == "openai":
        print("\033[93mOpenAI support is not fully implemented yet.\033[0m", file=sys.stderr)
        # Placeholder for OpenAI call
        # return call_openai_api(prompt)
        return "OpenAI support not ready."
    else:
        print(f"\033[91mError: Unknown API provider '{provider}' configured.\033[0m", file=sys.stderr)
        return None

def format_ai_response(response_text, title="AI Assistant"):
    """Formats the AI response for printing to the terminal."""
    print(f"\n\033[1;36m🤖 {title}:\033[0m") # Bold Cyan title
    # Simple formatting - could be enhanced (e.g., markdown parsing)
    for line in response_text.splitlines():
        print(f"   {line}")
    print() # Add a newline at the end


# --- Command Handlers ---

def handle_chat(args):
    """Handles the 'chat' command."""
    query = " ".join(args.query)
    if not query:
        print("\033[91mError: Please provide a question for the chat.\033[0m", file=sys.stderr)
        sys.exit(1)

    print_debug(f"Chat query: {query}")
    prompt = f"The user asked the following question in their terminal: '{query}'. Provide a helpful answer or relevant command(s)."
    response = call_ai_api(prompt)
    if response:
        format_ai_response(response, title="AI Chat")

def handle_fix_error(command, exit_code, is_automatic=False):
    """Handles fixing the last command error."""
    if not command:
        print("\033[91mError: Could not determine the command that failed.\033[0m", file=sys.stderr)
        return # Don't exit if called automatically

    print_debug(f"Fix error requested for command: '{command}' (Exit code: {exit_code}, Automatic: {is_automatic})")

    # If automatic, check config before proceeding
    if is_automatic and not CONFIG.get('auto_fix_errors', False):
        print_debug("Automatic error fixing is disabled in config. Skipping.")
        return

    prompt = (
        f"The following shell command failed with exit code {exit_code}:\n"
        f"```\n{command}\n```\n"
        f"Explain the likely reason for the error and suggest one or more specific commands to fix it or achieve the user's likely intent. "
        f"If it's a simple typo, point it out. Be concise."
    )
    response = call_ai_api(prompt)
    if response:
        format_ai_response(response, title=f"AI Fix Suggestion (for `{command}`)")

def handle_build(args):
     """Handles the 'build' command (Not Implemented)."""
     print("\033[93mSorry, the 'build' command (generating commands from description) is not yet implemented.\033[0m")


# --- Main Execution ---

# Load configuration globally first
try:
    CONFIG = load_config()
except SystemExit:
     # If config loading fails critically, exit before parsing args
     sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="AI Terminal Assistant")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Chat Command ---
    # Handles both `ai chat ...` and `ai ...` (if no other command matches)
    parser_chat = subparsers.add_parser('chat', help='Chat with the AI assistant (default if no command specified)')
    parser_chat.add_argument('query', nargs='+', help='Your question or prompt for the AI')

    # --- Fix Command (Manual) ---
    parser_fix = subparsers.add_parser('fix', help='Analyze the last failed command and suggest a fix')
    # No arguments needed here, the shell script will provide context if needed,
    # or we can try to fetch from history (more complex)

    # --- Build Command (Future) ---
    parser_build = subparsers.add_parser('build', help='Build a shell command from a description (future)')
    parser_build.add_argument('description', nargs='+', help='Description of the command to build')

    # --- Internal Command for Hooks (Not for direct user use) ---
    parser_internal_fix = subparsers.add_parser('--internal-fix-error', help=argparse.SUPPRESS)
    parser_internal_fix.add_argument('--command', required=True, help='The failed command string')
    parser_internal_fix.add_argument('--exit_code', required=True, help='The exit code of the failed command')

    # --- Parse Arguments ---
    # Need to handle the case where no subcommand is given, defaulting to 'chat'
    args = None
    try:
        # Check if the first arg looks like a command or just the start of a chat query
        known_commands = ['chat', 'fix', 'build', '--internal-fix-error']
        if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith('-'):
             # Assume it's a chat query, insert 'chat' command
             sys.argv.insert(1, 'chat')
        args = parser.parse_args()
    except SystemExit:
        # Argparse exits if help is requested, etc. Allow this.
         pass
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)


    if not args or not hasattr(args, 'command') or args.command is None:
         # If no command was successfully parsed (e.g., just `ai` or `ai -h`), show help
         if len(sys.argv) <= 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
              parser.print_help()
         else:
              # Should have been handled by inserting 'chat' earlier, but as fallback:
              print("Invalid usage. Try 'ai chat <query>' or 'ai fix'. Use 'ai --help' for details.", file=sys.stderr)
         sys.exit(1)


    # --- Execute Command ---
    if args.command == 'chat':
        handle_chat(args)
    elif args.command == 'fix':
        # Manual fix: Try to get last command from Zsh history (simplistic)
        try:
            # This fetches the *last* command line entry, might not be the *failed* one
            # A more robust solution involves the shell hook passing info via temp file or env var
            # For simplicity now, we rely on the internal hook or user running `ai fix` right after failure
            result = subprocess.run(['fc', '-ln', '-1'], capture_output=True, text=True, check=True, shell=True)
            last_cmd = result.stdout.strip()
            # We don't reliably know the exit code here for manual `ai fix` without shell help
            # Let's default to 'unknown' or prompt the AI differently
            print_debug(f"Manual 'fix' invoked. Last command from history: {last_cmd}")
            handle_fix_error(last_cmd, exit_code="unknown", is_automatic=False) # Trigger manually
        except Exception as e:
            print(f"\033[91mError retrieving last command from history: {e}\033[0m", file=sys.stderr)
            print("Please run 'ai fix' immediately after a command fails for best results.", file=sys.stderr)

    elif args.command == 'build':
        handle_build(args)
    elif args.command == '--internal-fix-error':
        handle_fix_error(args.command, args.exit_code, is_automatic=True) # Triggered by hook

if __name__ == "__main__":
    main()
