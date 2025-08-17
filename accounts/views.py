from django.shortcuts import render, redirect, get_object_or_404
from .forms import TransactionForm
from .models import Transaction, Account

def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'accounts/create_transaction.html', {'form': form})


def transaction_list(request):
    transactions = Transaction.objects.order_by('-created_at')
    return render(request, 'accounts/transaction_list.html', {'transactions': transactions})


def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    try:
        transaction.delete_transaction()
    except ValueError as e:
        print(e)
    return redirect('transaction_list')


def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'accounts/account_list.html', {'accounts': accounts})