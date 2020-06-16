from django.db import models

class Mov(models.Model):
	Action = models.IntegerField()
	ScienceFiction = models.IntegerField()
	Drama = models.IntegerField()
	Comedy = models.IntegerField()
	Thriller = models.IntegerField()
	Horror = models.IntegerField()
	Romance = models.IntegerField()
	Fantasy = models.IntegerField()
	History = models.IntegerField()
	Adventure = models.IntegerField()
	Mystery = models.IntegerField()