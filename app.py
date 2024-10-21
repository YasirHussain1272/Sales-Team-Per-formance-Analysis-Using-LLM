from flask import Flask, jsonify, request
import pandas as pd
import requests

app = Flask(__name__)

# Load sales data
data = pd.read_csv('sales_performance_data.csv')

# Endpoint for individual sales representative performance analysis
@app.route('/api/rep_performance', methods=['GET'])
def rep_performance():
    rep_id = request.args.get('rep_id')
    if rep_id is None:
        return jsonify({"error": "rep_id parameter is required"}), 400

    rep_data = data[data['rep_id'] == int(rep_id)]
    if rep_data.empty:
        return jsonify({"error": "Sales representative not found"}), 404

    # Prepare input for LLM
    rep_info = rep_data.to_dict(orient='records')
    response = analyze_performance(rep_info)

    return jsonify(response)

# Endpoint for overall sales team performance summary
@app.route('/api/team_performance', methods=['GET'])
def team_performance():
    team_summary = data.groupby('rep_name')['sales_amount'].sum().reset_index()
    response = analyze_performance(team_summary.to_dict(orient='records'))
    return jsonify(response)

# Endpoint for sales performance trends and forecasting
@app.route('/api/performance_trends', methods=['GET'])
def performance_trends():
    time_period = request.args.get('time_period')
    if time_period not in ['monthly', 'quarterly']:
        return jsonify({"error": "Invalid time_period. Use 'monthly' or 'quarterly'."}), 400

    # Process data based on time period
    if time_period == 'monthly':
        trends = data.groupby(['month', 'rep_name'])['sales_amount'].sum().reset_index()
    else:  # quarterly
        data['quarter'] = pd.to_datetime(data['month']).dt.to_period('Q')
        trends = data.groupby(['quarter', 'rep_name'])['sales_amount'].sum().reset_index()

    response = analyze_performance(trends.to_dict(orient='records'))
    return jsonify(response)

# Function to analyze performance using the LLM
def analyze_performance(data):
    # Here you would call your LLM for analysis
    llm_url = "http://127.0.0.1:11434/query"
    payload = {"data": data}
    
    try:
        llm_response = requests.post(llm_url, json=payload)
        return llm_response.json()  # Assume LLM returns a JSON response
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
