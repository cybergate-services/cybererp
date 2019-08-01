odoo.define('generic_request_dashboard', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var Dashboard = require('web_settings_dashboard');

    var DashboardBureaucrat = Widget.extend({
        template: 'DashboardBureaucrat',
    });

    Dashboard.Dashboard.include({
        template: 'DashboardMain_generic_request',

        init: function () {
            this._super.apply(this, arguments);
            this.all_dashboards.push('bureaucrat');
        },

        load_bureaucrat: function () {
            return new DashboardBureaucrat(this).replace(
                this.$('.o_web_settings_dashboard_bureaucrat'));
        },
    });


    return {
        Dashboard: Dashboard.Dashboard,
        DashboardBureaucrat: DashboardBureaucrat,
    };

});
