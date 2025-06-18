import validators


def normal_url(url):
    parsed = urlparse(url)
    normalized_url = f"parsed.scheme://parsed.netloc"


def error(url):
    if not url or not validators.url(url):
        return "Некорректный URL" 

    if len(url) > 255:
        return "Некорректный URL"
    return None
