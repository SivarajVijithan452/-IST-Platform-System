from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import yfinance as yf
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import requests  
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Stock price prediction routes

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    stock_symbol = request.form['stockSymbol']

    stock_data = yf.Ticker(stock_symbol)
    historical_data = stock_data.history(period="1y")

    # Check if historical_data is not empty
    if historical_data.empty:
        return jsonify({'error': 'No data available for the provided stock symbol.'})

    closing_prices = historical_data['Close']

    # Check if closing_prices is not empty
    if closing_prices.empty:
        return jsonify({'error': 'No closing prices available for the provided stock symbol.'})

    closing_prices.index = pd.date_range(start=closing_prices.index[0], periods=len(closing_prices), freq='D')

    train_size = int(len(closing_prices) * 0.8)
    train_data, test_data = closing_prices[:train_size], closing_prices[train_size:]

    order = (5, 1, 0)
    model = ARIMA(train_data, order=order)
    model_fit = model.fit()

    forecast_steps = len(test_data)
    forecast_index = pd.date_range(start=test_data.index[0], periods=forecast_steps, freq='D')
    forecast_series = pd.Series(model_fit.forecast(steps=forecast_steps), index=forecast_index)

    chart_data = {'labels': forecast_series.index.strftime('%Y-%m-%d').tolist(),
                  'actual_prices': closing_prices.tolist(),
                  'fitted_values': model_fit.fittedvalues.tolist(),
                  'forecasted_prices': forecast_series.tolist()}

    return jsonify(chart_data)


# Login routes

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace this with your actual authentication logic
        if username == "user" and password == "pass":
            session['logged_in'] = True
            return redirect(url_for('index'))  # Redirect to the index route after successful login
        else:
            error_message = "Incorrect username or password."

    return render_template('login.html', error_message=error_message)


@app.route('/data', methods=['GET', 'POST'])
def data():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    api_key = None
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        api_key = request.form['api_key']

        # Use these dates and API key to fetch historical data using yfinance
        historical_prices = get_historical_data("AAPL", start_date, end_date, api_key)

        # Pass the data to the template
        return render_template('data.html', historical_prices=historical_prices, api_key=api_key, start_date=start_date, end_date=end_date)

    return render_template('data.html', api_key=api_key, start_date=start_date, end_date=end_date)

def get_historical_data(stock_symbol, start_date, end_date, api_key=None):
    stock_data = yf.Ticker(stock_symbol)
    historical_data = stock_data.history(start=start_date, end=end_date)
    return historical_data

@app.route('/stock_api')
def stock_api():
    # List of 50 stock symbols and their corresponding company names
    stock_symbols = ['AAPL', 'GOOGL', 'MSN', 'AMZN', 'FB', 'TSLA', 'IBM', 'MSFT', 'INTC', 'CSCO',
                     'NVDA', 'PYPL', 'NFLX', 'BA', 'DIS', 'GS', 'JPM', 'WMT', 'VZ', 'CVX',
                     'GE', 'XOM', 'KO', 'PEP', 'IBM', 'GM', 'F', 'T', 'C', 'BAC', 'IBM',
                     'PFE', 'GILD', 'MRK', 'JNJ', 'GOOGL', 'AAPL', 'AMZN', 'FB', 'TSLA', 'MSFT',
                     'NVDA', 'PYPL', 'NFLX', 'BA', 'DIS', 'GS', 'JPM', 'WMT', 'VZ', 'CVX']

    company_names = ['Apple Inc.', 'Alphabet Inc.', 'Morgan Stanley', 'Amazon.com Inc.', 'Facebook Inc.',
                     'Tesla Inc.', 'IBM', 'Microsoft Corporation', 'Intel Corporation', 'Cisco Systems Inc.',
                     'NVIDIA Corporation', 'PayPal Holdings Inc.', 'Netflix Inc.', 'Boeing Co.', 'Walt Disney Co.',
                     'Goldman Sachs Group Inc.', 'JPMorgan Chase & Co.', 'Walmart Inc.', 'Verizon Communications Inc.', 'Chevron Corporation',
                     'General Electric Co.', 'Exxon Mobil Corporation', 'The Coca-Cola Company', 'PepsiCo Inc.', 'IBM', 'General Motors Company',
                     'Ford Motor Company', 'AT&T Inc.', 'Citigroup Inc.', 'Bank of America Corporation', 'IBM',
                     'Pfizer Inc.', 'Gilead Sciences Inc.', 'Merck & Co. Inc.', 'Johnson & Johnson', 'Alphabet Inc.', 'Apple Inc.',
                     'Amazon.com Inc.', 'Facebook Inc.', 'Tesla Inc.', 'Microsoft Corporation', 'NVIDIA Corporation', 'PayPal Holdings Inc.',
                     'Netflix Inc.', 'Boeing Co.', 'Walt Disney Co.', 'Goldman Sachs Group Inc.', 'JPMorgan Chase & Co.', 'Walmart Inc.',
                     'Verizon Communications Inc.', 'Chevron Corporation']

    stock_data = [{'symbol': symbol, 'company_name': company_name} for symbol, company_name in zip(stock_symbols, company_names)]

    return render_template('stockAPI.html', stock_data=stock_data)



# Logout route
@app.route('/logout')
def logout():
    # Clear the 'logged_in' session variable
    session.pop('logged_in', None)
    
    # Redirect the user to the login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
