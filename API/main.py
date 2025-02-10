from flask import Flask, request, render_template
from data import Model

model = Model()

app = Flask(__name__)
 
# Set a secret key for encrypting session data
app.secret_key = 'my_secret_key'
 
 
# To render a login form 
@app.route('/')
def view_form():
    return render_template('predict.html')
 
# Send prediction result
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        sepal_length = request.form['sepal_length']
        sepal_width = request.form['sepal_width']
        petal_length = request.form['petal_length']
        petal_width = request.form['petal_width']
        print(petal_length, petal_width)
        
        return {"response":model.predict(sepal_length, sepal_width, petal_length, petal_width)[0]}
    else:
        return render_template('predict.html')
 
if __name__ == '__main__':
    app.run()