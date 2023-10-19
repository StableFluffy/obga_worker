import requests
import json

API = 'http://localhost:5000/api/v1/generate'
SERVER = 'http://서버 아이피:5000/job' #서버 아이피 수정해서 사용

def generation(prompt):
    request = {
        'prompt': prompt,
        'max_new_tokens': 2048,
        'preset': 'LLaMA-Precise', #커스텀 프리셋 적용
        'negative_prompt': '이었다. 였다. 다.',
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 16384,
        'ban_eos_token': False,
        'custom_token_bans': '',
        'skip_special_tokens': True,
        'stopping_strings': [],
        'guidance_scale': 1
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = requests.post(API, json=request, headers=headers)

    if response.status_code == 200:
        result = response.json()['results'][0]['text']
        return result

def run():
    response = requests.get(SERVER)
    if response.status_code != 200:
        print('Failed to get job:', response.text)
        return None
    job = response.json()
    job_id = job['job_id']
    job_data = job['job_data']
    job_idx = int(job_id[:4])

    data_cache = []
    for i, data in enumerate(job_data):
        if len(data["text"]) > 400 and len(data["text"]) < 11000: # 텍스트 길이 조건 수정해서 사용
            prompt = f'{data["text"]}' # 프롬프트 적용
            result = generation(prompt)
            data_cache.append({"index": i + job_idx, "result": result, "source": data["text"]})

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = json.dumps({
        'job_id': job_id,
        'job_result': data_cache
    }, ensure_ascii=False).encode('utf-8')
    response = requests.post(SERVER, data=data, headers=headers)

    if response.status_code != 200:
        print('Failed to post job result:', response.text)
        return None

    result = response.json()
    return result['status']

while True:
    print(run())
