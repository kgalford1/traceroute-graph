import subprocess
import shutil
import pathlib

# Colours for different lines on graph.
colour = ['e6194b', '3cb44b', 'ffe119', '0082c8', 'f58231', '911eb4', '46f0f0', 'f032e6', 'd2f53c', 'fabebe', '008080',
          'e6beff', 'aa6e28', 'fffac8', '800000', 'aaffc3', '808000', 'ffd8b1', '000080', '808080', '000000', 'ffffff']
colour.insert(0, '')


def create(tr, args):
    # Extracting relevant arguments.
    heartbeat = args.heartbeat
    size = args.size
    step = args.step
    start = args.start

    # DS and RRA parameters.
    rrd_ds = "GAUGE:" + heartbeat + ":0.01:U"
    rrd_rra = "AVERAGE:0.5:1:" + size

    # Program call parameters.
    q = ["sudo", "rrdtool", "create", tr.rrd]
    q += ["--step", step]
    if start:  # If a start time for the database is specified (otherwise uses time.now() as default).
        q += ["--start", start]

    # DS & RRA for each hop.
    for i in range(1, len(tr)):
        q.append("DS:" + str(i) + ":" + rrd_ds)
    q.append("RRA:" + rrd_rra)

    # Create file listing hops.
    with open(tr.rrd[:-3] + 'hop', 'w') as f:
        for i in range(1, len(tr.ip)):
            f.write(tr.ip[i] + '\n')

    # Program call.
    subprocess.run([*q])


def update(tr):
    # Program call parameters.
    q = ["sudo", "rrdtool", "update", tr.rrd, "--template=" + tr.x(), "N:" + tr.y()]

    # TODO: Add number of hops to this file.
    with open(str(tr.rrd_dir) + '/current.txt', 'w') as f:
        f.write(tr.path_id)
        f.write('\n')

    # Program call.
    subprocess.run([*q])


def get_graph_params(args):
    q = ["--imgformat=PNG", "--legend-position=east", "--pango-markup", "--vertical-label=Latency (ms)", "--slope-mode"]
    q += ["-u", args.y_max]
    q += ["-l", "0"]
    q += ["--start", "now-" + args.graph_time]
    q += ["--week-fmt", "%d/%m"]
    q += ["-h", args.height, "-w", args.width]
    return q


def graph(args, target):
    # Relevant command line arguments.
    title = target.split('/')[-2]  # Removes path from title.
    graph_time = args.graph_time
    stack = args.stack
    thickness = args.thickness
    graph_dir = '/var/www/html/django/traceroute/static/' + title  # TODO: Remove hardcoded location.

    with open(target[:-3] + 'hop', 'r') as f:  # Opens file with list of hops.
        hops = f.readlines()

    # GRAPH INDIVIDUAL HOPS
    for i in range(1, len(hops)):
        i = str(i)

        # Program call parameters.
        q = ["sudo", "rrdtool", "graph"]
        q += [str(graph_dir / pathlib.Path("hop-" + i + ".png"))] + get_graph_params(args)
        q.extend(["--title", title + " - Hop " + i + " - <b>" + hops[int(i)].strip() + "</b> - " + graph_time])
        q.append("--legend-direction=bottomup")

        stack_str = ""
        if stack:
            stack_str = ":STACK"

        # Refer to man page for rrdgraph_graph.
        q.append("DEF:" + i + "=" + target + ":" + i + ":AVERAGE")
        q.append("LINE" + thickness + ":" + i + "#" + colour[int(i)] + ":" + '{0:>{1}}'.format(hops[int(i)].rstrip(), len(hops[int(i)]) + 7) + stack_str)
        q.append("GPRINT:" + i + ":LAST:%6.2lf")
        q.append("GPRINT:" + i + ":AVERAGE:%6.2lf\\n")
        q.append(
            "COMMENT:" '{0:>{1}}'.format('', len(hops[int(i)]) + 7) + '{:>10}{:>9}'.format("Last", "Average") + "\\n")

        # Program call.
        subprocess.run([*q], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # GRAPH MAIN
    # Program call parameters
    q = ["sudo", "rrdtool", "graph"]
    q += [str(graph_dir / pathlib.Path(title + ".png"))] + get_graph_params(args)
    q.extend(["--title", "<b>" + title + "</b> - " + graph_time])
    q.append("--legend-direction=topdown")

    stack_str = ""
    if stack:
        stack_str = ":STACK"

    # Refer to man page for rrdgraph_graph
    q.append("COMMENT:" + '{0:>{1}}'.format('', len(hops[0]) + 7) + '{:>10}{:>9}'.format("Last", "Average") + "\\n")

    for i in range(1, len(hops)):
        q.append("DEF:" + str(i) + "=" + target + ":" + str(i) + ":AVERAGE")
        q.append("LINE" + thickness + ":" + str(i) + "#" + colour[i] + ":Hop " + '{:>2}'.format(str(i)) + " -" + hops[
            int(i)].rstrip() + stack_str)
        q.append("GPRINT:" + str(i) + ":LAST:%6.2lf")
        q.append("GPRINT:" + str(i) + ":AVERAGE:%6.2lf\\n")

    # Program call.
    subprocess.run([*q], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

