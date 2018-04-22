from utilities import get_args, create_directories
from rrd import create, update
from traceroute import Traceroute
import pathlib
import argparse as ap

parser = ap.ArgumentParser()
parser.add_argument('target')
args = parser.parse_args()

directory = '/var/www/html/django'  # TODO: Remove hardcoded location.
target = args.target

args = get_args(directory, target)
rrd_dir, graph_dir = create_directories(args, target)
tr = Traceroute(target, rrd_dir, graph_dir)
exists = pathlib.Path(tr.rrd).exists()

exists or create(tr, args)
update(tr)

