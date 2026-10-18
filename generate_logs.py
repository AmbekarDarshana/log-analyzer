"""
generate_logs.py — Creates realistic fake log files for testing.

Simulates a web application running for 2 hours, with three
deliberate incidents injected at known times so we can verify
whether our anomaly detection catches them.
"""

import random
from datetime import datetime, timedelta


# ---------------------------------------------------------------
# MESSAGE POOLS — realistic things a web app would log
# ---------------------------------------------------------------

NORMAL_INFO = [
    "User login successful",
    "Page /home loaded",
    "Page /products loaded",
    "Session created",
    "Health check passed",
    "Cache hit for product list",
    "New user registered",
    "Profile updated",
    "Search query executed",
    "User logged out",
]

NORMAL_WARN = [
    "Cache miss, fetching from database",
    "Slow query detected 850ms",
    "Session nearing expiry",
    "Deprecated API endpoint used",
]

DB_ERRORS = [
    "Database connection failed",
    "Connection pool exhausted",
    "Query timeout after 30s",
    "Transaction rollback triggered",
]

AUTH_ERRORS = [
    "Failed login attempt for user admin",
    "Invalid credentials provided",
    "Account locked after repeated failures",
    "Suspicious login from unknown IP",
]

LATENCY_WARNINGS = [
    "Response time 3200ms exceeds threshold",
    "Upstream service responding slowly",
    "Request queue backing up",
    "Thread pool saturation detected",
]


# ---------------------------------------------------------------
# HELPER — format one log line
# ---------------------------------------------------------------

def make_line(timestamp, level, message):
    """
    Builds a single log line in the exact format our parser expects:
    "YYYY-MM-DD HH:MM:SS LEVEL Message text here"
    """
    time_text = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"{time_text} {level} {message}"


# ---------------------------------------------------------------
# TRAFFIC PATTERNS — what happens in a given minute
# ---------------------------------------------------------------

def normal_minute(minute_start):
    """
    A healthy minute: 5-12 requests, almost all INFO,
    occasionally one WARN.
    """
    lines = []
    count = random.randint(5, 12)

    for _ in range(count):
        second = random.randint(0, 59)
        moment = minute_start + timedelta(seconds=second)

        # 92% chance INFO, 8% chance WARN
        if random.random() < 0.92:
            lines.append(make_line(moment, "INFO", random.choice(NORMAL_INFO)))
        else:
            lines.append(make_line(moment, "WARN", random.choice(NORMAL_WARN)))

    return lines


def database_outage_minute(minute_start):
    """
    INCIDENT 1: The database goes down.
    Heavy burst of ERROR lines, very little normal traffic.
    """
    lines = []
    count = random.randint(25, 40)

    for _ in range(count):
        second = random.randint(0, 59)
        moment = minute_start + timedelta(seconds=second)

        roll = random.random()
        if roll < 0.75:
            lines.append(make_line(moment, "ERROR", random.choice(DB_ERRORS)))
        elif roll < 0.92:
            lines.append(make_line(moment, "WARN", "Retrying database connection"))
        else:
            lines.append(make_line(moment, "INFO", random.choice(NORMAL_INFO)))

    return lines


def brute_force_minute(minute_start):
    """
    INCIDENT 2: Someone is attacking the login page.
    Very high request volume, mostly failed authentication.
    """
    lines = []
    count = random.randint(50, 80)

    for _ in range(count):
        second = random.randint(0, 59)
        moment = minute_start + timedelta(seconds=second)

        roll = random.random()
        if roll < 0.85:
            lines.append(make_line(moment, "ERROR", random.choice(AUTH_ERRORS)))
        else:
            lines.append(make_line(moment, "WARN", "Rate limit threshold approaching"))

    return lines


def latency_spike_minute(minute_start):
    """
    INCIDENT 3: The system slows down badly.
    Normal volume, but dominated by latency warnings.
    """
    lines = []
    count = random.randint(8, 15)

    for _ in range(count):
        second = random.randint(0, 59)
        moment = minute_start + timedelta(seconds=second)

        roll = random.random()
        if roll < 0.60:
            lines.append(make_line(moment, "WARN", random.choice(LATENCY_WARNINGS)))
        elif roll < 0.80:
            lines.append(make_line(moment, "ERROR", "Timeout while calling payment service"))
        else:
            lines.append(make_line(moment, "INFO", random.choice(NORMAL_INFO)))

    return lines


# ---------------------------------------------------------------
# MAIN GENERATOR
# ---------------------------------------------------------------

def generate(total_minutes=120, output_file="big_sample.log"):
    """
    Builds a full log file covering `total_minutes` of activity,
    with three incidents injected at fixed, known times.
    """

    start_time = datetime(2026, 10, 17, 9, 0, 0)

    # Incident windows: (first_minute, last_minute)
    db_outage     = (35, 41)
    brute_force   = (68, 72)
    latency_spike = (95, 101)

    all_lines = []

    for minute in range(total_minutes):
        current_minute = start_time + timedelta(minutes=minute)

        if db_outage[0] <= minute <= db_outage[1]:
            all_lines.extend(database_outage_minute(current_minute))

        elif brute_force[0] <= minute <= brute_force[1]:
            all_lines.extend(brute_force_minute(current_minute))

        elif latency_spike[0] <= minute <= latency_spike[1]:
            all_lines.extend(latency_spike_minute(current_minute))

        else:
            all_lines.extend(normal_minute(current_minute))

    # Sort so timestamps are in proper order
    all_lines.sort()

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        for line in all_lines:
            f.write(line + "\n")

    # ---------- Print a summary so we know what to expect ----------

    info_count  = sum(1 for line in all_lines if " INFO " in line)
    warn_count  = sum(1 for line in all_lines if " WARN " in line)
    error_count = sum(1 for line in all_lines if " ERROR " in line)

    print("=" * 55)
    print(f"  Generated: {output_file}")
    print("=" * 55)
    print(f"  Total lines : {len(all_lines)}")
    print(f"  INFO        : {info_count}")
    print(f"  WARN        : {warn_count}")
    print(f"  ERROR       : {error_count}")
    print("-" * 55)
    print("  INJECTED INCIDENTS (ground truth):")
    print(f"    Database outage  -> 09:35 to 09:41")
    print(f"    Brute force      -> 10:08 to 10:12")
    print(f"    Latency spike    -> 10:35 to 10:41")
    print("=" * 55)


# ---------------------------------------------------------------
# Run it when the file is executed directly
# ---------------------------------------------------------------

if __name__ == "__main__":
    generate()