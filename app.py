import yfinance as yf
import matplotlib
matplotlib.use('Agg') # If you do the import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

def fetch_data(ticker, period, interval):
  stock = yf.Ticker(ticker)
  data = stock.history(period=period, interval=interval)
  return data

def calculate_returns(data, return_type):
  if return_type == 'close_to_close':
    close = data['Close']
    returns = close.pct_change()
  elif return_type == 'open_to_close':
    open_prices = data['Open']
    close_prices = data['Close']
    returns = (close_prices - open_prices) / open_prices
  elif return_type == 'high_to_low':
    high_prices = data['High']
    low_prices = data['Low']
    returns = (high_prices - low_prices) / low_prices
  else:
    raise ValueError('Invalid return type')
  return returns.dropna()

def plot_histogram(returns):
  plt.hist(returns, bins=50)
  plt.xlabel('Returns (%)')
  mean = returns.mean()
  kurtosis = returns.kurtosis()
  plt.title(f'Mean: {mean:.2f}%, Kurtosis: {kurtosis:.2f}')
  plt.savefig('static/histogram.png')

def calculate_statistics(returns):
  positive_returns = returns[returns > 0]
  negative_returns = returns[returns < 0]
  positive_count = positive_returns.count()
  negative_count = negative_returns.count()
  positive_mean = positive_returns.mean()
  negative_mean = negative_returns.mean()
  positive_frequency = positive_count / returns.count()
  negative_frequency = negative_count / returns.count()
  positive_adjusted_returns = positive_mean * positive_frequency
  negative_adjusted_returns = negative_mean * negative_frequency
  return positive_count, negative_count, positive_mean, negative_mean, positive_frequency, negative_frequency, positive_adjusted_returns, negative_adjusted_returns

def main(ticker, period, interval, return_type):
  data = fetch_data(ticker, period, interval)
  returns = calculate_returns(data, return_type)
  plot_histogram(returns)
  positive_count, negative_count, positive_mean, negative_mean, positive_frequency, negative_frequency, positive_adjusted_returns, negative_adjusted_returns = calculate_statistics(returns)
  return ticker, returns.mean(), returns.kurtosis(), positive_count, negative_count, positive_mean, negative_mean, positive_frequency, negative_frequency, positive_adjusted_returns, negative_adjusted_returns, url_for('static', filename='histogram.png')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
  ticker = request.form['ticker']
  period = request.form['period']
  interval = request.form['interval']
  return_type = request.form['return_type']
  ticker, mean, kurtosis, positive_count, negative_count, positive_mean, negative_mean, positive_frequency, negative_frequency, positive_adjusted_returns, negative_adjusted_returns, histogram_url = main(ticker, period, interval, return_type)
  return render_template('results.html', ticker=ticker, mean=mean, kurtosis=kurtosis, positive_count=positive_count, negative_count=negative_count, positive_mean=positive_mean, negative_mean=negative_mean, positive_frequency=positive_frequency, negative_frequency=negative_frequency, positive_adjusted_returns=positive_adjusted_returns, negative_adjusted_returns=negative_adjusted_returns, histogram_url=histogram_url)


if __name__ == '__main__':
  app.run()