#!/usr/bin/env python3
"""
Desktop Pet Griffin - macOS Edition (MacBook Air M1 / Apple Silicon)
Main execution entry point.
"""
import os
import sys

# Ensure current directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import run

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Desktop Pet Griffin (macOS Edition)")
    parser.add_argument("--style", choices=["cute", "real"], default=None, help="Start with cute or real griffin")
    parser.add_argument("--size", type=int, default=112, help="Pet size in pixels (default: 112)")
    parser.add_argument("--bed", action="store_true", help="Spawn permanent bed")
    parser.add_argument("--bowl", action="store_true", help="Spawn permanent food bowl")
    args, unknown = parser.parse_known_args()
    sys.exit(run(style=args.style, size=args.size, bed=args.bed, bowl=args.bowl))
