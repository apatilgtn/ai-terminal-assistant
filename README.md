# AI Terminal Assistant

A lightweight AI-powered assistant for your macOS terminal (initially focused on Zsh), inspired by Warp's AI features. Get help fixing command errors, ask questions about shell commands, and interact with an AI directly within your existing terminal workflow.



## 🚀 What This Project Does

*   ✅ **AI Chat:** Ask natural language questions directly in your terminal (e.g., `ai "how do I find large files?"`).
*   ✅ **Error Auto-Fix:** Optionally, automatically get AI explanations and suggested fixes when a terminal command fails.
*   ✅ **Manual Error Fix:** Manually trigger AI analysis of the last executed command using `ai fix`.
*   ✅ **Inline Output:** AI responses are displayed directly below your commands.
*   ✅ **Configurable:** Choose your AI provider (Anthropic initially supported), model, and toggle features via a simple YAML file.
*   ✅ **Integrates with *your* shell:** Works as a helper within your existing Zsh setup, not a full terminal replacement.

## ✨ Key Features

*   **Chat Interface:** Use `ai [chat] <your question>` to ask for commands, explanations, or general help.
*   **Automatic Error Detection:** The assistant hooks into Zsh's `precmd` to detect non-zero exit codes.
*   **Contextual Error Fixing:** When fixing errors, it sends the failed command and exit code to the AI for better suggestions.
*   **Simple Setup:** Requires Python 3 and involves adding one line to your `.zshrc`.
*   **Extensible:** Designed with future enhancements in mind (e.g., command building, other shells, local LLMs).

##📋 Requirements

*   **macOS:** Developed and tested on macOS.
*   **Python 3:** Version 3.7 or higher recommended. Check with `python3 --version`.
*   **Pip:** Python package installer. Check with `pip3 --version`.
*   **Zsh:** The default shell on recent macOS versions.
*   **API Key:** An API key from a supported AI provider (currently Anthropic - Claude). Get one from [console.anthropic.com](https://console.anthropic.com/).

## ⚙️ Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url> # Replace with your repo URL
    cd ai-terminal-assistant
    ```

2.  **Create and Activate Virtual Environment (Recommended):**
    This keeps dependencies isolated from your system Python.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *(You'll need to run `source venv/bin/activate` in each new terminal session where you want to use the `ai` command).*

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # or use pip3 if pip points to Python 2
    # pip3 install -r requirements.txt
    ```

4.  **Configure API Key:**
    *   Copy the template:
        ```bash
        cp config.yaml.template config.yaml
        ```
    *   **Edit `config.yaml`:** Open the `config.yaml` file in a text editor.
    *   Find the `anthropic` section and replace `"YOUR_ANTHROPIC_API_KEY_HERE"` with your actual Anthropic API key.
    *   (Optional) Adjust the `model`, `max_tokens`, or `temperature` if desired.
    *   (Optional) Set `auto_fix_errors` to `false` if you don't want automatic suggestions on errors.
    *   **Secure your key:** It's crucial **never to commit your `config.yaml` file with the API key** to version control (the `.gitignore` file should ideally list `config.yaml`). Restrict its permissions:
        ```bash
        chmod 600 config.yaml
        ```

5.  **Integrate with Zsh:**
    *   Add the following line to the **very end** of your `~/.zshrc` file. Make sure the path points to the correct location where you cloned the repository. The `~` symbol represents your home directory (`/Users/your_username`).
        ```bash
        # Add this line to the end of ~/.zshrc
        source ~/path/to/your/ai-terminal-assistant/.ai_assistant_setup.zsh
        ```
        *(Example: If you cloned it directly into your home folder, the path would be `~/ai-terminal-assistant/.ai_assistant_setup.zsh`)*
    *   You can edit `~/.zshrc` using `nano ~/.zshrc`, `vim ~/.zshrc`, or `open -e ~/.zshrc`.

6.  **Reload Shell Configuration:**
    Apply the changes to your current session:
    ```bash
    source ~/.zshrc
    ```
    Or simply **open a new terminal window/tab**.

## 🚀 Usage

**(Remember to activate your virtual environment first: `source venv/bin/activate` if you used one)**

*   **Chat with AI:**
    ```bash
    # Ask for a command
    ai "list all files ending in .log sorted by modification time"

    # Ask for an explanation
    ai chat "explain what 'chmod 755' means"

    # General questions
    ai "what is the current version of nodejs LTS?"
    ```
    *(The `chat` subcommand is optional if your query is the first argument)*

*   **Manual Error Fix:**
    1. Run a command that fails (e.g., `gti status` instead of `git status`).
    2. Immediately run:
       ```bash
       ai fix
       ```
    3. The assistant will analyze the last command from your history and provide suggestions.

*   **Automatic Error Fix (if enabled):**
    1. Set `auto_fix_errors: true` in `config.yaml`.
    2. Run a command that fails.
    3. The assistant should automatically print an explanation and suggestion below the error message before your next prompt appears.

## 🔧 Configuration (`config.yaml`)

*   `api_provider`: Currently supports `"anthropic"`. (Future: `"openai"`).
*   `anthropic`:
    *   `api_key`: **Required**. Your secret key.
    *   `model`: Which Claude model to use (e.g., `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`).
    *   `max_tokens`: Max length of the AI's response.
    *   `temperature`: Controls creativity (0.0 = deterministic, 1.0 = more creative).
*   `openai`: (Placeholder for future implementation).
*   `auto_fix_errors`: `true` or `false`. Enables/disables automatic suggestions on command errors.
*   `debug_mode`: `true` or `false`. Set to `true` to see verbose debugging messages from the scripts.

## ⚠️ Troubleshooting

*   **`zsh: command not found: ai`**:
    *   Did you run `source ~/.zshrc` or open a new terminal after adding the line to `.zshrc`?
    *   Check the `source` path in your `.zshrc` file – does it exactly match the location of `.ai_assistant_setup.zsh`?
    *   Did the `source ~/.zshrc` command itself produce any errors? Fix them first.
    *   If using a virtual environment, is it active (`source venv/bin/activate`)?
    *   Run `which ai`. It should output `ai: function`.

*   **`ModuleNotFoundError: No module named 'yaml'` (or `anthropic`, `requests`)**:
    *   Did you install the dependencies using `pip install -r requirements.txt`?
    *   If using a virtual environment, is it active in the current terminal session?

*   **API Errors (e.g., 401 Unauthorized, AuthenticationError)**:
    *   Double-check that the `api_key` in your `config.yaml` is correct and doesn't have typos.
    *   Ensure you copied the *entire* key.
    *   Verify your Anthropic account is active and has credits/permissions.
    *   Check the [Anthropic Status Page](https://status.anthropic.com/) for outages.

*   **`NameError: name 'CONFIG' is not defined`**:
    *   Ensure you are using the latest version of the `ai_assistant.py` script provided, which includes the fix for initializing `CONFIG`.

*   **Permission Denied errors**:
    *   Make sure the Python script is executable (though it's usually run via `python3 script.py`, so this is less common). `chmod +x ai_assistant.py`.
    *   Check permissions on `config.yaml` if errors occur during loading.

## 💡 Future Ideas & Contributing

*   Implement `ai build "<description>"` to generate commands.
*   Add support for other shells (Bash `PROMPT_COMMAND`, Fish `event`).
*   Integrate with local LLMs (via Ollama, LMStudio).
*   Improve context awareness (e.g., current directory, previous commands).
*   Add unit and integration tests.

Contributions are welcome! Feel free to open issues or submit pull requests.

##📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (you'll need to create a LICENSE file containing the standard MIT license text).
