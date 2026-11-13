"""PDF text extractor v6: stream order, newline on y change."""
import re
import sys
import zlib

PDF = sys.argv[1]
OUT = sys.argv[2]

data = open(PDF, 'rb').read()
obj_off = {}
for m in re.finditer(rb'(?<![0-9])(\d+)\s+(\d+)\s+obj\b', data):
    obj_off[int(m.group(1))] = m.end()
ENDS = {}
for n, s in obj_off.items():
    e = data.find(b'endobj', s)
    ENDS[n] = e if e != -1 else min(len(data), s + 3_000_000)


def ob(n, limit=None):
    s = obj_off.get(n)
    if s is None:
        return b''
    return data[s:(ENDS[n] if limit is None else min(ENDS[n], s + limit))]


def stream(n):
    s = obj_off.get(n)
    if s is None:
        return None
    raw = data[s:ENDS[n]]
    k = raw.find(b'stream')
    if k == -1:
        return None
    st = raw[k + 6:].lstrip(b'\r\n')
    en = st.rfind(b'endstream')
    st = st[:en] if en != -1 else st
    if b'FlateDecode' not in raw[:k]:
        return st
    try:
        return zlib.decompressobj().decompress(st)
    except Exception:
        return None


def parse_cmap(blob):
    mp = {}
    if not blob:
        return mp
    t = blob.decode('latin-1', 'replace')
    for blk in re.findall(r'beginbfchar(.*?)endbfchar', t, re.S):
        for src, dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>', blk):
            d = dst if len(dst) % 2 == 0 else dst + '0'
            try:
                mp[int(src, 16)] = bytes.fromhex(d).decode('utf-16-be', 'ignore')
            except Exception:
                pass
    for blk in re.findall(r'beginbfrange(.*?)endbfrange', t, re.S):
        for lo, hi, tail in re.findall(
                r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]*>|\[[^\]]*\])', blk):
            a, b = int(lo, 16), int(hi, 16)
            if tail.startswith('['):
                for i, it in enumerate(re.findall(r'<([0-9A-Fa-f]*)>', tail)):
                    if a + i > b:
                        break
                    d = it if len(it) % 2 == 0 else it + '0'
                    mp[a + i] = bytes.fromhex(d).decode('utf-16-be', 'ignore')
            else:
                base = tail[1:-1]
                if not base or len(base) % 2:
                    continue
                bb = bytes.fromhex(base)
                for i in range(b - a + 1):
                    v = bytearray(bb)
                    v[-2:] = ((int.from_bytes(v[-2:], 'big') + i) & 0xFFFF).to_bytes(2, 'big')
                    mp[a + i] = bytes(v).decode('utf-16-be', 'ignore')
    return mp


FC = {}


def cmap(fnum):
    if fnum not in FC:
        body = ob(fnum, 3000)
        tu = re.search(rb'/ToUnicode\s+(\d+)\s+\d+\s+R', body)
        FC[fnum] = parse_cmap(stream(int(tu.group(1)))) if tu else {}
    return FC[fnum]


N = r'[-+]?(?:\d+\.\d+|\.\d+|\d+)'
PAT = re.compile(
    r'/(?P<tf>[A-Za-z0-9]+)\s+' + N + r'\s+Tf'
    r'|<(?P<hex>[0-9A-Fa-f\s]*)>\s*Tj'
    r'|\[(?P<arr>(?:[^\[\]\\]|\\.)*)\]\s*TJ'
    r'|(?P<tdx>' + N + r')\s+(?P<tdy>' + N + r')\s+(?:Td|TD)'
    r'|(?P<a>' + N + r')\s+' + N + r'\s+' + N + r'\s+' + N + r'\s+(?P<ex>' + N + r')\s+(?P<ey>' + N + r')\s+Tm'
    r'|T\*'
)


def decode(h, mp):
    h = re.sub(r'\s', '', h)
    if len(h) % 2:
        h += '0'
    return ''.join(mp.get(int(h[j:j + 4], 16), '') for j in range(0, len(h), 4))


WM = ('闊╅『骞冲浘瑙inux', '鏇村瀛︿範璧勬枡', '鍏虫敞寰俊', 'hsp', '鍥捐ВLinux鍏ㄩ潰鍗囩骇')

pages = sorted(n for n in obj_off if re.search(rb'/Type\s*/Page[^s]', ob(n, 2000)))
out_pages = []

for idx, pn in enumerate(pages, 1):
    body = ob(pn)
    fm = re.search(rb'/Font\s*<<(.*?)>>', body, re.S)
    fonts = {n.decode(): int(v) for n, v in re.findall(rb'/([A-Za-z0-9]+)\s+(\d+)\s+\d+\s+R', fm.group(1))} if fm else {}
    cm = re.search(rb'/Contents\s+(\d+)\s+\d+\s+R', body)
    if cm:
        conts = [int(cm.group(1))]
    else:
        am = re.search(rb'/Contents\s*\[(.*?)\]', body, re.S)
        conts = [int(x) for x in re.findall(rb'(\d+)\s+\d+\s+R', am.group(1))] if am else []

    chunks = []          # list of (y, text) in stream order
    for c in conts:
        blob = stream(c)
        if not blob:
            continue
        txt = blob.decode('latin-1', 'replace')
        cur = None
        x = y = 0.0
        for m in PAT.finditer(txt):
            if m.group('tf'):
                cur = m.group('tf')
            elif m.group('hex') is not None:
                t = decode(m.group('hex'), cmap(fonts.get(cur, -1)))
                if t:
                    chunks.append((y, t))
            elif m.group('arr') is not None:
                mp = cmap(fonts.get(cur, -1))
                t = ''.join(decode(h, mp) for h in re.findall(r'<([0-9A-Fa-f\s]*)>', m.group('arr')))
                if t:
                    chunks.append((y, t))
            elif m.group('tdx') is not None:
                x += float(m.group('tdx'))
                y += float(m.group('tdy'))
            elif m.group('ex') is not None:
                x = float(m.group('ex'))
                y = float(m.group('ey'))
            else:
                y -= 12

    lines = []
    cur_y = None
    buf = []
    for gy, t in chunks:
        if cur_y is None or abs(gy - cur_y) <= 1.5:
            buf.append(t)
        else:
            lines.append(''.join(buf))
            buf = [t]
        cur_y = gy
    if buf:
        lines.append(''.join(buf))
    lines = [ln for ln in lines if not any(w in ln for w in WM)]
    out_pages.append((idx, '\n'.join(lines)))

blob_out = ''.join('\n\n===== PAGE %d =====\n%s' % (i, t) for i, t in out_pages).encode('utf-8')
open(OUT, 'wb').write(blob_out)
joined = ''.join(t for _, t in out_pages)
print('pages', len(out_pages), 'bytes', len(blob_out))
print('cjk', sum(1 for ch in joined if '\u4e00' <= ch <= '\u9fff'))
for kw in ['鐢ㄦ埛绠＄悊', 'groupadd', 'usermod', '杩愯绾у埆', '甯姪鎸囦护', 'Linux', '娣诲姞鐢ㄦ埛']:
    print(' ', kw, joined.count(kw))
sys.stdout.buffer.write(('\n--- PAGE 2 ---\n' + out_pages[1][1][:600]).encode('utf-8', 'replace'))

