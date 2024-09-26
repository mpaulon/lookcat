import argparse
import logging
from pathlib import Path

from lookcat.core import Watchdog
from lookcat.__version__ import __version__

logger = logging.getLogger()

# TODO: 
#   - by default: add folder to path + extract name to use as python module
#   - is it possible to do it on a single file
#   - remove is-not-module
#   - add a browser watcher ? extension ? use firefox by default
#   - rename module to 'path'
#   - rename module_args to 'args', pass them also to the custom command
#   - use current python interpreter

def main() -> None:
    parser = argparse.ArgumentParser(prog="lookcat")
    parser.add_argument("path", type=Path)
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parser.add_argument("--command", "-c", type=str, help="Custom command used to run process")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument('--version', "-V", action='version', version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    logging.basicConfig()

    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet args args mutually exclusive")
        return
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.disabled = True
    
    watchdog = Watchdog(args.path, args=args.args, command=args.command)
    watchdog.run()


if __name__ == "__main__":
    main()