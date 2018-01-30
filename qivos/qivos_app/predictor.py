import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score


class DiabPred(object):

    def __init__(self):
        # Load the diabetes dataset
        self.regr = None

        diabetes = datasets.load_diabetes()

        # Use only one feature
        diabetes_X = diabetes.data[:, np.newaxis, 2]

        # Split the data into training/testing sets
        self.diabetes_X_train = diabetes_X[:-20]
        self.diabetes_X_test = diabetes_X[-20:]

        # Split the targets into training/testing sets
        self.diabetes_y_train = diabetes.target[:-20]
        diabetes_y_test = diabetes.target[-20:]

    def train(self):
        # Create linear regression object
        self.regr = linear_model.LinearRegression()

        # Train the model using the training sets
        self.regr.fit(self.diabetes_X_train, self.diabetes_y_train)

    def predict(self, input_data):
        # Make predictions using the testing set
        diabetes_y_pred = self.regr.predict(input_data)

        return diabetes_y_pred
        # The coefficients
        #print('Coefficients: \n', self.regr.coef_)
        # The mean squared error
        #print("Mean squared error: %.2f" % mean_squared_error(self.diabetes_y_test, diabetes_y_pred))
        # Explained variance score: 1 is perfect prediction
        #print('Variance score: %.2f' % r2_score(diabetes_y_test, diabetes_y_pred))