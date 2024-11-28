from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length = 150, unique=True ,db_index=True)
	icon = models.FileField(upload_to = "category/")
	create_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.name

class Writer(models.Model):
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=150, unique=True ,db_index=True)
	bio = models.TextField()
	pic = models.FileField(upload_to = "writer/")
	create_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.name

class Book(models.Model):
	writer = models.ForeignKey(Writer, on_delete = models.CASCADE)
	category = models.ForeignKey(Category, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=100, db_index=True)
	price = models.IntegerField()
	stock = models.IntegerField()
	coverpage = models.FileField(upload_to = "coverpage/")
	bookpage = models.FileField(upload_to = "bookpage/")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	totalreview = models.IntegerField(default=1)
	totalrating = models.IntegerField(default=5)
	status = models.IntegerField(default=0)
	description = models.TextField()

	def __str__(self):
	    return self.name

class Review(models.Model):
	RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
	rating = models.IntegerField(choices=RATING_CHOICES)
	comment = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		unique_together = ('user', 'book')  # One review per user per book

	def __str__(self):
		return f'{self.user.username} rated {self.book.title} {self.rating} stars'

class Slider(models.Model):
	title = models.CharField(max_length=150)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	slideimg = models.FileField(upload_to = "slide/")

	def __str__(self):
		return self.title

