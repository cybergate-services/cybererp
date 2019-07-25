def migrate(cr, installed_version):
    cr.execute("""
        UPDATE ir_model_data
        SET module = 'generic_request_assignment'
        WHERE module = 'generic_request'
          AND name IN (
               'request_assign_policy_model_ir_model',
               'request_assign_policy_model');
    """)
