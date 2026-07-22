import csv
import os
import time
import sys
sys.path.insert(0, "scripts")
from fast_xlsx_parse import parse_rows, load_shared_strings

OUT_CSV = "data/telcom_data.csv"
TIME_BUDGET = 38  # seconds, leave margin under the 45s tool timeout

HEADER = ['Bearer Id', 'Start', 'Start ms', 'End', 'End ms', 'Dur. (ms)', 'IMSI', 'MSISDN/Number', 'IMEI',
          'Last Location Name', 'Avg RTT DL (ms)', 'Avg RTT UL (ms)', 'Avg Bearer TP DL (kbps)',
          'Avg Bearer TP UL (kbps)', 'TCP DL Retrans. Vol (Bytes)', 'TCP UL Retrans. Vol (Bytes)',
          'DL TP < 50 Kbps (%)', '50 Kbps < DL TP < 250 Kbps (%)', '250 Kbps < DL TP < 1 Mbps (%)',
          'DL TP > 1 Mbps (%)', 'UL TP < 10 Kbps (%)', '10 Kbps < UL TP < 50 Kbps (%)',
          '50 Kbps < UL TP < 300 Kbps (%)', 'UL TP > 300 Kbps (%)', 'HTTP DL (Bytes)', 'HTTP UL (Bytes)',
          'Activity Duration DL (ms)', 'Activity Duration UL (ms)', 'Dur. (ms).1', 'Handset Manufacturer',
          'Handset Type', 'Nb of sec with 125000B < Vol DL', 'Nb of sec with 1250B < Vol UL < 6250B',
          'Nb of sec with 31250B < Vol DL < 125000B', 'Nb of sec with 37500B < Vol UL',
          'Nb of sec with 6250B < Vol DL < 31250B', 'Nb of sec with 6250B < Vol UL < 37500B',
          'Nb of sec with Vol DL < 6250B', 'Nb of sec with Vol UL < 1250B', 'Social Media DL (Bytes)',
          'Social Media UL (Bytes)', 'Google DL (Bytes)', 'Google UL (Bytes)', 'Email DL (Bytes)',
          'Email UL (Bytes)', 'Youtube DL (Bytes)', 'Youtube UL (Bytes)', 'Netflix DL (Bytes)',
          'Netflix UL (Bytes)', 'Gaming DL (Bytes)', 'Gaming UL (Bytes)', 'Other DL (Bytes)',
          'Other UL (Bytes)', 'Total UL (Bytes)', 'Total DL (Bytes)']
COLS_SORTED = sorted(
    {c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"} |
    {a + b for a in "ABC" for b in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    key=lambda c: (len(c), c),
)[: len(HEADER)]

t0 = time.time()

already = 0
write_header = True
if os.path.exists(OUT_CSV):
    with open(OUT_CSV, "r") as f:
        already = sum(1 for _ in f) - 1
    if already > 0:
        write_header = False
    else:
        already = 0

print("already written:", already, flush=True)

ss = load_shared_strings()
print("shared strings loaded", time.time() - t0, flush=True)

start_row = already + 2
rows_iter = parse_rows(ss, start_row=start_row)

mode = "a" if not write_header else "w"
n = 0
t1 = time.time()
with open(OUT_CSV, mode, newline="") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(HEADER)
    for row in rows_iter:
        writer.writerow([row.get(c, "") for c in COLS_SORTED])
        n += 1
        if time.time() - t1 > TIME_BUDGET:
            print("time budget hit, stopping this batch", flush=True)
            break

print("wrote this run:", n, "elapsed", time.time() - t1, flush=True)
print("total so far:", already + n, flush=True)
