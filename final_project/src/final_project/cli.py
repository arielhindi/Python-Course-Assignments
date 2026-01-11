"""Small CLI entrypoint for final_project."""
import argparse


def main(argv=None):
    p = argparse.ArgumentParser(prog="final_project", description="Final project CLI")
    p.add_argument("--who", default="world", help="Who to greet")
    args = p.parse_args(argv)
    print(f"Hello, {args.who}! This is the final_project scaffold.")


if __name__ == "__main__":
    main()
