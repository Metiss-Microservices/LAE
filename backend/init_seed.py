from database import SessionLocal

import models

from datetime import datetime

from uuid import uuid4

import random


db = SessionLocal()


# =========================================================
# SERVICES
# =========================================================

services = {

    "تعمیرات لوازم خانگی": [

        "تعمیر کولر گازی",
        "تعمیر کولر آبی",
        "تعمیر یخچال",
        "تعمیر ماشین لباسشویی",
        "تعمیر ماشین ظرفشویی",
        "تعمیر مایکروفر",
        "تعمیر جاروبرقی",
        "تعمیر بخاری"
    ],

    "خدمات خودرو": [

        "مکانیکی سیار",
        "تعویض روغن",
        "جلوبندی سازی",
        "برق خودرو",
        "باطری سازی",
        "صافکاری و نقاشی",
        "کارواش در محل",
        "امداد خودرو",
        "نصب دزدگیر و ردیاب"
    ],

    "زیبایی و آرایش": [

        "آرایشگری زنانه",
        "آرایشگری مردانه",
        "رنگ و مش",
        "کاشت ناخن",
        "اکستنشن مو",
        "اصلاح صورت",
        "پاکسازی پوست",
        "ماساژ زیبایی"
    ],

    "ورزش و سلامت": [

        "مربی بدنسازی",
        "برنامه غذایی",
        "یوگا",
        "پیلاتس",
        "ماساژ درمانی",
        "فیزیوتراپی",
        "تمرین در منزل"
    ],

    "انجام امور اداری": [

        "ترجمه رسمی",
        "ترجمه غیر رسمی",
        "پر کردن فرم سفارت",
        "رزرو وقت سفارت",
        "ثبت شرکت",
        "امور مالیاتی",
        "بیمه تامین اجتماعی",
        "مشاوره حقوقی"
    ],

    "نظافت و خدمات منزل": [

        "نظافت منزل",
        "نظافت اداری",
        "نظافت راه‌پله",
        "نظافت پس از اسباب‌کشی",
        "شستشوی فرش",
        "مبل شویی",
        "شیشه شویی"
    ],

    "ساختمان و بازسازی": [

        "نقاشی ساختمان",
        "کاغذ دیواری",
        "کاشی کاری",
        "گچ کاری",
        "بنایی",
        "بازسازی کامل"
    ],

    "تاسیسات و برق": [

        "لوله کشی",
        "رفع نشتی",
        "نصب پمپ آب",
        "برقکاری ساختمان",
        "نصب دوربین مداربسته"
    ],

    "حمل و نقل": [

        "اسباب کشی",
        "وانت بار",
        "باربری بین شهری"
    ],

    "سلامت در منزل": [

        "پرستار سالمند",
        "پرستار کودک",
        "فیزیوتراپی",
        "تزریقات در منزل"
    ]
}


# =========================================================
# GOODS
# =========================================================

goods = {

    "خانه و آشپزخانه": [

        "یخچال",
        "اجاق گاز",
        "ماشین لباسشویی",
        "ماشین ظرفشویی",
        "مایکروفر",
        "جاروبرقی"
    ],

    "آرایشی و بهداشتی": [

        "کرم صورت",
        "لوازم آرایشی",
        "عطر و ادکلن",
        "شامپو",
        "محصولات پوستی",
        "ضد آفتاب"
    ],

    "ورزش و مکمل": [

        "پروتئین وی",
        "کراتین",
        "مکمل بدنسازی",
        "لباس ورزشی",
        "کفش ورزشی",
        "تجهیزات بدنسازی"
    ],

    "ابزار و تجهیزات": [

        "دریل",
        "پیچ گوشتی",
        "فرز",
        "کمپرسور",
        "اره برقی",
        "ابزار دستی"
    ],

    "کالای دیجیتال": [

        "موبایل",
        "لپ‌تاپ",
        "تبلت",
        "ساعت هوشمند",
        "هدفون",
        "اسپیکر",
        "پاوربانک",
        "کنسول بازی"
    ],

    "مد و پوشاک": [

        "لباس مردانه",
        "لباس زنانه",
        "کفش",
        "کیف",
        "اکسسوری"
    ],

    "خودرو و موتورسیکلت": [

        "لوازم یدکی خودرو",
        "روغن موتور",
        "لاستیک",
        "باتری خودرو"
    ]
}


# =========================================================
# LOCATIONS
# =========================================================

provinces = [

    "تهران",
    "البرز",
    "اصفهان",
    "خراسان رضوی",
    "فارس",
    "آذربایجان شرقی",
    "مازندران",
    "گیلان"
]

cities = {

    "تهران": ["تهران"],

    "البرز": ["کرج"],

    "اصفهان": ["اصفهان"],

    "خراسان رضوی": ["مشهد"],

    "فارس": ["شیراز"],

    "آذربایجان شرقی": ["تبریز"],

    "مازندران": ["ساری"],

    "گیلان": ["رشت"]
}

tehran_districts = [

    "سعادت آباد",
    "پونک",
    "جنت آباد",
    "شهرک غرب",
    "مرزداران",
    "ستارخان",
    "ونک",
    "پاسداران",
    "نیاوران",
    "تهرانپارس",
    "نارمک",
    "انقلاب"
]


# =========================================================
# HELPERS
# =========================================================

def create_location(
    name,
    type_,
    parent=None
):

    loc = db.query(
        models.Location
    ).filter_by(

        name=name,
        type=type_

    ).first()

    if loc:
        return loc

    loc = models.Location(

        id=uuid4(),

        name=name,

        type=type_,

        parent_id=(
            parent.id
            if parent
            else None
        )
    )

    db.add(loc)

    db.commit()

    db.refresh(loc)

    return loc


