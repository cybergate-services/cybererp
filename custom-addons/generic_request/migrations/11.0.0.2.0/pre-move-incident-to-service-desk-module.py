# -*- coding: utf-8 -*-

XMLIDS_TO_MIGRATE = (
    'request_type_incident',
    'request_stage_type_incident_draft',
    'request_stage_type_incident_new',
    'request_stage_type_incident_classification',
    'request_stage_type_incident_progress',
    'request_stage_type_incident_done',
    'request_stage_type_incident_rejected',
    'request_stage_route_type_incident_draft_to_new',
    'request_stage_route_type_incident_new_to_classification',
    'request_stage_route_type_incident_classification_to_rejected',
    'request_stage_route_type_incident_classification_to_progress',
    'request_stage_route_type_incident_progress_to_done',
)


def migrate(cr, version):
    cr.execute("""
        SELECT EXISTS (
            SELECT 1 FROM ir_module_module
            WHERE name = 'service_desk'
              AND state IN ('installed', 'to install', 'to upgrade')
        )
    """)
    is_service_desk_installed = cr.fetchone()[0]

    if is_service_desk_installed:
        cr.execute("""
            UPDATE ir_model_data
            SET module = 'service_desk'
            WHERE name IN %(xmlids)s
            AND module = 'generic_request'
        """, {'xmlids': XMLIDS_TO_MIGRATE})
