import difflib

def generate_diff(changes: list) -> list:
    diffs = []
    for change in changes:
        before = change["original"].splitlines(keepends=True)
        after = change["fixed"].splitlines(keepends=True)

        diff = "".join(
            difflib.unified_diff(
                before,
                after,
                fromfile=f"a/{change['file']}",
                tofile=f"b/{change['file']}"
            )
        )

        diffs.append({
            "file": change["file"],
            "diff": diff
        })

    return diffs
