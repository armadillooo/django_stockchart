from django.db import models

class Company(models.Model):
    class Meta:
        db_table = 'Company'

    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    market = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Price(models.Model):
    class Meta:
        db_table = 'Price'

    prime = models.CharField(max_length=100, primary_key=True, default=' ')
    date = models.DateField()
    code = models.ForeignKey(Company, on_delete=models.CASCADE)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    adjust = models.FloatField()

    def __str__(self):
        return str(self.date) + ' : ' + str(self.code)


class Adjust(models.Model):
    class Meta:
        db_table = 'Adjust'

    prime = models.CharField(max_length=100, primary_key=True, default=' ')
    date = models.DateField()
    code = models.ForeignKey(Company, on_delete=models.CASCADE)
    constant = models.FloatField()

    def __str__(self):
        return str(self.date) + ':' + str(self.code) 

