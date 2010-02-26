from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class Drink(models.Model):
    person = models.ForeignKey(Person)
    finished = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s" % (str(self.person), self.finished)
