import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class Model :

    model : DecisionTreeClassifier
    
    def __init__(self) :
        
        # 1. Load from sklean.datasets the Iris dataset after importing load iris data object and 
        # use a variable-name iris to store the returned value: iris = load iris();

        self.iris = load_iris()

        # 2. Extract from iris.data the petal length and width then affect them to an 
        # input data as a new variable X

        self.iris_df = pd.DataFrame(self.iris.data, columns=["Sepal_Length_cm",
                                                    "Sepal_Width_cm",
                                                    "Petal_Length_cm",
                                                        "Petal_Width_cm"])

        X = self.iris_df[["Sepal_Length_cm", "Sepal_Width_cm", "Petal_Length_cm", "Petal_Width_cm"]]
        Y = self.iris.target

        print(self.iris.target)

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

        # 4. Import DecisionTreeClassifier from sklearn.tree and create a new object treeClassifer 
        # with a maximum depth value equal to 2.

        self.model = DecisionTreeClassifier(max_depth=2)

        # 5. Fit your decision tree on your data

        self.model.fit(X_train, y_train)

        # 6. We test the model accuracy
        y_pred = self.model.predict(X_test)

        print(f"Accuracy : {accuracy_score(y_test, y_pred)}")

    def predict(self, sepal_length, sepal_width, petal_length, petal_width) :

        return self.iris.target_names[self.model.predict([[sepal_length, sepal_width, petal_length, petal_width]])]
    