import spacy
from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import os
import re
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Load and Process Dataset
try:
    df = pd.read_csv('SYNAPSE_with_Detailed_Guidance.csv')
    df = df.astype(str)

    symptom_data = []
    all_symptoms = set()
    for _, row in df.iterrows():
        symptoms_list = [symptom.strip() for symptom in row['Symptoms'].lower().split(',')]
        symptom_data.append(row.to_dict())
        for symptom in symptoms_list:
            all_symptoms.add(symptom)
except FileNotFoundError:
    print("CSV not found")
    exit()

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query', '').lower().strip()

    # emergency / service locator
    if 'hospital' in user_query or 'service locator' in user_query or 'emergency' in user_query:
        return jsonify({
            "response": (
                "🚑 <b>Emergency Options:</b><br>"
                "➡️ <a href='https://www.google.com/maps/search/nearby+hospitals' target='_blank'><b>Open Map (Nearby Hospitals)</b></a><br>"
                "➡️ <a href='https://www.practo.com/' target='_blank'><b>Book Appointment Online</b></a>"
            )
        })

    user_info = {'symptoms': [], 'age': None}

    # match multiple symptoms manually
    for symptom in all_symptoms:
        if symptom in user_query:
            user_info['symptoms'].append(symptom)

    # age (optional)
    age_match = re.search(r'(\d+-\d+\s*years|\b\d+\b)', user_query)
    if age_match:
        age_str = age_match.group(0)
        user_info['age'] = age_str.lower().replace(' ', '')

    # If multiple symptoms and no age, show combined descriptions
    if user_info['symptoms'] and not user_info['age']:
        descriptions = []
        for s in user_info['symptoms']:
            descs = [
                row['Description'] for row in symptom_data
                if s in [sym.strip() for sym in row['Symptoms'].lower().split(',')]
            ]
            if descs:
                descriptions.append(f"<b>{s}</b>: {random.choice(descs)}")
        if descriptions:
            return jsonify({"response": "<br>".join(descriptions)})
        else:
            return jsonify({"response": "No description found for the provided symptoms."})

    # full match (symptoms + age)
    if user_info['symptoms'] and user_info['age']:
        best_match = None
        max_symptom_matches = 0
        for row_data in symptom_data:
            symptoms_in_row = [s.strip() for s in row_data['Symptoms'].lower().split(',')]
            symptom_matches = len(set(symptoms_in_row).intersection(user_info['symptoms']))
            if symptom_matches > max_symptom_matches and row_data['Age'].lower().replace(' ', '') == user_info['age'].lower().replace(' ', ''):
                best_match = row_data
                max_symptom_matches = symptom_matches

        if best_match:
            return jsonify({"response": (
                f"Based on your input:<br>"
                f"📝 <b>Description:</b> {best_match['Description']}<br>"
                f"⚠️ <b>Severity:</b> {best_match['Severity']}<br>"
                f"✅ <b>Final Recommendation:</b> {best_match['Final Recommendation']}"
            )})
        else:
            return jsonify({"response": (
                "I'm sorry, I couldn't find a perfect match.<br>"
                "➡️ <a href='https://www.google.com/maps/search/nearby+hospitals' target='_blank'><b>Open Map (Nearby Hospitals)</b></a><br>"
                "➡️ <a href='https://www.practo.com/' target='_blank'><b>Book Appointment Online</b></a>"
            )})

    if not user_info['symptoms']:
        return jsonify({"response": "Please mention at least one symptom."})

    return jsonify({"response": "Please provide your age for a more accurate match."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
