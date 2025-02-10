from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from data import Model

# Initialisation du modèle
model = Model()

app = Flask(__name__)

# Clé secrète pour Flask (nécessaire pour gérer les sessions)
app.secret_key = 'my_secret_key'

# Route pour afficher le formulaire
@app.route('/')
def view_form():
    return render_template('predict.html', show_form=True)

# Route pour obtenir la prédiction et rediriger vers /predict
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        try:
            # Récupération des valeurs saisies par l'utilisateur
            sepal_length = float(request.form['sepal_length'])
            sepal_width = float(request.form['sepal_width'])
            petal_length = float(request.form['petal_length'])
            petal_width = float(request.form['petal_width'])

            # Prédiction avec le modèle
            prediction = model.predict(sepal_length, sepal_width, petal_length, petal_width)

            # Stockage du résultat dans la session pour l'afficher après redirection
            session['prediction'] = prediction
            return {"response" : prediction}
            #redirect(url_for('predict'))



        except Exception as e:
            return jsonify({"error": str(e)})

    elif request.method == 'GET':
        # Vérifie s'il y a une prédiction stockée et l'affiche sans formulaire
        prediction = session.get('prediction', None)
        return render_template('predict.html', prediction=prediction, show_form=False)

if __name__ == '__main__':
    app.run()
