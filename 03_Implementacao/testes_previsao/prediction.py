# fit an ARIMA model and plot residual errors
import datetime
from pandas import read_csv
from pandas import DataFrame
from statsmodels.tsa.arima.model import ARIMA
from matplotlib import pyplot

# load dataset
def excel_date_parser(x):
    epoch = datetime.datetime(1899, 12, 30)
    td = datetime.timedelta(days=float(x))
    y = epoch + td
    return y

series = read_csv('AustinSemana.csv', header=0, index_col=0, parse_dates=True, squeeze=True, date_parser=excel_date_parser)
series.index = series.index.to_period('H')


# fit model
# lag value to P for autoregression, uses a difference order of D to make the time series stationary, and uses a moving average model of Q.
#model = ARIMA(series, order=(5,1,0))
#model_fit = model.fit()


# summary of fit model
#print(model_fit.summary())


# line plot of residuals
#residuals = DataFrame(model_fit.resid)
#residuals.plot()
#pyplot.show()


# density plot of residuals
#residuals.plot(kind='kde')
#pyplot.show()


# summary stats of residuals
#print(residuals.describe()) # media != 0? erro : ok

##

# split into train and test sets
X = series.values
size = int(len(X) * 6/7)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()


# walk-forward validation
for t in range(len(test)):
	model = ARIMA(history, order=(5,1,0))
	model_fit = model.fit()
	output = model_fit.forecast()
	yhat = output[0]
	predictions.append(yhat)
	obs = test[t]
	history.append(obs)
	print('predicted=%f, expected=%f' % (yhat, obs))

# evaluate forecasts
from sklearn.metrics import mean_squared_error
from math import sqrt
rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
# plot forecasts against actual outcomes
series.plot()
pyplot.plot(series.index[-len(test):], predictions, color='red')
pyplot.show()

# erro absoluto e relativo