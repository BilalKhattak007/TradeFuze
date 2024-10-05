from decimal import Decimal
from django.db import models

class Wallet(models.Model):
    starting_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    withdraw_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

   
    def save(self, *args, **kwargs):
        # Ensure current_balance is initialized with starting_balance if it's zero (new wallet)
        if self.pk is None:  # This means the wallet is being created for the first time
            self.current_balance = self.starting_balance
        super(Wallet, self).save(*args, **kwargs)

    def deposit(self, amount):
        # Convert the amount to a Decimal
        amount = Decimal(amount)
        self.deposit_amount += amount
        self.current_balance += amount
        self.save()

    def withdraw(self, amount):
        # Convert the amount to a Decimal
        amount = Decimal(amount)
        if self.current_balance >= amount:
            self.withdraw_amount += amount
            self.current_balance -= amount
            self.save()
        else:
            raise ValueError("Insufficient balance to withdraw")

    def __str__(self):
        return f"Wallet - Starting: {self.starting_balance}, Current: {self.current_balance}"



class Trade(models.Model):
    TRADE_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    trade_date = models.DateField()
    entry_price = models.DecimalField(max_digits=15, decimal_places=2)
    exit_price = models.DecimalField(max_digits=15, decimal_places=2)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    stop_loss = models.DecimalField(max_digits=15, decimal_places=2)
    reason = models.TextField()
    leverage_used = models.IntegerField(default=1)
    profit_or_loss = models.DecimalField(max_digits=15, decimal_places=2)
    winning_trade = models.BooleanField(default=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)  # link to Wallet model

    def apply_profit_or_loss(self):
        # Ensure profit_or_loss is a Decimal
        profit_or_loss = Decimal(self.profit_or_loss)

        # Update the wallet's current balance using Decimal arithmetic
        if self.winning_trade:
            self.wallet.current_balance += profit_or_loss
        else:
            self.wallet.current_balance -= profit_or_loss

        self.wallet.save()

    def save(self, *args, **kwargs):
        # Apply the profit or loss to the current balance before saving the trade
        self.apply_profit_or_loss()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trade on {self.trade_date} ({self.trade_type.upper()}) - {'Win' if self.winning_trade else 'Loss'}"