from urllib.parse import urlsplit, urlunsplit


def normalize_url(raw: str) -> tuple[str, str]:
    parts = urlsplit(raw.strip())
    scheme = parts.scheme.lower() or "https"
    host = parts.hostname.lower() if parts.hostname else ""
    if host.startswith("www."):
        host = host[4:]
    path = parts.path.rstrip("/") or "/"
    normalized = urlunsplit((scheme, host, path, "", ""))
    return normalized, host
