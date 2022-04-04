import yfinance as yf
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from ta.trend import MACD
from ta.momentum import StochasticOscillator
import requests
import json
from google.oauth2 import service_account
import pandas_gbq
import config

# CONNECTION TO GOOGLE BIGQUERY

credentials = service_account.Credentials.from_service_account_file('qmulcloud-cw-2022-1375ef7b19b1.json') # REPLACE FILE NAME WITH YOUR SERVICE ACCOUNT CREDENTIALS FILE
project_id = 'qmulcloud-cw-2022'

def company_list(country):

	'''
	Pulls list of company tickers from database
	'''

	df_sql = f"""
	SELECT ticker FROM `stocks.info`
	WHERE country = '{country}'
	"""

	df = pd.read_gbq(df_sql, project_id=project_id, dialect="standard", credentials=credentials)

	company_list = df.ticker.unique()

	return company_list

def get_stock_data(ticker):

	'''
	Returns historical financial data for a given stock ticker
	'''

	df_sql = f"""
	SELECT * FROM `stocks.prices`
	WHERE ticker = '{ticker}'
	"""

	df = pd.read_gbq(df_sql, project_id=project_id, dialect="standard", credentials=credentials)

	#data = yf.download(f"{ticker}", period="ytd", auto_adjust=True)
	#df = pd.DataFrame(data)

	return df

def dict_values(ticker_list):

	'''
	Creates dictionary in {ticker: dataframe of historical prices} format
	'''

	dict = {}
	for ticker in ticker_list:
		values = get_stock_data(ticker)
		dict[ticker]=values
	return dict

def get_stock_info(ticker):

	'''
	Returns additional information about a company for a given stock ticker
	'''

	df_sql = f"""
	SELECT * FROM `stocks.info`
	WHERE ticker = '{ticker}'
	"""

	df = pd.read_gbq(df_sql, project_id=project_id, dialect="standard", credentials=credentials)

	dict = {}

	dict['ticker'] = ticker
	dict['company'] = df['Company'].iloc[0]
	dict['website'] = df['Website'].iloc[0]
	dict['country'] = df['Country'].iloc[0]
	dict['sector'] = df['Sector'].iloc[0]
	dict['industry'] = df['Industry'].iloc[0]
	dict['price'] = df['Price'].iloc[0]
	dict['price_target'] = df['Price_Target'].iloc[0]
	dict['logo'] = df['Logo'].iloc[0]
	dict['analyst_recommendation'] = df['Analyst_Recommendation'].iloc[0]

	return dict


def get_headlines():

	'''
	Returns the top business headlines from News API
	'''

	api_key = config.api_key

	news_url = ('https://newsapi.org/v2/top-headlines?'
	   'country=us&'
	   'sortBy=popularity&'
	   'category=business&'
	   f'apiKey={api_key}')

	response = requests.get(news_url)
	response = response.json()

	top_headline = [response['articles'][0]['title'], response['articles'][0]['url']]
	second_headline = [response['articles'][1]['title'], response['articles'][1]['url']]
	third_headline = [response['articles'][2]['title'], response['articles'][2]['url']]
	fourth_headline = [response['articles'][3]['title'], response['articles'][3]['url']]
	fifth_headline = [response['articles'][4]['title'], response['articles'][4]['url']]

	article_dict = {}

	article_dict['first'] = top_headline
	article_dict['second'] = second_headline
	article_dict['third'] = third_headline
	article_dict['fourth'] = fourth_headline
	article_dict['fifth'] = fifth_headline

	return article_dict


def create_card(ticker, values):

	'''
	Responsible for creating cards for dashboard. Each card has the stock's name, a drop down filled with more information, 
	and charts with subplots showing price, volume and other technical analysis indicators.
	'''

	# removing all empty dates
	# build complete timeline from start date to end date
	dt_all = pd.date_range(start=min(values['Date']),end=max(values['Date']))
	# retrieve the dates that ARE in the original datset
	dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(values['Date'])]
	# define dates with missing values
	dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

	macd = MACD(close=values['Close'],
				window_slow=26,
				window_fast=12,
				window_sign=9)

	stoch = StochasticOscillator(high=values['High'],
								close=values['Close'],
								low=values['Low'],
								window=14,
								smooth_window=3)

	fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.01)

	# Plot Candlestick chart

	fig.add_trace(go.Candlestick(x=values['Date'],
  		open=values['Open'],
  		high=values['High'],
  		low=values['Low'],
  		close=values['Close']))

	# Plot volume trace

	fig.add_trace(go.Bar(x=values['Date'], 
                     y=values['Volume']
                    ), row=2, col=1)

	# Plot MACD trace

	fig.add_trace(go.Bar(x=values['Date'], 
                     y=macd.macd_diff()
                    ), row=3, col=1)
	
	fig.add_trace(go.Scatter(x=values['Date'],
                         y=macd.macd(),
                         line=dict(color='black', width=2)
                        ), row=3, col=1)
	
	fig.add_trace(go.Scatter(x=values['Date'],
                         y=macd.macd_signal(),
                         line=dict(color='blue', width=1)
                        ), row=3, col=1)

	# Plot stochastics trace 

	fig.add_trace(go.Scatter(x=values['Date'],
                         y=stoch.stoch(),
                         line=dict(color='black', width=2)
                        ), row=4, col=1)
	
	fig.add_trace(go.Scatter(x=values['Date'],
                         y=stoch.stoch_signal(),
                         line=dict(color='blue', width=1)
                        ), row=4, col=1)

	fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

	fig.update_layout( 
                  showlegend=False, 
                  xaxis_rangeslider_visible=False,
                  xaxis_rangebreaks=[dict(values=dt_breaks)])

	fig.update_yaxes(title_text="Price", row=1, col=1)
	fig.update_yaxes(title_text="Volume", row=2, col=1)
	fig.update_yaxes(title_text="MACD", showgrid=False, row=3, col=1)
	fig.update_yaxes(title_text="Stoch", row=4, col=1)

	stock_info = get_stock_info(ticker)

	# Create structure of card that houses and displays charts + info

	chart = html.Div(dbc.Card([
				dbc.CardHeader(dbc.Row([
								dbc.Col(html.Div(html.H4(f"${ticker}", className="card-title")), align="center", width=5),
								dbc.Col(html.Div(html.H4(f"{stock_info['company']}", className="card-title")), align="center", width=5),
								dbc.Col(html.Img(src=stock_info['logo'], className="img-thumbnail"))
								])),
				dbc.CardBody(
					[
					dbc.Accordion(
					dbc.AccordionItem(
					dbc.ListGroup(
						[
							dbc.ListGroupItem(f"Price: ${stock_info['price']}"),
							dbc.ListGroupItem(f"Price Target: ${stock_info['price_target']}"),
							dbc.ListGroupItem(f"Sector: {stock_info['sector']}"),
							dbc.ListGroupItem(f"Industry: {stock_info['industry']}"),
							dbc.ListGroupItem(f"Country: {stock_info['country']}"),
							dbc.ListGroupItem(f"Analyst Recommendation: {stock_info['analyst_recommendation']}"),
							dbc.ListGroupItem(f"Website: {stock_info['website']}", href=f"{stock_info['website']}", color="primary", target="_blank")
						],
						horizontal = True
						), title='More Info'
					),
					start_collapsed=True
					),
					dcc.Graph(figure=fig)
						],className="card"
					)
				]
			)
		)

	return chart

def get_charts(ticker_list, dict):
	charts = []
	for ticker in ticker_list:
		charts.append(create_card(ticker, dict[ticker]))
	return charts