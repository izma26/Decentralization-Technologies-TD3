from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from data import Model


model = Model()

app = Flask(__name__)


app.secret_key = 'my_secret_key'


@app.route('/')
def view_form():
    return render_template('predict.html', show_form=True)


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        try:
           
            sepal_length = float(request.form['sepal_length'])
            sepal_width = float(request.form['sepal_width'])
            petal_length = float(request.form['petal_length'])
            petal_width = float(request.form['petal_width'])

          
            prediction = model.predict(sepal_length, sepal_width, petal_length, petal_width)

            
            session['prediction'] = prediction
            return {"response" : prediction}
            #redirect(url_for('predict'))



        except Exception as e:
            return jsonify({"error": str(e)})

    elif request.method == 'GET':
        
        prediction = session.get('prediction', None)
        return render_template('predict.html', prediction=prediction, show_form=False)

if __name__ == '__main__':
    app.run()
