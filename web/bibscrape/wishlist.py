from bibscrape.models import BibUser, StoredBook
from bibscrape.services.bibhsearch import BookCopy

import logging

logger = logging.getLogger(__name__)

def find_or_create_user(name_):
    existing_user = list(BibUser.objects.filter( name = name_))
    if not existing_user:
        existing_user = BibUser(name_)
        existing_user.save()
    else:
        return existing_user[0]

def wishlist_of(user_name : str):
    return list(StoredBook.objects.filter(user__name = user_name))

def add_to_wishlist(user_name : str, title : str, ean : str, hash : str):
    owner = find_or_create_user(user_name)
    to_add = StoredBook(user = owner, title = title, ean = ean, disamb = hash)
    to_add.save()

def remove_from_wishlist(user_name : str, title : str, ean : str, hash : str):
    try:
        StoredBook.objects.filter(user__name = user_name).filter(disamb = hash).get().delete()
    except StoredBook.DoesNotExist:
        logger.warning("Attempt to delete non-existing book {} from wishlist of {}".format(title, user_name) )

def wishlist_id(user_name : str, book_copy : BookCopy):
    try:
        return StoredBook.objects.filter(user__name = user_name).filter(disamb = book_copy.hash).get().id
    except StoredBook.DoesNotExist:
        return None

def wishlist_item(id : str):
    try:
        return StoredBook.objects.filter(id = id).get()
    except StoredBook.DoesNotExist:
        return None
