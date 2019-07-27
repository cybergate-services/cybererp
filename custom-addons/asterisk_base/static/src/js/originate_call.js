odoo.define('asterisk_base.originate_call_widget', function (require) {
  "use strict"

  var FieldChar = require('web.basic_fields').FieldChar;
  var fieldRegistry = require('web.field_registry');

  var OriginateCall = FieldChar.extend({

    _renderReadonly: function () {
      this._super();
      var self = this
      this.$el.append('&nbsp;<button type="button" class="btn btn-sm originate_call_button">\
                    <div class="fa fa-fw fa-phone o_button_icon"/><span/></button>')      
      this.$el.find('.originate_call_button').click(function(){
        return self._rpc({
            model: 'res.users',
            method: 'originate_call',
            args: [self.getSession().uid, self.value]
        })
      })
    },
  })
  fieldRegistry.add('originate_call', OriginateCall)
})
