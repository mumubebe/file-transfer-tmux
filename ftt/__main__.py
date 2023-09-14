import argparse
from .ftt import transfer_file


parser = argparse.ArgumentParser(description="Tmux file transfer tool")

parser.add_argument(
    "send",
    type=str,
    help="Sending end\npaneid:/path/to/file",
)

parser.add_argument(
    "recv",
    type=str,
    help="Recieving end\npaneid:/path/",
)

args = parser.parse_args()

s = args.send.split(":")
if len(s) == 2:
    spane = int(s[0])
    spath = s[1]

r = args.recv.split(":")
if len(r) == 2:
    rpane = int(r[0])
    rpath = r[1]

transfer_file(spane, rpane, spath, rpath)
