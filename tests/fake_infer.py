from __future__ import annotations

import argparse
import time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    print(f"model={args.model}")
    print(f"config={args.config}")
    time.sleep(0.2)


if __name__ == "__main__":
    main()
