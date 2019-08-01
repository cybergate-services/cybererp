def migrate(cr, installed_version):
    cr.execute("""
        UPDATE ir_model_data
        SET module = 'generic_request'
        WHERE module = 'generic_request_stage_type'
          AND name IN (
            'request_stage_type_draft',
            'request_stage_type_sent',
            'request_stage_type_cancel',
            'request_stage_type_closed_ok',
            'request_stage_type_closed_fail',
            'request_stage_type_pause',
            'model_request_stage_type');

        UPDATE ir_model_constraint
        SET module = (
               SELECT id FROM ir_module_module
               WHERE name = 'generic_request')
        WHERE module IN (
               SELECT id FROM ir_module_module
               WHERE name IN (
                'generic_request_stage_type',
                'generic_request_stage_type_sla')
        );

        UPDATE ir_model_data
        SET module = 'generic_request'
        WHERE module = 'generic_request_stage_type'
          AND model IN (
                 'ir.model.fields',
                 'ir.model.constraint',
                 'ir.model.relation',
                 'ir.ui.menu',
                 'ir.model.access',
                 'ir.actions.act_window');

        -- Migrate generic_request_sla_log related
        UPDATE ir_model_data
        SET module = 'generic_request_sla_log'
        WHERE module = 'generic_request_stage_type_sla'
          AND name = 'field_request_sla_log_stage_type_id';

        -- Delete views
        DELETE FROM ir_ui_view WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE model = 'ir.ui.view'
              AND module IN (
                    'generic_request_stage_type_sla',
                    'generic_request_stage_type')
        );

        -- DELETE references to ir_model
        DELETE FROM ir_model_data
        WHERE model = 'ir.model'
          AND module IN (
                'generic_request_stage_type_sla',
                'generic_request_stage_type');

        -- DELETE removed modules from database
        DELETE FROM ir_module_module WHERE name IN (
                'generic_request_stage_type_sla',
                'generic_request_stage_type');
    """)
