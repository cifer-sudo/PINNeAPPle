"""List or extract single members of a remote ZIP over HTTP range requests (no full download).

Usage:
    python remote_zip.py list URL [pattern]
    python remote_zip.py get URL MEMBER OUTFILE
"""
import io
import struct
import sys
import urllib.request
import zipfile


class HttpRangeFile(io.RawIOBase):
    def __init__(self, url):
        self.url = url
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "pinn-scouting/0.1"})
        with urllib.request.urlopen(req, timeout=60) as r:
            self.size = int(r.headers["Content-Length"])
        self.pos = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.pos + n, self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}",
                                                        "User-Agent": "pinn-scouting/0.1"})
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
        self.pos += len(data)
        return data

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def main():
    cmd, url = sys.argv[1], sys.argv[2]
    zf = zipfile.ZipFile(io.BufferedReader(HttpRangeFile(url), buffer_size=1 << 20))
    if cmd == "list":
        pat = sys.argv[3] if len(sys.argv) > 3 else ""
        infos = zf.infolist()
        print(f"# {len(infos)} members")
        for i in infos:
            if pat in i.filename:
                print(f"{i.file_size:>12d}  {i.filename}")
    elif cmd == "get":
        member, out = sys.argv[3], sys.argv[4]
        with zf.open(member) as src, open(out, "wb") as dst:
            dst.write(src.read())
        print("wrote", out)


if __name__ == "__main__":
    main()
