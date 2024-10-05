import calendar
from datetime import date, timedelta
from django.shortcuts import render,redirect
from .models import Wallet,Trade
from decimal import Decimal
from django.contrib.auth import logout as auth_logout
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Wallet, Trade
from calendar import month_name
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            auth_login(request, user)
            
            # Redirect to the home page (or another page)
            return redirect('home')  # Redirect to the home page (adjust URL name if necessary)
        else:
            # Invalid login, return to login page with error message
            return redirect('login')  # If login fails, redirect back to login page

    return render(request, 'login.html')



#home:
@login_required
def home(request):
    # Get the first wallet (assuming you are using one wallet)
    wallet = Wallet.objects.first()
    current_balance = wallet.current_balance if wallet else Decimal(0)

    # Get trade data
    trades = Trade.objects.all()

    # Calculate total trades
    total_trades = trades.count()

    # Calculate winning and losing trades
    winning_trades = trades.filter(winning_trade=True).count()
    losing_trades = trades.filter(winning_trade=False).count()

    # Calculate win/loss ratio (handling division by zero)
    if losing_trades > 0:
        win_loss_ratio = Decimal(winning_trades) / Decimal(losing_trades)
    else:
        win_loss_ratio = Decimal(winning_trades)

    # Pie chart data for wins and losses
    pie_labels = ['Wins', 'Losses']
    pie_values = [winning_trades, losing_trades]
    pie_colors = ['#2ca02c', '#d62728']  # Green for Wins, Red for Losses

    # Bar chart (monthly performance) - calculate monthly profits/losses
    if trades.exists():
        first_trade_date = trades.order_by('trade_date').first().trade_date
        current_month = datetime.now().month
        current_year = datetime.now().year

        bar_labels = []
        bar_values = []

        start_year, start_month = first_trade_date.year, first_trade_date.month
        while (start_year < current_year) or (start_year == current_year and start_month <= current_month):
            # Get trades for the current month and year
            month_trades = trades.filter(trade_date__year=start_year, trade_date__month=start_month)

            # Sum profit/loss for the month
            monthly_performance = sum(
                trade.profit_or_loss if trade.winning_trade else -trade.profit_or_loss
                for trade in month_trades
            )

            # Append the results
            bar_labels.append(f"{month_name[start_month]} {start_year}")
            bar_values.append(float(monthly_performance))  # Ensure it's a float for Chart.js

            # Increment month
            if start_month == 12:
                start_month = 1
                start_year += 1
            else:
                start_month += 1
    else:
        bar_labels = ['No Trades']
        bar_values = [0]

    bar_colors = ['#1f77b4'] * len(bar_values)  # Blue for all bars

    return render(request, 'home.html', {
        'current_balance': current_balance,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_loss_ratio': win_loss_ratio.quantize(Decimal("0.01")),  # Limit ratio to 2 decimal places
        'pie_labels': pie_labels,
        'pie_values': pie_values,
        'pie_colors': pie_colors,
        'bar_labels': bar_labels,
        'bar_values': bar_values,
        'bar_colors': bar_colors,
    })

#add trade:
@login_required
def addTrade(request):
     wallet = Wallet.objects.first()  # Adjust based on how wallets are structured in your app
     if request.method == 'POST':
        # Get data from the form
        trade_date = request.POST.get('trade_date')
        entry_price = request.POST.get('entry_price')
        exit_price = request.POST.get('exit_price')
        trade_type = request.POST.get('trade_type')
        stop_loss = request.POST.get('stop_loss')
        reason = request.POST.get('reason')  # Adjust from 'reasoning' in form
        leverage_used = request.POST.get('leverage_used')
        profit_or_loss = request.POST.get('profit_or_loss')
        winning_trade = request.POST.get('winning_trade') == 'on'  # Check if the checkbox is checked
        
        # Convert data to appropriate types
        try:
            entry_price = float(entry_price)
            exit_price = float(exit_price)
            stop_loss = float(stop_loss)
            leverage_used = int(leverage_used)
            profit_or_loss = float(profit_or_loss)
        except ValueError:
            # Handle invalid data error
            return render(request, 'add_trade.html', {'error': 'Invalid input.'})

        # Create a new trade object
        new_trade = Trade(
            trade_date=trade_date or timezone.now().date(),  # Default to current date if not provided
            entry_price=entry_price,
            exit_price=exit_price,
            trade_type=trade_type,
            stop_loss=stop_loss,
            reason=reason,
            leverage_used=leverage_used,
            profit_or_loss=profit_or_loss,
            winning_trade=winning_trade,
            wallet=wallet  # Link the trade to the wallet
        )
        
        # Save the trade, which also updates the wallet balance via the `apply_profit_or_loss` method
        new_trade.save()
        
        # Redirect to a success page or home page after adding the trade
        return redirect('home')  # Adjust the redirection as necessary
     return render(request, 'addTrade.html')

