  odoo.define("asterisk_base.tree_buttons", function (require) {
  "use strict";

  var session = require('web.session');
  var ListView = require('web.ListView');
  var ListController = require('web.ListController');
  
  var AstBaseListController = ListController.include({
    
    renderButtons: function($node) {
        this._super.apply(this, arguments)
        if (this.$buttons) {
          let apply_btn = this.$buttons.find('.o_apply_changes');
          apply_btn && apply_btn.click(this.proxy('apply_changes'));
          let bans_btn = this.$buttons.find('.o_reload_access_bans');
          bans_btn && bans_btn.click(this.proxy('reload_access_bans'));
        }
    },

    apply_changes: function () {
      var self = this;
      this._rpc({
        model: 'asterisk.conf',
        method: 'apply_all_changes'
      }).then(function (){
        if (self.modelName == "asterisk.conf") {
            console.log('reload')
            self.trigger_up('reload')
        }
      })
    },

    reload_access_bans: function() {        
      var self = this;
      console.log(self)
      this._rpc({
        model: 'asterisk.access_ban',
        method: 'reload_bans'
      }).then(function (){
        if (self.modelName == "asterisk.access_ban") {
            console.log('reload')
            self.trigger_up('reload');
        }
      })
    },
  
  });

});



