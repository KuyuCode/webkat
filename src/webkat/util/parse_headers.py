from multidict import CIMultiDict


def parse_headers(raw: list[tuple[bytes, bytes]]) -> CIMultiDict[str]:
    headers: CIMultiDict[str] = CIMultiDict()

    for key, value in raw:
        headers.add(key.decode("utf-8"), value.decode("utf-8"))

    return headers
