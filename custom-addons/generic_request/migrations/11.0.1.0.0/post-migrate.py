def migrate(cr, installed_version):
    cr.execute("""
        DROP TABLE IF EXISTS request_wizard_assign CASCADE;
        DELETE FROM ir_model WHERE model = 'request.wizard.assign';
    """)
