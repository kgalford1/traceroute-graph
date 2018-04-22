import pathlib

try:
    from traceroute.models import Time
except ImportError:
    pass


class Args:
    def __init__(self, directory, target):
        self.directory = directory
        self.target = target
        self.step = '60'
        self.heartbeat = '120'
        self.size = '1y'
        try:
            self.graph_time = Time.objects.all()[0].rrd_graph_time
        except NameError:
            pass
        self.y_max = '0'
        self.width = '1000'
        self.height = '410'
        self.stack = False
        self.thickness = '1'
        self.start = ''


def get_args(directory, target):
    return Args(directory, target)


def create_directories(args, target):
    root_dir = pathlib.Path(args.directory)
    target_dir = pathlib.Path(target)

    rrd_dir = root_dir / pathlib.Path("db") / target_dir
    # TODO: Relate this directory to that in ktr/settings.py.
    graph_dir = root_dir / pathlib.Path("traceroute/static") / target_dir

    rrd_dir.mkdir(parents=True, exist_ok=True)
    graph_dir.mkdir(parents=True, exist_ok=True)

    return rrd_dir, graph_dir

