"""
parser.py — This file breaks raw log lines into useful pieces.
"""


def parse_line(raw_line):
    """
    Takes one raw log line and breaks it into 3 parts:
    - timestamp
    - level
    - message

    Example input:
        "2026-10-17 10:02:03 ERROR Database connection failed"

    Example output:
        {"timestamp": "2026-10-17 10:02:03",
         "level": "ERROR",
         "message": "Database connection failed"}
    """

    # .split(" ", 3) splits the text by spaces, but stops after 3 splits
    parts = raw_line.strip().split(" ", 3)

    # Check if we got at least 4 pieces (timestamp has 2 words + level + message)
    if len(parts) < 4:
        return None  # Line is malformed, skip it

    return {
        "timestamp": parts[0] + " " + parts[1],  # date and time are two words
        "level": parts[2],                         # INFO, WARN, or ERROR
        "message": parts[3]                        # everything else
    }


def parse_file(raw_lines):
    """
    Takes a list of raw log lines and returns a list of parsed dictionaries.
    Any malformed lines are skipped.
    """

    parsed_logs = []

    for line in raw_lines:
        result = parse_line(line)
        if result is not None:
            parsed_logs.append(result)

    return parsed_logs