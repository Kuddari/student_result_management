import requests

# API endpoint
url = 'http://161.139.153.153:50000/deploy/inference'

# Headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Data to send
data = {"deploy_id": 10,
    "data_infer": [[0.0,0.0,0.707,0.707,0.707,0.509,0.571,0.577,0.604,0.5,0.514,0.48,0.309,0.31,0.312,0.347,0.318,0.27,0.34]]
    
}

# Send POST request
response = requests.post(url, headers=headers, json=data)

# Print the response
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Error:", response.status_code, response.text)
