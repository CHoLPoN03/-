import secrets
from django.db import models
from django.utils import timezone

def new_account_number():
    return ''.join(secrets.choice("0123456789") for _ in range(10))

class BalanceSheetItem(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=10, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class BalanceGroup(models.Model):
    item = models.ForeignKey(BalanceSheetItem, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ('item', 'name')

    def __str__(self):
        return f"{self.item} - {self.name}"

class Account(models.Model):
    TYPE_CHOICES = [
        ("active", "Актив"),
        ("passive", "Пассив"),
        ("active_passive", "Активно-пассивный"),
    ]

    number = models.CharField(max_length=10, unique=True, default=new_account_number)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    group = models.ForeignKey(BalanceGroup, on_delete=models.CASCADE, related_name="accounts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.number} - {self.name}"

class Transaction(models.Model):
    debit_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='debit_transactions')
    credit_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_reversal = models.BooleanField(default=False)
    original_transaction = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.created_at.date()} | {self.debit_account.name} -> {self.credit_account.name} | {self.amount}"

    def save(self, *args, **kwargs):
        if not self.debit_account or not self.credit_account:
            raise ValueError("Оба счета должны быть выбраны")
        if self.amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")

        debit_type = self.debit_account.type
        credit_type = self.credit_account.type

        if not hasattr(self.debit_account, 'balance'):
            self.debit_account.balance = 0
        if not hasattr(self.credit_account, 'balance'):
            self.credit_account.balance = 0

        if debit_type == 'active' and credit_type == 'active':
            self.debit_account.balance += self.amount
            self.credit_account.balance -= self.amount
        elif debit_type == 'passive' and credit_type == 'passive':
            self.debit_account.balance -= self.amount
            self.credit_account.balance += self.amount
        elif debit_type == 'active' and credit_type == 'passive':
            self.debit_account.balance += self.amount
            self.credit_account.balance += self.amount
        elif debit_type == 'passive' and credit_type == 'active':
            self.debit_account.balance -= self.amount
            self.credit_account.balance -= self.amount
        else:
            raise ValueError("Неподдерживаемая комбинация типов счетов")

        self.debit_account.save()
        self.credit_account.save()
        super().save(*args, **kwargs)

    def create_reversal(self, description=None):
        description = description or f"Сторно транзакции #{self.id}"
        reversal = Transaction.objects.create(
            debit_account=self.credit_account,
            credit_account=self.debit_account,
            amount=self.amount,
            description=description,
            is_reversal=True,
            original_transaction=self
        )
        return reversal

    def delete_transaction(self):
        if self.is_deleted:
            raise ValueError("Транзакция уже удалена")
        self.create_reversal(description=f"Отмена транзакции #{self.id}")
        self.is_deleted = True
        self.save()
