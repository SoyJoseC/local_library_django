from django.db import models
from django.db.models.base import Model
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from datetime import date
# Create your models here.

class Genre(models.Model):
    """A class for Genre model"""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        return self.name

class Language(models.Model):
    """A class for Language model"""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Book(models.Model):
    """A class defining a Book object and its atributes"""

    title = models.CharField(max_length=200, help_text="Title of the book")
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Summary of the book")
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language = models.ForeignKey('Language', on_delete=models.RESTRICT, null=False,blank=False)

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'



class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    due_back = models.DateField(null=True,blank=True)
    imprint = models.CharField(max_length=200)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        """Meta definition for BookInstance."""
        ordering = ['due_back']
        verbose_name = 'BookInstance'
        verbose_name_plural = 'BookInstances'
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """Unicode representation of BookInstance."""
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
