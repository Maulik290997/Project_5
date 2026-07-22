"""
Fast streaming parser for the TellCo xlsx export.
openpyxl / pandas.read_excel are too slow for this ~150k-row, 52-column file
in this sandbox, so we parse the underlying sheet XML directly with lxml's
C-accelerated iterparse and stream rows straight out to CSV/Parquet.
"""
import re
import time
import datetime
from lxml import etree

SRC_DIR = "/tmp/xlsxext"
SHEET_XML = f"{SRC_DIR}/xl/worksheets/sheet1.xml"
SHARED_STRINGS_XML = f"{SRC_DIR}/xl/sharedStrings.xml"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
EXCEL_EPOCH = datetime.datetime(1899, 12, 30)

_col_re = re.compile(r"[A-Z]+")


def load_shared_strings():
    strings = []
    context = etree.iterparse(SHARED_STRINGS_XML, events=("end",), tag=f"{NS}si")
    for _, elem in context:
        strings.append("".join(elem.itertext()))
        elem.clear()
    return strings


def col_letters(cell_ref):
    return _col_re.match(cell_ref).group(0)


def excel_serial_to_dt(value):
    try:
        return EXCEL_EPOCH + datetime.timedelta(days=float(value))
    except (ValueError, OverflowError):
        return None


def parse_rows(shared_strings, start_row=1, max_rows=None):
    """Yields dict {col_letter: value} for each physical row, 1-indexed incl. header."""
    context = etree.iterparse(SHEET_XML, events=("end",), tag=f"{NS}row")
    n = 0
    yielded = 0
    for _, row_elem in context:
        n += 1
        if n < start_row:
            row_elem.clear()
            while row_elem.getprevious() is not None:
                del row_elem.getparent()[0]
            continue
        values = {}
        for c in row_elem.iter(f"{NS}c"):
            ref = c.get("r")
            if not ref:
                continue
            col = col_letters(ref)
            t = c.get("t")
            s = c.get("s")
            v_elem = c.find(f"{NS}v")
            if v_elem is None or v_elem.text is None:
                values[col] = ""
                continue
            raw = v_elem.text
            if t == "s":
                values[col] = shared_strings[int(raw)]
            elif s == "2":
                dt = excel_serial_to_dt(raw)
                values[col] = dt.isoformat(sep=" ") if dt else ""
            else:
                values[col] = raw
        yield values
        row_elem.clear()
        while row_elem.getprevious() is not None:
            del row_elem.getparent()[0]
        yielded += 1
        if max_rows and yielded >= max_rows:
            break


if __name__ == "__main__":
    t0 = time.time()
    ss = load_shared_strings()
    print("shared strings loaded", len(ss), time.time() - t0, flush=True)
