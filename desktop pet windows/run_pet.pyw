import os
import sys
import argparse

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
os.chdir(base_dir)

from main import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cozy Desktop Pet")
    parser.add_argument("--style", choices=["cute", "real"], default=None)
    parser.add_argument("--size", type=int, default=112)
    parser.add_argument("--bed", action="store_true", help="Keep bed visible on desktop")
    parser.add_argument("--bowl", action="store_true", help="Keep food bowl visible on desktop")
    args, unknown = parser.parse_known_args()
    sys.exit(run(style=args.style, size=args.size, bed=args.bed, bowl=args.bowl))
