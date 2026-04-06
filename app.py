import argparse
import json
import os
from pathlib import Path
from textwrap import indent

from openai import OpenAI


SYSTEM_PROMPT = (
    "You are a helpful sales assistant. Write a polished sales follow-up email "
    "based only on the provided case details. Keep the tone professional and "
    "warm, keep the email concise, and structure it with a clear opening, a "
    "brief value-oriented middle, and a direct closing call to action. Never "
    "invent facts, names, dates, pricing, commitments, or next steps that are "
    "not provided in the input. If important information is missing, explicitly "
    "note the gap instead of guessing."
)

MODEL = "gpt-4o"
EVAL_SET_PATH = Path("eval_set.json")
OUTPUTS_PATH = Path("outputs.txt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate follow-up emails for one or more eval cases."
    )
    parser.add_argument(
        "--case",
        dest="case_id",
        help="Optional case ID to run. If omitted, all cases are processed.",
    )
    return parser.parse_args()


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as infile:
        return json.load(infile)


def select_cases(cases: list[dict], case_id: str | None) -> list[dict]:
    if case_id is None:
        return cases

    selected = [case for case in cases if case.get("id") == case_id]
    if not selected:
        available_ids = ", ".join(case.get("id", "<missing-id>") for case in cases)
        raise SystemExit(
            f"Case '{case_id}' not found in {EVAL_SET_PATH}. Available IDs: {available_ids}"
        )
    return selected


def summarize_input(case_input: dict) -> str:
    lines = []
    for key, value in case_input.items():
        label = key.replace("_", " ").title()
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


def build_user_prompt(case: dict) -> str:
    case_input = case["input"]
    return (
        "Write a sales follow-up email for the case below.\n\n"
        f"Case ID: {case['id']}\n"
        f"Input:\n{summarize_input(case_input)}\n\n"
        f"Good output criteria:\n{case['good_output_criteria']}\n"
    )


def generate_email(client: OpenAI, case: dict) -> str:
    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=build_user_prompt(case),
    )
    return response.output_text.strip()


def format_section(case: dict, generated_email: str) -> str:
    input_summary = summarize_input(case["input"])
    return (
        f"===== Case ID: {case['id']} =====\n"
        "Input Summary:\n"
        f"{indent(input_summary, '  ')}\n\n"
        "Generated Email:\n"
        f"{indent(generated_email, '  ')}\n"
    )


def main() -> None:
    args = parse_args()
    cases = select_cases(load_cases(EVAL_SET_PATH), args.case_id)
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set.")
    client = OpenAI()

    sections = []
    for case in cases:
        generated_email = generate_email(client, case)
        section = format_section(case, generated_email)
        sections.append(section)
        print(section)

    OUTPUTS_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"Saved outputs to {OUTPUTS_PATH}")


if __name__ == "__main__":
    main()
