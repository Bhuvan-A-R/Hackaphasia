This is an AI-Enabled Virtual Health Assistant for Refugees

Dataset Links:

https://www.kaggle.com/datasets/dogcdt/synapse

How to Run Locally:

1. Clone the Repository

bash:
git clone https://github.com/your-username/Hackaphasia
cd Hackphasia

2. Install Requirements
 
bash:
pip install flask pandas spacy
python -m spacy download en_core_web_sm

3. Add Dataset
   
Place SYNAPSE_with_Detailed_Guidance.csv in the project folder.
It should have columns like:
Symptoms, Age, Description, Severity, Final Recommendation

4. Start the App

bash:
python app.py

Then open in browser:
http://127.0.0.1:5000
