# Cloud Computing Coursework Project 2022

This project is a web app built using [Dash by Plotly](https://plotly.com/dash/); Dash is a framework built on top of Flask, (itself a web development framework built on top of Python) that allows for web development to be conducted entirely in Python without the need for HTML or CSS.

The project relies heavily on the [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) library to visualise the application.

The application provides financial data through price history and technical analysis charts on stocks listed on the S&P 500 and FTSE 100 respectively. This information is sourced through the `yfinance` python module, and then stored within a cloud database hosted by `Google BigQuery`, where it is served into the app.

This information is then returned as a feed of cards, each of which contains:

- The stock's ticker, name, and logo
- A dropdown component featuring information on the price, the sector/industry, company location and website, and analyst recommendations
- A chart created via plotly.graph_objects, comprised of 4 subplots: A candlestick price chart, a volume chart, a moving average convergence divergence chart (MACD), and a Stochastic chart.

<img width="1345" alt="Screenshot 2022-04-04 at 15 48 02" src="https://user-images.githubusercontent.com/58397502/161569986-1bec9f1f-21b2-4567-b988-d74c8309b1e6.png">

The application also integrates with `NewsAPI` in order to provide a feed of popular US business headlines in the sidebar.

<img width="250" alt="Screenshot 2022-04-04 at 15 48 39" src="https://user-images.githubusercontent.com/58397502/161570121-c01f52c2-9bc2-4ba0-80eb-23b7a93be1cc.png">

# How to Use

1. Clone repository + install relevant libraries
2. Create config.py file within `project` directory
3. In config.py, declare a variable called `api_key`. Set this variable equal to the API key sourced from `NewsAPI` [here](https://newsapi.org/register)
4. Google BigQuery service account credentials for a project are provided as a json file; When this file is obtained, add it to the `project` directory
<img width="302" alt="Screenshot 2022-04-04 at 16 06 55" src="https://user-images.githubusercontent.com/58397502/161574156-85debf19-aed4-4ee7-9d5b-f677cdeae1c3.png">
5. Go to line 17 in project/functions.py where the JSON file that stores credentials is referenced; update the filename here to your file containing your credentials.
