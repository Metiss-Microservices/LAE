from database import (

    engine,
    Base,
    SessionLocal
)

import models


def init_db():

    print("🧨 resetting database...")

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )

    db = SessionLocal()

    try:

        # -----------------------------------
        # demo clients
        # -----------------------------------

        clients = [

            models.Client(
                full_name="حسینی",
                phone="09123333333"
            ),

            models.Client(
                full_name="محمدی",
                phone="09124444444"
            )
        ]

        db.add_all(clients)

        db.commit()

        print("✅ clients inserted")

        # -----------------------------------
        # demo suppliers
        # -----------------------------------

        suppliers = [

            models.Supplier(
                full_name="تامین کننده نمونه 1",
                phone="09125555555",
                password="1234",
                credit_balance=50,
                wallet_balance=1000000,
                score=4.5,
                wins=5,
                total_jobs=10,
                reputation_score=85,
                success_rate=90,
                is_verified=True,
                is_active=True
            ),

            models.Supplier(
                full_name="تامین کننده نمونه 2",
                phone="09126666666",
                password="1234",
                credit_balance=20,
                wallet_balance=500000,
                score=3.9,
                wins=2,
                total_jobs=6,
                reputation_score=70,
                success_rate=75,
                is_verified=False,
                is_active=True
            )
        ]

        db.add_all(suppliers)

        db.commit()

        print("✅ suppliers inserted")

        print("✅ database initialized")

    except Exception as e:

        db.rollback()

        print(
            "❌ INIT ERROR:",
            e
        )

    finally:

        db.close()


if __name__ == "__main__":

    init_db()