def create_category(
    name,
    type_
):

    row = db.query(
        models.Category
    ).filter_by(

        name=name,
        type=type_

    ).first()

    if row:
        return row

    row = models.Category(

        id=uuid4(),

        name=name,

        type=type_
    )

    db.add(row)

    db.commit()

    db.refresh(row)

    return row


def create_subcategory(
    name,
    category_id
):

    row = db.query(
        models.SubCategory
    ).filter_by(

        name=name,

        category_id=category_id

    ).first()

    if row:
        return row

    row = models.SubCategory(

        id=uuid4(),

        name=name,

        category_id=category_id
    )

    db.add(row)

    db.commit()

    db.refresh(row)

    return row


# =========================================================
# MASTER DATA
# =========================================================

def seed_master():

    print("🌱 seeding master data...")

    iran = create_location(
        "ایران",
        "country"
    )

    province_objs = {}

    city_objs = {}

    districts = []

    # -----------------------------------------------------
    # provinces + cities
    # -----------------------------------------------------

    for province_name in provinces:

        province = create_location(

            province_name,

            "province",

            iran
        )

        province_objs[
            province_name
        ] = province

        for city_name in cities[province_name]:

            city = create_location(

                city_name,

                "city",

                province
            )

            city_objs[
                city_name
            ] = city

    # -----------------------------------------------------
    # tehran districts
    # -----------------------------------------------------

    tehran_city = city_objs["تهران"]

    for district_name in tehran_districts:

        district = create_location(

            district_name,

            "district",

            tehran_city
        )

        districts.append(district)

    # -----------------------------------------------------
    # categories + subcategories
    # -----------------------------------------------------

    sub_map = {}

    # services

    for category_name, subs in services.items():

        category = create_category(

            category_name,

            "service"
        )

        sub_map[category_name] = []

        for sub_name in subs:

            sub = create_subcategory(

                sub_name,

                category.id
            )

            sub_map[
                category_name
            ].append(sub)

    # products

    for category_name, subs in goods.items():

        category = create_category(

            category_name,

            "product"
        )

        sub_map[category_name] = []

        for sub_name in subs:

            sub = create_subcategory(

                sub_name,

                category.id
            )

            sub_map[
                category_name
            ].append(sub)

    print("✅ master data ready")

    return (

        sub_map,

        districts,

        list(city_objs.values())
    )


# =========================================================
# SUPPLIERS
# =========================================================

def seed_suppliers(
    sub_map,
    districts,
    cities_list,
):
    print("👷 seeding suppliers...")

    all_locations = districts + cities_list

    identities = []
    suppliers = []
    supplier_categories = []
    supplier_subcategories = []

    for i in range(50):
        category_name = random.choice(
            list(sub_map.keys())
        )

        sub = random.choice(
            sub_map[category_name]
        )

        location = random.choice(
            all_locations
        )

        phone = f"0912{i:08}"

        identity = models.UserIdentity(
            id=uuid4(),
            phone=phone,
        )

        supplier = models.Supplier(
            id=uuid4(),
            identity_id=identity.id,
            full_name=f"تأمین‌کننده {i}",
            phone=phone,
            password="1234",
            location_id=location.id,
            credit_balance=100,
            wallet_balance=500000,
            score=round(
                random.uniform(3, 5),
                2,
            ),
            wins=random.randint(
                0,
                20,
            ),
            rating_count=random.randint(
                5,
                50,
            ),
            completed_jobs=random.randint(
                5,
                50,
            ),
            cancelled_jobs=random.randint(
                0,
                5,
            ),
            response_speed=random.randint(
                30,
                120,
            ),
            is_verified=random.choice(
                [True, False]
            ),
            is_active=True,
            is_blocked=False,
        )

        identities.append(identity)
        suppliers.append(supplier)

        supplier_categories.append(
            models.SupplierCategory(
                supplier_id=supplier.id,
                category_id=sub.category_id,
            )
        )

        supplier_subcategories.append(
            models.SupplierSubCategory(
                supplier_id=supplier.id,
                subcategory_id=sub.id,
            )
        )

    db.add_all(identities)
    db.flush()

    db.add_all(suppliers)
    db.flush()

    db.add_all(supplier_categories)
    db.add_all(supplier_subcategories)

    db.commit()

    print(
        f"✅ {len(suppliers)} suppliers inserted"
    )

# =========================================================
# LEADS
# =========================================================

def seed_leads(
    sub_map,
    districts,
    cities_list
):

    print("🔥 seeding leads...")

    clients = db.query(
        models.Client
    ).all()

    if not clients:

        print("❌ no clients found")

        return

    leads = []

    all_locations = (
        districts +
        cities_list
    )

    for _, subs in sub_map.items():

        for sub in subs:

            for _ in range(2):

                location = random.choice(
                    all_locations
                )

                client = random.choice(
                    clients
                )

                lead = models.Lead(

                    id=uuid4(),

                    category_id=
                        sub.category_id,

                    subcategory_id=
                        sub.id,

                    location_id=
                        location.id,

                    problem=
                        f"درخواست برای {sub.name}",

                    client_id=
                        client.id,

                    created_at=
                        datetime.utcnow()
                )

                leads.append(lead)

    db.add_all(leads)

    db.commit()

    print(
        f"✅ {len(leads)} leads inserted"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:

        print("🚀 init seed started")

        sub_map, districts, cities_list = seed_master()

        seed_suppliers(
            sub_map,
            districts,
            cities_list
        )

        seed_leads(
            sub_map,
            districts,
            cities_list
        )

        print("🎉 seed completed")

    except Exception as e:

        db.rollback()

        print(
            "❌ seed error:",
            e
        )

    finally:

        db.close()

        print("🔒 database closed")