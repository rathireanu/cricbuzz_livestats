import requests

def get_live_matches():
    url = "https://cricbuzz-cricket2.p.rapidapi.com/matches/v1/live"
    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
        "X-RapidAPI-Host": "cricbuzz-cricket2.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"API Fetch Error: {e}")
        return None