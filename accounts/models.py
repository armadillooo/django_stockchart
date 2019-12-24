from django.db import models

class Favorite(models.Model):
    class Meta:
        db_table = 'Favorite'

    prime = models.CharField(max_length=100, primary_key=True, default=' ')
    user = models.CharField(max_length=100)
    code = models.IntegerField()

    def __str__(self):
        return self.user + ':' + str(self.code)
