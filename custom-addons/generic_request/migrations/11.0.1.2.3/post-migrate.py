def migrate(cr, installed_version):
    cr.execute("""
        UPDATE request_type
        SET color = 'rgba('||
            ('x'||substr(color,2,2))::bit(8)::int||','||
            ('x'||substr(color,4,2))::bit(8)::int||','||
            ('x'||substr(color,6,2))::bit(8)::int||',1)'
        WHERE color NOT LIKE 'rgba%';

        UPDATE request_stage
        SET bg_color = 'rgba('||
            ('x'||substr(bg_color,2,2))::bit(8)::int||','||
            ('x'||substr(bg_color,4,2))::bit(8)::int||','||
            ('x'||substr(bg_color,6,2))::bit(8)::int||',1)'
        WHERE bg_color NOT LIKE 'rgba%';

        UPDATE request_stage
        SET label_color = 'rgba('||
            ('x'||substr(label_color,2,2))::bit(8)::int||','||
            ('x'||substr(label_color,4,2))::bit(8)::int||','||
            ('x'||substr(label_color,6,2))::bit(8)::int||',1)'
        WHERE label_color NOT LIKE 'rgba%';
    """)
