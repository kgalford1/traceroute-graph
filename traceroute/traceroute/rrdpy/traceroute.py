import datetime
import time
import subprocess
import re
import pathlib
import hashlib


# When object instantiated, runs MTR (or uses 'archive' if provided) and parses output into object.
class Traceroute:
    epoch = datetime.datetime(1970, 1, 1)

    def __init__(self, target, rrd_dir, graph_dir, archive=''):
        self.target = target  # Target of traceroute
        self.archive = archive  # Archived data if provided, empty otherwise.

        self.f_call = self.mtr()  # MTR call.
        self.stdout, self.stderr = self.outputs()  # stdout and stderr from MTR call.
        self.datetime = self.set_datetime()  # Epoch time of MTR call.
        self.hop_data = self.parse()  # Results of MTR call in array.

        self.path = self.set_path()  # List of hops.
        self.path_id = self.hash()  # MD5 hash of list of hops.
        self.ip = self.set_ip()  # Formatted list of hops.

        self.id_dir = pathlib.Path(str(self.path_id))
        self.rrd_dir = rrd_dir
        self.rrd = str(rrd_dir / self.id_dir) + ".rrd"  # db/target/id.rrd - str since directly referenced.
        self.graph_dir = graph_dir  # graphs/target/id/ - PosixPath since need to refer to files inside.

        self.print_log()  # Prints stdout and stderr of MTR call.

    def mtr(self):
        if not self.archive:
            t = subprocess.run(["sudo", "mtr", "-w", self.target, "-c", str(10)], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True, check=True)
            try:
                t.check_returncode()
                return t
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                exit(1)
            except OSError as e:
                print(e.strerror)
                exit(1)
        else:
            return None

    def outputs(self):
        if self.archive:
            return self.archive.lstrip(), ''
        else:
            return self.f_call.stdout, self.f_call.stderr

    def set_datetime(self):
        t = re.split('[: ]', self.stdout.split('\n')[0])
        t = list(filter(None, t))
        t[2] = time.strptime(t[2], '%b').tm_mon
        return int((datetime.datetime(*[int(t[i]) for i in [7, 2, 3, 4, 5, 6]]) - Traceroute.epoch).total_seconds())

    def parse(self):
        # Index         Property
        # ------------------------
        #     0         Hop #
        #     1         IP Address
        #     2         Packet Loss %
        #     3         Packets Sent
        #     4         Last Time
        #     5         Average Time
        #     6         Best Time
        #     7         Worst Time
        #     8         σ
        data_in = self.stdout.split('\n')[2:-1]
        data_out = []
        for hop in data_in:
            if hop.strip():
                hop = hop.split()
                try:
                    hop[0] = re.match('\d+', hop[0]).group()
                except AttributeError as e:
                    print(e)
                    exit(1)
                hop[2] = hop[2][:-1]
                data_out.append(hop)
        data_out.insert(0, [''] * len(data_out[0]))  # Puts ['', ...] at index 0 so index x corresponds to hop x.
        return data_out

    def print_log(self):
        t = "MTR stdout:\n" + self.stdout + "\n"
        t += "MTR stderr:\n" + self.stderr + "\n"
        print(t)

    def __len__(self):
        return len(self.hop_data)

    def x(self):
        return ":".join([str(i) for i in range(1, len(self))])

    def y(self):
        return ":".join([str(self.hop_data[i][5]) for i in range(1, len(self))])

    def set_path(self):
        return [self.hop_data[i][1] for i in range(len(self))]

    def hash(self):
        return hashlib.md5(b''.join([bytes(t, 'utf-8') for t in self.path])).hexdigest()

    def set_ip(self):
        length = len(max([self.hop_data[i][1] for i in range(len(self))], key=len))
        return ['{:>{len}}'.format(self.hop_data[i][1], len=length + 1) for i in range(len(self))]

