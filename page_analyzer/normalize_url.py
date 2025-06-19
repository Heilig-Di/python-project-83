import validators


def normal_url(url):
    parsed = urlparse(url)

    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def vlidate(url):

    if not url or not validators.url(url):
        return "Некорректный URL" 

    if len(url) > 255:
        return "Некорректный URL"
    return None
