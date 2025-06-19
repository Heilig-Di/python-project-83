from bs4 import BeautifulSoup


def parser_html(html):
    soup = BeautifulSoup(html, 'lxml')

    h1 = (soup.find('h1')).get_text(strip=True) if soup.find('h1') else None

    title_found = soup.find('title')
    title = title_found.get_text(strip=True) if title_found else None

    meta = soup.find('meta', attrs={"name": "description"})
    description = (
        meta['content'].strip()
        if meta and meta.get('content')
        else None
    )

    return {'h1': h1, 'title': title, 'meta': meta, 'description': description}
