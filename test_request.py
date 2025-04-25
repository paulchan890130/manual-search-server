import requests

res = requests.post(
    "https://hanwoory.onrender.com/search",
    json={"question": "F-4 비자 연장 조건은?"},
    timeout=30
)

print(res.status_code)
print(res.json())