#all trades:
@login_required
def trades(request):
    trades = Trade.objects.all()

    # Set up pagination (10 trades per page)
    paginator = Paginator(trades, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'trades.html', {
        'page_obj': page_obj,
    })

#monthly:
@login_required
def monthlyCal(request):
    # Get the current month, year, and today's date
    today = date.today()
    current_year, current_month = today.year, today.month

    # Query the Trade model for the current month
    trades = Trade.objects.filter(trade_date__year=current_year, trade_date__month=current_month)

    # Build a dictionary mapping each day of the month to its profit/loss
    trade_data = {}
    for trade in trades:
        trade_day = trade.trade_date.day
        if trade_day not in trade_data:
            trade_data[trade_day] = 0  # Initialize
        if trade.winning_trade:
            trade_data[trade_day] += trade.profit_or_loss
        else:
            trade_data[trade_day] -= trade.profit_or_loss

    # Create a calendar for the current month
    cal = calendar.Calendar(firstweekday=6)  # First weekday as Sunday (6)
    days_in_month = cal.itermonthdays4(current_year, current_month)

    calendar_days = []
    for day_tuple in days_in_month:
        year, month, day, weekday = day_tuple

        # Skip days that are not in the current month
        if month != current_month:
            calendar_days.append({'date': '', 'pnl': '', 'color_class': 'bg-white'})
            continue

        # Get profit or loss for the day or default to 0
        pnl = trade_data.get(day, 0)

        # Determine the color based on PnL
        if pnl > 0:
            color_class = 'bg-green-50 hover:bg-green-100'
        elif pnl < 0:
            color_class = 'bg-red-50 hover:bg-red-100'
        else:
            color_class = 'bg-white hover:bg-gray-100'

        # Highlight today
        if date(year, month, day) == today:
            color_class = 'bg-blue-50 hover:bg-blue-100'

        # Append the day to the calendar with its PnL and color
        calendar_days.append({
            'date': day,
            'pnl': f"${pnl:.2f}" if pnl != 0 else 'No Trade',
            'color_class': color_class
        })

    return render(request, 'monthlyCal.html', {
        'calendar_days': calendar_days,
        'month_name': calendar.month_name[current_month],  # Use month name like "October"
        'year': current_year,
    })

#rules:
@login_required
def rules(request):
    return render(request,"rules.html")

#wallet:
@login_required
def wallet(request):
    wallet, created = Wallet.objects.get_or_create(id=1)
    if request.method == 'POST':
        if 'deposit' in request.POST:
            deposit_amount = float(request.POST.get('deposit_amount', 0))
            wallet.deposit(deposit_amount)  # Call deposit method from Wallet model
        elif 'withdraw' in request.POST:
            withdraw_amount = float(request.POST.get('withdraw_amount', 0))
            wallet.withdraw(withdraw_amount)  # Call withdraw method from Wallet model
        
        return redirect('wallet')

    context = {
        'wallet': wallet
    }
    return render(request, 'wallet.html', context)

# Logout View
def logout_view(request):
    auth_logout(request)  # Logs out the user
    return redirect('login')  # Redirects to the login page after logout
