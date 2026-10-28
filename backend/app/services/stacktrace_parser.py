import re

EXCEPTION_PATTERNS = [
    r"([A-Za-z0-9_.]+(?:Exception|Error|Fault|Failure|Crash|Warning))(?::|\s)",
    r"\b(HTTP\s*(?:400|401|403|404|429|500|502|503|504))\b",
    r"\b(OOMKilled|ExitCode:\s*137|SIGSEGV|SIGKILL)\b",
]

FILE_LINE_PATTERNS = [
    r'File\s+["\']([^"\']+\.(?:py|ts|tsx|js|go|rs|java))["\'],\s+line\s+(\d+)',
    r"at\s+([A-Za-z0-9_./$-]+\.(?:ts|tsx|js|java)):(\d+)",
    r"([a-zA-Z0-9_\-./]+\.(?:go|rs|cpp|c|h)):(\d+)",
]


def parse_stacktrace(text: str) -> dict:
    has_trace = bool(
        "Traceback" in text
        or "Exception:" in text
        or "Error:" in text
        or "at " in text
        or 'File "' in text
        or "OOMKilled" in text
    )

    detected_exception = None
    for pattern in EXCEPTION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            detected_exception = match.group(1)
            break

    source_file = None
    line_number = None
    for pattern in FILE_LINE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            source_file = match.group(1)
            try:
                line_number = int(match.group(2))
            except (ValueError, TypeError):
                pass
            break

    return {
        "has_trace": has_trace,
        "detected_exception": detected_exception,
        "source_file": source_file,
        "line_number": line_number,
    }
