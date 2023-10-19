import datasets
import pandas as pd
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
from uuid import uuid4

dataset = datasets.load_dataset('userDATASET', split='train') #데이터셋 입력
df = pd.DataFrame(dataset)

app = Flask(__name__)
CORS(app)

start_index = 2000

@app.route('/job', methods=['GET'])
def job():
    global start_index
    if start_index >= len(df):
        print('Done')
        return jsonify({
            "message": "No more data"
        })
        
    job_data = df[start_index:start_index+5].to_json(orient="records")
    job_id = f"{start_index}-{uuid4()}"
    start_index += 5
    print("[+] 작업 생성 - ", job_id)
    response_data = jsonify({
        "job_id": job_id,
        "job_data": json.loads(job_data)
    })
    response = Response(response_data.data, mimetype='application/json; charset=utf-8')
    return response

@app.route('/job', methods=['POST'])
def job_result():
    try:
        raw_data = request.data.decode('utf-8')
        json_data = json.loads(raw_data)
        
        job_id = json_data['job_id']
        job_result = json_data['job_result']
        
        print("\033[32m[+] 작업 완료 및 저장 완료 - ", job_id, "\033[0m")
        with open(f'job_results/{job_id}.jsonl', 'w', encoding='utf-8') as f:
            for data in job_result:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    response_data = jsonify({
        "status": "ok"
    })
    response = Response(response_data.data, mimetype='application/json; charset=utf-8')
    return response

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Error: {e}")
