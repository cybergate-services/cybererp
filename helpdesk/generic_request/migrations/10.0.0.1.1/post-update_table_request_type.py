def migrate(cr, version):
    cr.execute("""
    INSERT INTO request_type_category_rel
        (type_id, category_id)
    SELECT id,
           category_id
        FROM request_type AS RT
        WHERE NOT EXISTS
            (SELECT type_id, category_id
                FROM request_type_category_rel
                WHERE type_id = RT.id AND category_id = RT.category_id)
    """)
    cr.execute("""
        ALTER TABLE request_type DROP COLUMN category_id;
    """)
