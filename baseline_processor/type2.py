import matplotlib.pyplot as plt
import matplotlib.dates as dates
import argparse as ap
import datetime
import os


# Takes the datetime format in the log file and converts it to a datetime object.
def time(raw):
    # TODO: Change to regex split.
    t = raw.replace('/', ' ').replace(':', ' ').replace('.', ' ').replace(',', ' ').split()  # Changes all delimiters to space.
    i = list(reversed(t[3:6])) + t[0:3]
    return datetime.datetime(*[int(j) for j in i])


#  ------------------------------------------------------------------------------------------------------------------- #

parser = ap.ArgumentParser()
parser.add_argument('--us_time', action='store_true')
args = parser.parse_args()
us_time = args.us_time

for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith(".log")]:
        file = os.path.join(dirpath, filename)

        with open(file, 'r') as f:
            # Empty arrays to store data points.
            x = []  # Datetimes for latency.
            xt = []  # Datetimes for timeouts.
            y = []  # Latency.
            yt = []  # Timeouts.
            tr = ''  # Traceroutes text.
            ip = ''  # ipconfig text.

            t = f.readline()
            eof = False
            # MAIN LOOP
            while True:
                # Catch ipconfig information.
                while True:
                    k = ''
                    try:
                        k = f.readline()
                        if k == '':
                            eof = True
                            break
                        catch = k.split()[0]  # catch <- first word of line.
                        if catch == 'Tracing' or catch == 'Unable':  # This indicates ipconfig is finished.
                            break
                        ip += k  # If ipconfig not finished, add line to ip text.
                    except IndexError:  # If empty line is found, continue.
                        ip += k
                        continue
                if eof:
                    break
                f.readline() and f.readline()  # Skip two lines.

                # Catch traceroute information.
                while True:
                    try:
                        k = f.readline()
                        hop = k.split()[0]  # Get hop number. If empty line, hop will be empty array causing IndexError.
                        tr += k  # Add to traceroute information.
                    except IndexError:  # If line empty, traceroute is finished.
                        tr += '\n'
                        break
                for _ in range(2):
                    f.readline()  # Skip line.

                # Collecting ping statistics.
                while True:
                    try:
                        t = f.readline()
                        if t == 'Control-C\n':  # If user Control-C's, go to top of main loop.
                            t = f.readline()
                            break
                        run_time = time(t)  # Stores datetime stamp.
                    except TypeError:  # If invalid datetime given.
                        break

                    # Skipping newlines. Sometimes there will be a newline, sometimes not. This accounts for that.
                    line = f.readline().split()
                    if len(line) == 0:
                        line = f.readline().split()

                    # If pinging.
                    if line[0] == 'Pinging':
                        while True:
                            ping_time = 0
                            try:
                                t = f.readline()
                                s = t.split()
                                if len(s) == 6:  # Normal output of ping is 6 words long.
                                    ping_time = int(s[4].replace('<', '=').split('=')[1][:-2])  # Split data into array.
                                elif len(s) == 4:  # But one of the log files was only 4 words.
                                    ping_time = int(s[3].replace('<', '=').split('=')[1][:-2])  # Split data into array.

                                # If not 4 or 6 words we don't know what to do.
                                # TODO: Should change this to find the 'time=xms' line in the ping output.
                                else:
                                    raise IndexError

                            except IndexError:
                                if len(t.split()) == 0:  # If newline, ping is finished.
                                    break
                                elif len(
                                        t.split()) == 3:  # TODO: Ping timeouts are three words long. Should verify the words.
                                    xt.append(run_time)
                                    try:  # Use previous ping value to put a red dot on the ping graph.
                                        yt.append(y[-1])
                                    except IndexError:  # If no pings yet recorded, add timeout dot with latency 0.
                                        yt.append(0)
                                    continue

                            x.append(run_time)
                            y.append(ping_time)
                        for _ in range(5):  # Skip five lines.
                            f.readline()

                    # If ping request could not find host, go to next line.
                    elif line[0:2] == ['Ping', 'request']:
                        f.readline()
                        continue

                    # If Windows IP Configuration, go to top of main loop.
                    elif line[0] == 'Target':
                        break

                    # Else who knows what happened.
                    else:
                        raise Exception('An unknown error occurred.')

            # Statistics
            successes = len(y)
            timeouts = len(yt)

            min_latency = min(y)
            average_latency = sum(y) / successes
            max_latency = max(y)
            packet_loss = timeouts / (timeouts + successes) * 100

            # TODO: Format this better. Perhaps render it on the graph.
            print(file)
            print('Min Avg Max Loss%')
            print('{:.0f} {:.0f} {:.0f} {:.2f}'.format(min_latency, average_latency, max_latency, packet_loss))

            # Plotting parameters here.
            # Refer to matplotlib.
            # ------------------------- #
            # Plot window and plots.
            fig, ax = plt.subplots()
            fig.canvas.set_window_title('Baselining')
            ax.plot(x, y, 'b-', label='Success')
            ax.plot(xt, yt, 'r.', label='Timeout')

            # Metadata for plots.
            title = file.split('\\')[-3:]
            title[-1] = title[-1][:-4]
            title = '/'.join(title)
            plt.title(title)
            plt.xlabel('Date / Time')
            plt.ylabel('Latency (ms)')
            plt.legend()
            plt.ylim(ymin=0)

            # Change x-axis to datetime format.
            fig.autofmt_xdate()
            fmt = dates.DateFormatter('%d/%m %H:%M')
            ax.xaxis.set_major_formatter(fmt)

            plt.savefig(file[:-4] + ".png", dpi=200)
