from datetime import date
from sqlalchemy.orm import Session
from app import models
from app.auth import hash_password


def init_db(db: Session):
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin = models.User(
            username="admin",
            password_hash=hash_password("village@2024"),
            role=models.UserRole.ADMIN,
            full_name="系统管理员",
            phone="13800000000"
        )
        db.add(admin)

    homestay_data = [
        {"name": "溪边小筑", "address": "浙江省杭州市临安区太湖源镇溪边村1号", "room_count": 5, "phone": "13800000001", "host_user": "host1"},
        {"name": "竹林雅舍", "address": "浙江省湖州市安吉县天荒坪镇竹林村8号", "room_count": 6, "phone": "13800000002", "host_user": "host2"},
        {"name": "茶香阁", "address": "浙江省杭州市西湖区龙坞镇茶村15号", "room_count": 4, "phone": "13800000003", "host_user": "host3"},
        {"name": "山涧居", "address": "浙江省衢州市开化县钱江源镇山涧村3号", "room_count": 7, "phone": "13800000004", "host_user": "host4"},
        {"name": "花海民宿", "address": "浙江省台州市仙居县横溪镇花海村22号", "room_count": 3, "phone": "13800000005", "host_user": "host5"},
        {"name": "古村人家", "address": "浙江省金华市武义县俞源乡古村9号", "room_count": 8, "phone": "13800000006", "host_user": "host6"},
    ]

    room_templates = [
        ("清风阁", models.RoomType.KING, 28, 198, 2),
        ("明月轩", models.RoomType.TWIN, 32, 228, 2),
        ("山景套房", models.RoomType.FAMILY, 45, 398, 4),
        ("竹林雅居", models.RoomType.DELUXE, 35, 298, 2),
        ("溪畔大床房", models.RoomType.KING, 26, 168, 2),
        ("家庭亲子房", models.RoomType.FAMILY, 50, 458, 5),
        ("豪华套房", models.RoomType.SUITE, 55, 598, 3),
        ("标准双床房", models.RoomType.TWIN, 28, 188, 2),
    ]

    homestays = []
    for i, hs_data in enumerate(homestay_data):
        host = db.query(models.User).filter(models.User.username == hs_data["host_user"]).first()
        if not host:
            host = models.User(
                username=hs_data["host_user"],
                password_hash=hash_password("h123"),
                role=models.UserRole.HOST,
                full_name=hs_data["name"] + "民宿主",
                phone=hs_data["phone"]
            )
            db.add(host)
            db.flush()

        homestay = db.query(models.Homestay).filter(models.Homestay.name == hs_data["name"]).first()
        if not homestay:
            homestay = models.Homestay(
                name=hs_data["name"],
                address=hs_data["address"],
                room_count=hs_data["room_count"],
                contact_phone=hs_data["phone"],
                description=f"{hs_data['name']}是一家精品乡村民宿，环境优美，服务周到。",
                host_id=host.id
            )
            db.add(homestay)
            db.flush()

            room_count = hs_data["room_count"]
            for j in range(room_count):
                template_idx = j % len(room_templates)
                template = room_templates[template_idx]
                room_name = f"{template[0]}{j+1:02d}号" if j > 0 else template[0]
                room = models.Room(
                    name=room_name,
                    room_type=template[1],
                    area=template[2] + (j * 2),
                    base_price=template[3] + (j * 20),
                    max_guests=template[4],
                    homestay_id=homestay.id
                )
                db.add(room)
        homestays.append(homestay)

    holidays_2024 = [
        ("2024-01-01", "元旦"),
        ("2024-02-10", "春节"),
        ("2024-02-11", "春节"),
        ("2024-02-12", "春节"),
        ("2024-02-13", "春节"),
        ("2024-02-14", "春节"),
        ("2024-02-15", "春节"),
        ("2024-02-16", "春节"),
        ("2024-02-17", "春节"),
        ("2024-04-04", "清明节"),
        ("2024-04-05", "清明节"),
        ("2024-04-06", "清明节"),
        ("2024-05-01", "劳动节"),
        ("2024-05-02", "劳动节"),
        ("2024-05-03", "劳动节"),
        ("2024-05-04", "劳动节"),
        ("2024-05-05", "劳动节"),
        ("2024-06-10", "端午节"),
        ("2024-09-15", "中秋节"),
        ("2024-09-16", "中秋节"),
        ("2024-09-17", "中秋节"),
        ("2024-10-01", "国庆节"),
        ("2024-10-02", "国庆节"),
        ("2024-10-03", "国庆节"),
        ("2024-10-04", "国庆节"),
        ("2024-10-05", "国庆节"),
        ("2024-10-06", "国庆节"),
        ("2024-10-07", "国庆节"),
    ]
    holidays_2025 = [
        ("2025-01-01", "元旦"),
        ("2025-01-28", "春节"),
        ("2025-01-29", "春节"),
        ("2025-01-30", "春节"),
        ("2025-01-31", "春节"),
        ("2025-02-01", "春节"),
        ("2025-02-02", "春节"),
        ("2025-02-03", "春节"),
        ("2025-02-04", "春节"),
        ("2025-04-04", "清明节"),
        ("2025-04-05", "清明节"),
        ("2025-04-06", "清明节"),
        ("2025-05-01", "劳动节"),
        ("2025-05-02", "劳动节"),
        ("2025-05-03", "劳动节"),
        ("2025-05-04", "劳动节"),
        ("2025-05-05", "劳动节"),
        ("2025-05-31", "端午节"),
        ("2025-06-01", "端午节"),
        ("2025-06-02", "端午节"),
        ("2025-10-01", "国庆节"),
        ("2025-10-02", "国庆节"),
        ("2025-10-03", "国庆节"),
        ("2025-10-04", "国庆节"),
        ("2025-10-05", "国庆节"),
        ("2025-10-06", "国庆节"),
        ("2025-10-07", "国庆节"),
        ("2025-10-06", "中秋节"),
    ]
    holidays_2026 = [
        ("2026-01-01", "元旦"),
        ("2026-02-16", "春节"),
        ("2026-02-17", "春节"),
        ("2026-02-18", "春节"),
        ("2026-02-19", "春节"),
        ("2026-02-20", "春节"),
        ("2026-02-21", "春节"),
        ("2026-02-22", "春节"),
        ("2026-02-23", "春节"),
        ("2026-04-04", "清明节"),
        ("2026-04-05", "清明节"),
        ("2026-04-06", "清明节"),
        ("2026-05-01", "劳动节"),
        ("2026-05-02", "劳动节"),
        ("2026-05-03", "劳动节"),
        ("2026-05-04", "劳动节"),
        ("2026-05-05", "劳动节"),
        ("2026-06-19", "端午节"),
        ("2026-06-20", "端午节"),
        ("2026-06-21", "端午节"),
        ("2026-09-25", "中秋节"),
        ("2026-09-26", "中秋节"),
        ("2026-09-27", "中秋节"),
        ("2026-10-01", "国庆节"),
        ("2026-10-02", "国庆节"),
        ("2026-10-03", "国庆节"),
        ("2026-10-04", "国庆节"),
        ("2026-10-05", "国庆节"),
        ("2026-10-06", "国庆节"),
        ("2026-10-07", "国庆节"),
    ]

    all_holidays = holidays_2024 + holidays_2025 + holidays_2026
    holiday_map = {}
    for date_str, name in all_holidays:
        if date_str not in holiday_map:
            holiday_map[date_str] = name
    
    for date_str, name in holiday_map.items():
        d = date.fromisoformat(date_str)
        existing = db.query(models.Holiday).filter(models.Holiday.date == d).first()
        if not existing:
            db.add(models.Holiday(date=d, name=name))

    db.commit()
