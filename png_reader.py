#!/usr/bin/env python3
"""PNG file parser — read chunks, extract metadata."""
import struct, zlib, sys

def read_png(filename):
    with open(filename, "rb") as f:
        sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            print(f"Not a PNG file"); return
        chunks = []
        while True:
            header = f.read(8)
            if len(header) < 8: break
            length, chunk_type = struct.unpack(">I4s", header)
            data = f.read(length); crc = f.read(4)
            chunks.append((chunk_type.decode(), length, data))
            if chunk_type == b"IEND": break
        return chunks

def parse_ihdr(data):
    w, h, depth, color, comp, filt, interlace = struct.unpack(">IIBBBBB", data)
    color_types = {0:"Grayscale",2:"RGB",3:"Indexed",4:"Gray+Alpha",6:"RGBA"}
    return {"width":w,"height":h,"bit_depth":depth,"color_type":color_types.get(color,str(color)),
            "compression":comp,"filter":filt,"interlace":interlace}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: png_reader.py <file.png>")
        print("\nDemo: creating and reading a minimal PNG...")
        # Create a 1x1 red pixel PNG
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        raw = zlib.compress(b"\x00\xff\x00\x00")  # filter byte + RGB
        def chunk(ctype, data):
            c = ctype + data; return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")
        with open("/tmp/test.png", "wb") as f: f.write(png)
        chunks = read_png("/tmp/test.png")
    else:
        chunks = read_png(sys.argv[1])
    if chunks:
        for ctype, length, data in chunks:
            print(f"  {ctype}: {length} bytes")
            if ctype == "IHDR": print(f"    {parse_ihdr(data)}")
