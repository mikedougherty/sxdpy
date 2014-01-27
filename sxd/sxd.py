import sys
import codecs
from struct import unpack, calcsize


def binread(spec, data, endian = '<'):
    sz = calcsize(endian + spec)
    readable, remainder = data[:sz], data[sz:]
    return unpack(spec, readable), remainder


def pstring(data, endian = '<'):
    (sz,), data = binread('I', data, endian)
    s, data = data[:sz], data[sz:]
    return s, data


def read_header(data):
    header, data = pstring(data)
    header = header.rstrip('\x00')

    return header.split(), data


def read_saverx_config(data):
    saverx_config, data = pstring(data)
    checksum = ''.join(map(chr, range(0,10)))
    if saverx_config.startswith(checksum):
        saverx_config = saverx_config[len(checksum):]

    saverx_config, doc_remain = pstring(saverx_config)
    if doc_remain:
        raise Exception("Unexpected leftover data: %r", doc_remain)


    if saverx_config.startswith(codecs.BOM_UTF8):
        saverx_config = saverx_config[len(codecs.BOM_UTF8):].decode('utf8')

    return saverx_config, data


def main(fname):
    with open(fname, 'rb') as f:
        data = f.read()

    header, data = read_header(data)
    saverx_config, data = read_saverx_config(data)

    sections = []

    while data:
        section_s, data = pstring(data)
        section, _rem = binread((len(section_s)/4) * 'I', section_s)
        assert not _rem, repr(_rem)
        sections.append(section)

    print [len(x) for x in sections]


if __name__ == '__main__':
    main(*sys.argv[1:])
