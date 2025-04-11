from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# 네이버 API 키 설정 (환경변수로 관리)
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

# 차종, 연료 매핑
def get_cartype_code(name):
    return {
        "승용차": 1,
        "중형승합/화물": 2,
        "대형차": 3,
        "3축 이상": 4,
        "4축 이상": 5,
        "경차": 6
    }.get(name, 1)

def get_fueltype_code(name):
    return {
        "휘발유": "gasoline",
        "고급휘발유": "highgradegasoline",
        "경유": "diesel",
        "LPG": "lpg"
    }.get(name, "gasoline")

# 주소 -> 좌표
def get_coordinates(address):
    url = f"https://maps.apigw.ntruss.com/map-geocode/v2/geocode?query={address}"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET
    }
    res = requests.get(url, headers=headers).json()
    if res.get("addresses"):
        x = res["addresses"][0]["x"]
        y = res["addresses"][0]["y"]
        return x, y
    else:
        return None, None

# 경로 요청
def get_route_info(start_coords, goal_coords, cartype, fueltype, mileage):
    url = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
    params = {
        "start": f"{start_coords[0]},{start_coords[1]}",
        "goal": f"{goal_coords[0]},{goal_coords[1]}",
        "option": "trafast",
        "cartype": cartype,
        "fueltype": fueltype,
        "mileage": mileage
    }
    headers = {
        "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
        "X-NCP-APIGW-API-KEY": CLIENT_SECRET
    }
    res = requests.get(url, headers=headers, params=params).json()
    try:
        s = res["route"]["trafast"][0]["summary"]
        return {
            "distance_km": round(s["distance"] / 1000, 2),
            "toll": s.get("tollFare", 0),
            "fuel": s.get("fuelPrice", 0),
            "total": s.get("tollFare", 0) + s.get("fuelPrice", 0)
        }
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        start = request.form.get("start")
        goal = request.form.get("goal")
        cartype = get_cartype_code(request.form.get("cartype"))
        fueltype = get_fueltype_code(request.form.get("fueltype"))
        mileage = float(request.form.get("mileage"))

        start_coords = get_coordinates(start)
        goal_coords = get_coordinates(goal)

        if None in (start_coords + goal_coords):
            result = {"error": "주소를 찾을 수 없습니다."}
        else:
            route_info = get_route_info(start_coords, goal_coords, cartype, fueltype, mileage)
            result = route_info if route_info else {"error": "경로 정보를 불러올 수 없습니다."}

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
