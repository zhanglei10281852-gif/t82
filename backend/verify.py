import urllib.request
import urllib.parse
import json
import sys

base = 'http://localhost:8791/api'

def api_post(url, data=None, headers=None, is_form=False):
    if is_form and data:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    else:
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def api_put(url, data=None, headers=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method='PUT')
    req.add_header('Content-Type', 'application/json')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def api_get(url, headers=None):
    req = urllib.request.Request(url, method='GET')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

print('=== 1. 管理员登录 ===')
code, result = api_post(f'{base}/auth/login', 
    {'username': 'admin', 'password': 'village@2024'}, is_form=True)
print(f'Status: {code}')
if code == 200:
    admin_token = result['access_token']
    print(f'Admin token 长度: {len(admin_token)}')
else:
    print(f'Error: {result}')
    sys.exit(1)

admin_headers = {'Authorization': f'Bearer {admin_token}'}

print('\n=== 2. 民宿列表 ===')
code, homestays = api_get(f'{base}/homestays', admin_headers)
print(f'Status: {code}, 数量: {len(homestays)}')
for h in homestays:
    print(f'  - {h["name"]} | {h["room_count"]}间房 | 民宿主: {h["host_name"]}')

print('\n=== 3. 房间总数 ===')
code, rooms = api_get(f'{base}/rooms', admin_headers)
print(f'Status: {code}, 总房间数: {len(rooms)}')
for r in rooms[:3]:
    print(f'  - {r["name"]} ({r["room_type"]}) ¥{r["base_price"]}/晚')

print('\n=== 4. 节假日数量 ===')
code, holidays = api_get(f'{base}/holidays', admin_headers)
print(f'Status: {code}, 节假日总数: {len(holidays)}')

print('\n=== 5. 民宿主登录 ===')
code, result = api_post(f'{base}/auth/login',
    {'username': 'host1', 'password': 'h123'}, is_form=True)
print(f'host1 登录状态: {code}')
if code == 200:
    host_token = result['access_token']
    print(f'Host token 长度: {len(host_token)}')

print('\n=== 6. 房态日历 ===')
if homestays:
    hs_id = homestays[0]['id']
    code, cal = api_get(f'{base}/calendar/homestay/{hs_id}?year=2026&month=6', admin_headers)
    print(f'Status: {code}')
    if code == 200:
        print(f'  民宿: {cal["homestay_name"]}')
        print(f'  房间数: {len(cal["rooms"])}')
        if cal['rooms']:
            print(f'  当月天数: {len(cal["rooms"][0]["days"])}')

print('\n=== 7. 创建预订测试 ===')
if rooms:
    room = rooms[0]
    print(f'测试房间: {room["name"]} (ID: {room["id"]})')
    
    import datetime
    check_in = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    check_out = (datetime.date.today() + datetime.timedelta(days=33)).isoformat()
    
    code, price_info = api_post(f'{base}/bookings/calculate-price', {
        'room_id': room['id'],
        'check_in_date': check_in,
        'check_out_date': check_out
    }, admin_headers)
    print(f'价格计算状态: {code}')
    if code == 200:
        print(f'  总价: ¥{price_info["total_price"]}')
        print(f'  晚数: {price_info["nights"]}')
        print(f'  折扣: {price_info["discount"]}')
    
    code, booking = api_post(f'{base}/bookings', {
        'guest_name': '测试客人',
        'guest_phone': '13800000000',
        'check_in_date': check_in,
        'check_out_date': check_out,
        'room_id': room['id'],
        'guest_count': 2,
        'special_requests': 'API测试预订'
    }, admin_headers)
    print(f'创建预订状态: {code}')
    if code == 200:
        print(f'  预订ID: {booking["id"]}')
        print(f'  状态: {booking["status"]}')
        print(f'  总价: ¥{booking["total_price"]}')
        
        booking_id = booking['id']
        
        code, _ = api_put(f'{base}/bookings/{booking_id}/status', 
            {'status': 'confirmed'}, admin_headers)
        print(f'确认预订: {code}')
        
        code, _ = api_put(f'{base}/bookings/{booking_id}/status',
            {'status': 'checked_in'}, admin_headers)
        print(f'办理入住: {code}')
        
        code, _ = api_put(f'{base}/bookings/{booking_id}/status',
            {'status': 'checked_out'}, admin_headers)
        print(f'办理退房: {code}')

print('\n=== 所有测试完成 ===')
