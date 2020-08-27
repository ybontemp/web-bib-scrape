from django.shortcuts import render
from django.http import HttpResponse

from bibscrape.services.bibhsearch import find_all_books, Book, BookCopy, details_of
from bibscrape.wishlist import add_to_wishlist, remove_from_wishlist, wishlist_id, wishlist_of

import logging

logger = logging.getLogger(__name__)

# some dummy result to speed up dev
mock_result = [BookCopy(book = Book('Livre Premier', ean = "EAN1"), 
                                  available='Disponible', code='Code1', 
                                  network = 'Réseau louviérois de lecture publique', 
                                  location = 'LL - Service des prêts directs', 
                                  section = 'Adulte'), 
                        BookCopy(book = Book('Livre Deux', ean = "EAN2"), 
                                  available='QUARANTAINE', code='Code1', 
                                  network = 'Réseau louviérois de lecture publique', 
                                  location = 'LL - Service des prêts directs', 
                                  section = 'Adulte'),
                        BookCopy(book = Book('Livre Trois', ean="EAN3", format="Poche"), 
                                  available='Prêté', code='Code1', 
                                  network = 'Réseau louviérois de lecture publique', 
                                  location = 'LL - Service des prêts directs', 
                                  section = 'Adulte')]

def index(request):
    return HttpResponse("Hello world")

def search(request):
    search_key = request.GET.get('q',None)

    #If /search is accessed, it is equivalent to an empty result (ready to start searching)
    if search_key is None:
        search_result = []
    else: 
        mock = request.GET.get('m', False)
        if (mock):
            logger.info("Running in mock mode")
            search_result = mock_result
        else:        
            search_result = list(filter(lambda b: b.network.startswith('Réseau louv'), find_all_books(search_key)))
            search_result.sort(key = lambda b : b.book.title)
            logger.info("Found {} books".format(len(search_result)))
            

        for b in search_result:
            b.in_wishlist = wishlist_id('yves', b) 

    context = {'search' : search_key, 'book_copies' : search_result}
    return render(request, 'bibscrape/search.html', context) 

def wishlist(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        title = request.POST.get('title')
        ean = request.POST.get('ean')
        bookhash = request.POST.get('hash')
        response = HttpResponse()        
        if action == 'add':
            add_to_wishlist('yves', title, ean, bookhash)
            response.status_code = 201
        elif action == 'del':
            remove_from_wishlist('yves', title, ean, bookhash)
            response.status_code = 202
        return response
    elif request.method == 'GET':
        items = [details_of(b) for b in wishlist_of('yves')]
        return render(request, 'bibscrape/wishlist.html' ,{'user' : 'yves', 'items' : items })

