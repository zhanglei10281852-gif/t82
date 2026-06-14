import requests

base_url = 'http://localhost:8791/api'

r = requests.post(f'{base_url}/auth/login',
    data={'username': 'admin', 'password': 'village@2024'})
print('Login status:', r.status_code)
token = r.json()['access_token']
print('Token obtained, length:', len(token))

headers = {'Authorization': f'Bearer {token}'}

r = requests.get(f'{base_url}/homestays', headers=headers)
print('Homestays status:', r.status_code)
homestays = r.json()
print(f'Homestays count: {len(homestays)}')
for h in homestays:
    print(f'  - {h["name"]} ({h["room_count"]} rooms, host: {h["host_name"]})')

r = requests.get(f'{base_url}/rooms', headers=headers)
print(f'\nRooms count: {len(r.json())}')

r = requests.get(f'{base_url}/holidays', headers=headers)
print(f'Holidays count: {len(r.json())}')

r = requests.get(f'{base_url}/stats/dashboard?year=2026&month=6', headers=headers)
print(f'\nDashboard stats status: {r.status_code}')
if r.status_code == 200:
    stats = r.json()
    print(f'  Total revenue: {stats["total_revenue"]}')
    print(f'  Total bookings: {stats["total_bookings"]}')
    print(f'  Occupancy rate: {stats["occupancy_rate"]}%')

r = requests.get(f'{base_url}/calendar/homestay/1?year=2026&month=6', headers=headers)
print(f'\nCalendar status: {r.status_code}')
if r.status_code == 200:
    cal = r.json()
    print(f'  Homestay: {cal["homestay_name"]}')
    print(f'  Rooms in calendar: {len(cal["rooms"])}')
    if cal["rooms"]:
        print(f'  Days per room: {len(cal["rooms"][0]["days"])}')

print('\n=== Test booking creation ===')
r = requests.get(f'{base_url}/rooms', headers=headers)
rooms = r.json()
if rooms:
    room = rooms[0]
    print(f'Testing with room: {room["name"]} (ID: {room["id"]})')
    
    import datetime
    check_in = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    check_out = (datetime.date.today() + datetime.timedelta(days=32)).isoformat()
    
    r = requests.post(f'{base_url}/bookings/calculate-price', headers=headers, json={
        'room_id': room['id'],
        'check_in_date': check_in,
        'check_out_date': check_out
    })
    print(f'Price calc status: {r.status_code}')
    if r.status_code == 200:
        price = r.json()
        print(f'  Total price: {price["total_price"]}')
        print(f'  Nights: {price["nights"]}')
        print(f'  Discount: {price["discount"]}')
    
    r = requests.post(f'{base_url}/bookings', headers=headers, json={
        'guest_name': '测试客人',
        'guest_phone': '13800000000',
        'check_in_date': check_in,
        'check_out_date': check_out,
        'room_id': room['id'],
        'guest_count': 2,
        'special_requests': '测试预订'
    })
    print(f'Booking create status: {r.status_code}')
    if r.status_code == 200:
        booking = r.json()
        print(f'  Booking ID: {booking["id"]}')
        print(f'  Status: {booking["status"]}')
        print(f'  Total price: {booking["total_price"]}')
        
        r = requests.put(f'{base_url}/bookings/{booking["id"]}/status', headers=headers, json={
            'status': 'confirmed'
        })
        print(f'Confirm status: {r.status_code}')
        
        r = requests.put(f'{base_url}/bookings/{booking["id"]}/status', headers=headers, json={
            'status': 'checked_in'
        })
        print(f'Check in status: {r.status_code}')
        
        r = requests.put(f'{base_url}/bookings/{booking["id"]}/status', headers=headers, json={
            'status': 'checked_out'
        })
        print(f'Check out status: {r.status_code}')

print('\n=== All tests completed ===')
