# ===================== بيانات المتجر =====================

SHOP_CATEGORIES = {
    "🎮": {
        "name": "بطاقات الألعاب", 
        "products": [
            {"id": "psn_10", "name": "🎮 بطاقة PSN 10$", "points": 500, "balance": 0, "details": "كود رقمي - صالح لجميع المناطق"},
            {"id": "psn_20", "name": "🎮 بطاقة PSN 20$", "points": 950, "balance": 0, "details": "كود رقمي - خصم 50 نقطة"},
            {"id": "steam_5", "name": "🎮 بطاقة Steam 5$", "points": 250, "balance": 0, "details": "كود رقمي - يضاف إلى المحفظة"},
            {"id": "steam_10", "name": "🎮 بطاقة Steam 10$", "points": 480, "balance": 0, "details": "كود رقمي - خصم 20 نقطة"},
            {"id": "pubg_600", "name": "🎮 UC PUBG 600", "points": 300, "balance": 0, "details": "شحن مباشر إلى المعرف"},
            {"id": "freefire_100", "name": "🎮 دايموند FreeFire 100", "points": 150, "balance": 0, "details": "شحن سريع"},
        ]
    },
    "📱": {
        "name": "شحن موبايل", 
        "products": [
            {"id": "syriatel_5000", "name": "📱 شحن Syriatel 5000 ل.س", "points": 400, "balance": 5000, "details": "كود شحن فوري"},
            {"id": "syriatel_10000", "name": "📱 شحن Syriatel 10000 ل.س", "points": 750, "balance": 10000, "details": "كود شحن فوري - توفير 250 نقطة"},
            {"id": "mtn_5000", "name": "📱 شحن MTN 5000 ل.س", "points": 400, "balance": 5000, "details": "كود شحن فوري"},
            {"id": "mtn_10000", "name": "📱 شحن MTN 10000 ل.س", "points": 750, "balance": 10000, "details": "كود شحن فوري - توفير 250 نقطة"},
        ]
    },
    "⚡": {
        "name": "خدمات رقمية", 
        "products": [
            {"id": "vip_1m", "name": "⭐ عضوية VIP شهر", "points": 1000, "balance": 0, "details": "مميزات حصرية: خصم 10%، دعم أولوية، لوجو خاص"},
            {"id": "vip_3m", "name": "⭐ عضوية VIP 3 أشهر", "points": 2700, "balance": 0, "details": "توفير 300 نقطة + هدية مجانية"},
            {"id": "bot_service", "name": "🤖 تصميم بوت مخصص", "points": 5000, "balance": 0, "details": "نصمم لك بوت متكامل حسب طلبك"},
            {"id": "server_1m", "name": "🖥️ استضافة شهر", "points": 2000, "balance": 0, "details": "استضافة بوت 24/7"},
        ]
    },
    "🎁": {
        "name": "عروض خاصة", 
        "products": [
            {"id": "mystery_box", "name": "🎁 صندوق غامض", "points": 100, "balance": 0, "details": "تحصل على منتج عشوائي بقيمة 100-500 نقطة"},
            {"id": "ramadan_offer", "name": "🌙 عرض رمضان", "points": 500, "balance": 0, "details": "بطاقة Steam 5$ + شحن 5000 ل.س"},
        ]
    }
}

def get_all_products():
    """الحصول على جميع المنتجات"""
    products = []
    for cat in SHOP_CATEGORIES.values():
        products.extend(cat["products"])
    return products

def get_product(product_id):
    """الحصول على منتج معين بواسطة ID"""
    for p in get_all_products():
        if p["id"] == product_id:
            return p
    return None

def get_products_by_category(category_emoji):
    """الحصول على منتجات فئة معينة"""
    cat = SHOP_CATEGORIES.get(category_emoji)
    return cat["products"] if cat else []
