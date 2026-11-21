"""The joke about the demo — make.fun entry.

Writes one line of joke text to $MAKEFUN_OUTPUT_DIR/entry.txt.
Stdlib only, no network, deterministic: the same bytes every run.
"""

import os

JOKE = (
    "The demo crashed, so my AI coding agent rolled back \u2014 "
    "not the code, just the chat, to the moment I said \u2018yeah, go ahead.\u2019"
)


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(JOKE)


if __name__ == "__main__":
    main()
