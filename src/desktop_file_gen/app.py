#!/bin/env python
import argparse
from desktop_file_gen.desktop import DesktopEntry


def parse_args():
    parser = argparse.ArgumentParser(description="Generate .desktop files.")
    parser.add_argument("path", nargs='*', type=str, help="exe/url/dir path")
    # parser.add_argument("-a", "--append", action="store_true", help="Append to existing .desktop file.")
    parser.add_argument("-i", "--icon", type=str, help="Path to the icon file.")
    parser.add_argument("--exec", type=str, help="Command to execute the application.")
    return parser.parse_args()


def main():
    args = parse_args()
    for p in args.path:
        name = p.split("/")[-1]
        try:
            desktop = DesktopEntry(
                path=p,
                Name=name,
                Icon=args.icon,
                Exec=args.exec,
            )
            desktop.save()
        except Exception as e:
            print(f"Error creating .desktop file for {p}: {e}")
            continue


if __name__ == "__main__":
    main()
