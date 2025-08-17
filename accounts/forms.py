from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['debit_account', 'credit_account', 'amount', 'description']

    def clean(self):
        cleaned_data = super().clean()
        debit = cleaned_data.get('debit_account')
        credit = cleaned_data.get('credit_account')
        amount = cleaned_data.get('amount')

        if not debit or not credit:
            raise forms.ValidationError("Выберите оба счета")
        if amount <= 0:
            raise forms.ValidationError("Сумма должна быть больше нуля")
        return cleaned_data
