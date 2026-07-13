from database import (
    engine,
    Base,
    SessionLocal,
)

import models


def init_db():
    print("🧨 resetting database...")
    print("1")
    print("Drop start")

    for table in reversed(Base.metadata.sorted_tables):
        print("dropping:", table.name)
        table.drop(bind=engine, checkfirst=True)
        print("dropped:", table.name)

    print("Drop finished")
    # Base.metadata.drop_all(bind=engine)
    print("2")
    for table in Base.metadata.sorted_tables:
        print("creating:", table.name)
        table.create(bind=engine, checkfirst=True)
        print("done:", table.name)

    print("2.5")
    Base.metadata.create_all(bind=engine)
    print("3")
    db = SessionLocal()
    print("4")
    try:
        # demo clients
        clients = [
            models.Client(
                full_name="حسینی",
                phone="09123333333",
            ),
            models.Client(
                full_name="محمدی",
                phone="09124444444",
            ),
        ]

        db.add_all(clients)
        db.commit()

        print("✅ clients inserted")

        # demo suppliers
        suppliers = [
            models.Supplier(
                full_name="تامین کننده نمونه 1",
                phone="09125555555",
                password="1234",
                credit_balance=50,
                wallet_balance=1000000,
                score=4.5,
                wins=5,
                is_verified=True,
                is_active=True,
            ),
            models.Supplier(
                full_name="تامین کننده نمونه 2",
                phone="09126666666",
                password="1234",
                credit_balance=20,
                wallet_balance=500000,
                score=3.9,
                wins=2,
                is_verified=False,
                is_active=True,
            ),
        ]

        db.add_all(suppliers)
        db.commit()

        print("✅ suppliers inserted")
        print("✅ database initialized")

    except Exception as e:
        import traceback

        traceback.print_exc()
        db.rollback()
        print("❌ INIT ERROR:", repr(e))

    finally:
        db.close()


if __name__ == "__main__":
    init_db()