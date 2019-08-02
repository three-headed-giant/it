import argparse
from pathlib import Path

class DoesntExist(Exception):
    pass

def main():
    parser = argparse.ArgumentParser(description='InspectorTiger')
    parser.add_argument('paths', metavar='P', type=Path, nargs='+',
                        help='paths to check')
    args = parser.parse_args()
    files = []
    for path in args.paths:
        if not path.exists():
            raise DoesntExist(path)
        
        if path.is_file():
            files.append(path)
        else:
            files.extend(path.glob("**/*.py"))


if __name__ == "__main__":
    main()
