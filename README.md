# Sales Follow-Up Email Generator

This project uses the OpenAI API to generate sales follow-up emails from the evaluation cases in `eval_set.json`.

## How to run

### 1. Install dependencies

```bash
pip install openai
```

### 2. Set your API key

The app expects an `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 3. Run the app

Run all evaluation cases:

```bash
python app.py
```

Run a single case:

```bash
python app.py --case 1
```

## What the script does

- Loads cases from `eval_set.json`
- Sends each case to the OpenAI Responses API using `gpt-4o`
- Prints the generated email to the terminal
- Saves all generated outputs to `outputs.txt`

## Notes

- If `OPENAI_API_KEY` is missing, the script exits with an error.
- If `--case` does not match a valid case ID, the script exits and shows the available IDs.

VIDEO_LINK: TODO
