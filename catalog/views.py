from django.shortcuts import render
from .models import Book, Author, Genre, BookInstance
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm
# Create your views here.

def index(request):
    """View function for home page of site."""
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    num_books_harry_title = Book.objects.filter(title__icontains ='harry').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_harry_title': num_books_harry_title,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    #template_name = 'book_list.html'
    # context_object_name = 'my_book_list'   # your own name for the list as a template variable

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model=Book
    #template_name='book_detail.html'
    
class AuthorListView(generic.ListView):
    model = Author
    #template_name='author_list.html'
    paginate_by=10

class AuthorDetailView(generic.DetailView):
    model = Author
    #template_name='author_detail.html'

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name='catalog/bookinstance_list_borrowed_user.html'
    paginate_by=10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required='catalog.can_mark_returned'
    template_name = 'catalog/all_loaned_books.html'
    context_object_name = 'borrowed_books_list'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    model = Author
    permission_required='catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(LoginRequiredMixin, PermissionRequiredMixin,UpdateView):
    model = Author
    permission_required='catalog.can_mark_returned'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(LoginRequiredMixin, PermissionRequiredMixin,DeleteView):
    model = Author
    permission_required='catalog.can_mark_returned'
    success_url = reverse_lazy('authors')

class BookCreate(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    model = Book
    permission_required='catalog.can_mark_returned'
    fields = '__all__'

class BookUpdate(LoginRequiredMixin, PermissionRequiredMixin,UpdateView):
    model = Book
    permission_required='catalog.can_mark_returned'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(LoginRequiredMixin, PermissionRequiredMixin,DeleteView):
    model = Book
    permission_required='catalog.can_mark_returned'
    success_url = reverse_lazy('books')