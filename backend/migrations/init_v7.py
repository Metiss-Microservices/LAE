from database import (
    engine,
    Base
)

import models


# =========================================================
# CREATE ALL TABLES
# =========================================================

def create_tables():

    print(
        "\n🚀 LAE V7 migration started..."
    )

    Base.metadata.create_all(
        bind=engine
    )

    print(
        "✅ tables created"
    )


# =========================================================
# VERIFY MODELS
# =========================================================

def verify_models():

    tables = list(
        Base.metadata.tables.keys()
    )

    print(
        f"📦 detected {len(tables)} tables"
    )

    for table in sorted(tables):

        print(
            f"   • {table}"
        )


# =========================================================
# RUN
# =========================================================

def run():

    create_tables()

    verify_models()

    print(
        "\n✅ LAE V7 migration completed"
    )


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    run()