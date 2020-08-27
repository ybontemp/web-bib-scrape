from urllib.request import urlopen, build_opener, HTTPCookieProcessor
from urllib.parse import quote
from http.cookiejar import CookieJar

import time

from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString

from bibscrape.models import StoredBook

import logging
import hashlib

SEARCH_URL = 'https://bibliotheques.hainaut.be/osiros/result/notice.php?queryosiros={}&spec_expand=1&sort_define=tri_titre&sort_order=1&osirosrows=10&osirosstart={}&idosiros=1234567'


logger = logging.getLogger(__name__)

class Book:
    def __init__(self, title, ean = "", format = ""):
        self.title = title
        self.ean = ean
        self.format = format

    def __str__(self):
        return 'Book{}'.format(self.__dict__)

class BookCopy:
    def __init__(self, book, available, network, location, section, code):
        self.book = book
        self.available = available
        self.network = network
        self.location = location
        self.section = section
        self.code = code
        self.in_wishlist = False       
        self.hash = hashlib.md5(bytes(self.book.ean+self.code+self.location+self.book.format, "utf-8")).hexdigest()
    def __str__(self):
        return 'BookCopy{}'.format(self.__dict__)
    
def create_opener():
    cookie_jar = CookieJar()
    return build_opener(HTTPCookieProcessor(cookie_jar))

def get_soup(url_opener, query, page_index = 0):
    start = time.time()
    http = url_opener.open(SEARCH_URL.format(quote(query), str(page_index)))
    html = http.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    end = time.time()
    logger.info("{} ms to GET {} page {}".format(query, page_index, end - start))
    return soup

def ean_tag(tag):
    
    if isinstance(tag, Tag):
        previous = tag.previous_sibling.previous_sibling
        return isinstance(previous, Tag) and tag.name == 'div' and previous.name == 'span' and previous.string.strip().startswith('EAN')
    else:
        return False
    
def extract_number_pages(soup):
    return int(soup.find(class_ = "pager-nb-page").string.split('/')[1])

def extract_book(soup):
    try:
        title = soup.find(class_ = "descriptionNotice").find("h1")
        ean = soup.find(id = "notice-onglet-contient").find(ean_tag).string.strip()
    except AttributeError:
        ean = None
    if ean is not None:
        return Book(title.string.strip(), ean= ean)
    else:
        return None

def cell_to_bookcopy(book, cell):
    copy = BookCopy(book = book, 
                    available = cell[0].string.strip(),
                    network = cell[1].string.strip(),
                    location = cell[2].string.strip(),
                    section = cell[4].string.strip(),
                    code = cell[5].string.strip()
    )
    return copy

def extract_book_copy_info(soup, book):    
    exemplaires_table = soup.find(class_ ="table-exemplaires")

    try:        
        return [cell_to_bookcopy(book, list(filter(lambda x : isinstance(x, Tag), row.contents))) for row in exemplaires_table.tbody.find_all('tr')]
    except AttributeError:
        return []

def find_all_books(query):    
    opener = create_opener()
    soup = get_soup(opener, query)
    try: 
        number_pages = extract_number_pages(soup)
    except AttributeError:
        return []
    book_copies = []
    for i in range(0, number_pages)  :           
        book = extract_book(soup)
        if book is not None:
            book_copies = book_copies + extract_book_copy_info(soup, book)
        if i < number_pages-1: 
            # get the next page (only if it this was not the last iteration)
            soup = get_soup(opener, query, i+1)
    logger.info("{} pages found for criteria {}".format(len(book_copies), query))
    return book_copies
        
def details_of(stored_book : StoredBook):
    for b in find_all_books(stored_book.ean) :
        if b.hash == stored_book.disamb:
            return b        
    return None        
