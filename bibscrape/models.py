from django.db import models

class BibUser(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class StoredBook(models.Model):
    user = models.ForeignKey(BibUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    ean = models.CharField(max_length=13)
    disamb = models.CharField(max_length=200)
    def __str__(self):
        return self.title+" EAN="+self.ean+" h="+self.disamb
