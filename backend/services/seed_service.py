from taxonomy.category import Category, SubCategory
from taxonomy.location import Location


def get_or_create_category(db, name, type_):
    obj = db.query(Category).filter_by(name=name).first()
    if obj:
        return obj

    obj = Category(name=name, type=type_)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_subcategories(db, category, items):
    for name in items:
        exists = db.query(SubCategory).filter_by(
            name=name,
            category_id=category.id
        ).first()

        if not exists:
            db.add(SubCategory(name=name, category_id=category.id))

    db.commit()


def create_location(db, name, level, parent=None):
    exists = db.query(Location).filter_by(name=name, parent_id=parent.id if parent else None).first()
    if exists:
        return exists

    loc = Location(name=name, level=level, parent_id=parent.id if parent else None)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc
