/**
 * Created by colin on 27/01/15.
 */

openerp.nh_etake_list_theme = function(instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var kiosk_mode = false;
    var initKanban = false;

    instance.web.Menu.include({
        open_menu: function(id){
            var self = this;
            this.current_menu = id;
            this.session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
                $('.oe_secondary_menu_section').removeClass('active');
                if(typeof($sub_menu.children('ul').attr('data-tab-id')) !== 'undefined'){
                    $('.oe_secondary_menu_section[data-tab-id='+$sub_menu.children('ul').attr('data-tab-id')+']').addClass('active');
                }
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
                $('.oe_secondary_menu_section').removeClass('active');
                $('.oe_secondary_menu_section[data-tab-id='+$sub_menu.attr('data-tab-id')+']').addClass('active');
            }



            // Activate current main menu
            this.$el.find('.active').removeClass('active');
            $main_menu.parent().addClass('active');


            // Show current sub menu
            this.$secondary_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Hide/Show the leftbar menu depending of the presence of sub-items
            if (! kiosk_mode){
                this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);
            }

            // Activate current menu item and show parents
            if($clicked_menu.parents('.oe_user_menu_placeholder').length < 1){
                this.$secondary_menus.find('.active').not('.oe_secondary_menu_section').removeClass('active');
            }


            if ($main_menu !== $clicked_menu) {
                if (! kiosk_mode){
                    $clicked_menu.parents().show();
                }
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    $clicked_menu.parent().addClass('active');
                }
            }
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'destroy');
            });

            //var activeMenu = $('.oe_secondary_menu').not(':hidden');
            var sectionTitles = $sub_menu.find('.oe_secondary_menu_section');
            var sectionLists = $sub_menu.find('.oe_secondary_submenu');
            var navbarDiv = $('<div class="navbar"></div>');


            if($main_menu.parent().css('display') == "none"){
//                if($('.oe_secondary_menu .oe_user_menu_placeholder').length < 1){
//                    userMenu.clone(true).appendTo(navbarDiv);
//                    //userMenu.hide();
//                }
               $('#oe_main_menu_navbar').hide();
                if($("#oe_main_menu_navbar").css('display') == "none"){
                    $(".openerp.openerp_webclient_container").css('height', '100%');
                }
            }
            if($sub_menu.find('.navbar').length < 1){
                $sub_menu.prepend(navbarDiv);
            }else{
                $sub_menu.find('.navbar').remove();
                $sub_menu.prepend(navbarDiv);

            }
            sectionTitles.each(function(index){
                // set the tab id on the section header
                $(this).attr('data-tab-id', index);

                // set the tab id on the list itself
                $(this).next('ul').attr('data-tab-id', index);

                // show / hide the list based on if it is currently 'active' or not

                if($(this).next('ul').children('.active').length > 0){
                    $(this).addClass('active');
                    $(this).next('ul').show();
                }else{
                    $(this).next('ul').hide();
                }

                //userMenu.show();

                // set up events to 'switch tabs'
                $(this).on('click', function(){
                    var tabId = $(this).attr('data-tab-id');
                    $(this).addClass('active');
                    sectionLists.each(function(index){
                        if($(this).attr('data-tab-id') == tabId){
                            $(this).show();
                        }else{
                            $(this).hide();
                        }
                    });
                });

                navbarDiv.append($(this));
//                if(navbarDiv.find('.oe_user_menu_placeholder').length < 1){
//                    userMenu = $('.oe_user_menu_placeholder').first();
//                    userMenu.clone(true).appendTo(navbarDiv);
//                    //userMenu.hide();
//
//                }
            });

            var userMenu = $('<ul class="oe_user_menu_placeholder"></ul>');
            self.user_menu = new instance.web.UserMenu(instance.webclient);
            self.user_menu.appendTo(userMenu);
            userMenu.appendTo(navbarDiv);
            self.user_menu.on('user_logout', self, instance.webclient.on_logout);
            self.user_menu.do_update();
        }
    });

    instance.web.FormView.include({
        can_be_discarded: function () {
            if (this.$el.is('.oe_form_dirty')) {
                var popup_content = '<div><p>The record has been modified, your changes will be discarded.</p><p>Please save or discard your changes.</p></div>';
                var popup = new instance.web.Dialog(this, {
                    title: _t('Warning'),
                    size: 'medium',
                    buttons: {
                        Ok: function () {
                            this.parents('.modal').modal('hide');
                        }}
                }, $(popup_content));
                popup.open();
                this.$el.removeClass('oe_form_dirty');
                return false;


            } else {
                return true;
            }
        },
    });

    //test menu foo
    instance.web.WebClient.include({
        show_application: function() {
            var self = this;
            self.toggle_bars(true);

            self.update_logo();
            //this.$('.oe_logo_edit_admin').click(function(ev) {
             //   self.logo_edit(ev);
            //});

            // Menu is rendered server-side thus we don't want the widget to create any dom
            self.menu = new instance.web.Menu(self);
            self.menu.setElement(this.$el.parents().find('.oe_application_menu_placeholder'));
            self.menu.start();
            self.menu.on('menu_click', this, this.on_menu_action);
            //self.user_menu = new instance.web.UserMenu(self);
            //self.user_menu.appendTo(this.$el.parents().find('.oe_user_menu_placeholder'));
            //self.user_menu.on('user_logout', self, self.on_logout);
            //self.user_menu.do_update();
            self.bind_hashchange();
            self.set_title();
            self.check_timezone();
            if (self.client_options.action_post_login) {
                self.action_manager.do_action(self.client_options.action_post_login);
                delete(self.client_options.action_post_login);
            }
        },
    });

    instance.web_kanban.KanbanView.include({
        do_show: function() {
            var application_height = $(window).height();
            var table_offset = $('.nh_kanban_scroll_fix').offset();
            var vertical_padding = 30;
            $('.nh_kanban_scroll_fix').css('height', ((application_height-table_offset.top) - (vertical_padding*2)));
            $('.oe_view_manager_switch').hide();
            if (this.$buttons) {
                this.$buttons.show();
            }
            this.do_push_state({});
            return this._super();
        },
        do_hide: function(){
            $('.oe_view_manager_switch').show();
            if (this.$buttons) {
                this.$buttons.hide();
            }
            return this._super();
        },
        do_add_group: function() {
            var self = this;
            self.do_action({
                name: _t("Add column"),
                res_model: self.group_by_field.relation,
                views: [[false, 'form']],
                type: 'ir.actions.act_window',
                target: "new",
                context: self.dataset.get_context(),
                flags: {
                    action_buttons: false,
                }
            });



            var am = instance.webclient.action_manager;
            var form = am.dialog_widget.views.form.controller;
            form.on("on_button_cancel", am.dialog, am.dialog.close);
            form.on('record_created', self, function(r) {
                (new instance.web.DataSet(self, self.group_by_field.relation)).name_get([r]).done(function(new_record) {
                    am.dialog.close();
                    var domain = self.dataset.domain.slice(0);
                    domain.push([self.group_by, '=', new_record[0][0]]);
                    var dataset = new instance.web.DataSetSearch(self, self.dataset.model, self.dataset.get_context(), domain);
                    var datagroup = {
                        get: function(key) {
                            return this[key];
                        },
                        value: new_record[0],
                        length: 0,
                        aggregates: {},
                    };
                    var new_group = new instance.web_kanban.KanbanGroup(self, [], datagroup, dataset);
                    self.do_add_groups([new_group]).done(function() {
                        $(window).scrollTo(self.groups.slice(-1)[0].$el, { axis: 'x' });
                    });
                });
            });
        },

    });

    instance.web_kanban.KanbanRecord.include({
          do_action_open: function($action){
              var self = this;
              var state = get_action_from_state(self.group.value);
              this.rpc('/web/action/load', {'action_id': 'nh_etake_list.action_show_'+state}).done(function(result){
                  result.res_id = self.id;
                  result.view_type = 'form';
                  instance.client.action_manager.do_action(result).done(function(){
                     $('tr[data-id='+self.id+']').trigger('click');
                  });
              });
          },
    });

    instance.web_kanban.KanbanGroup.include({
       start: function(){
           var self = this;
           if(self.dataset.model !== 'nh.etake_list.overview'){
               return self._super();
           }
           if (! self.view.group_by) {
               self.$el.addClass("oe_kanban_no_group");
               self.quick = new (get_class(self.view.quick_create_class))(this, self.dataset, {}, false)
                   .on('added', self, self.proxy('quick_created'));
               self.quick.replace($(".oe_kanban_no_group_qc_placeholder"));
           }
           this.$records = $(QWeb.render('KanbanView.group_records_container', { widget : this}));
           this.$records.insertBefore(this.view.$el.find('.oe_kanban_groups_records td:last'));

           this.$el.on('click', '.oe_kanban_group_dropdown li a', function(ev) {
               var fn = 'do_action_' + $(ev.target).data().action;
               if (typeof(self[fn]) === 'function') {
                   self[fn]($(ev.target));
               }
           });

           this.$el.find('.oe_kanban_add').click(function () {
               if (self.view.quick) {
                   self.view.quick.trigger('close');
               }
               if (self.quick) {
                   return false;
               }
               self.view.$el.find('.oe_view_nocontent').hide();
               var ctx = {};
               ctx['default_' + self.view.group_by] = self.value;
               self.quick = new (get_class(self.view.quick_create_class))(this, self.dataset, ctx, true)
                   .on('added', self, self.proxy('quick_created'))
                   .on('close', self, function() {
                       self.view.$el.find('.oe_view_nocontent').show();
                       this.quick.destroy();
                       delete self.view.quick;
                       delete this.quick;
                   });
               self.quick.appendTo($(".oe_kanban_group_list_header", self.$records));
               self.quick.focus();
               self.view.quick = self.quick;
           });
           this.$el.find('.nh_referral_add').click(function(){
               self.rpc('/web/action/load', {action_id: 'nh_etake_list.action_show_referral_forms'}).done(function(res){
                  self.rpc('/web/action/load', {action_id: 'nh_etake_list.action_new_referral_form'}).done(function(result) {

                      instance.client.on_menu_action({'action_id': result.id}).done(function () {
                          $('.oe_secondary_menu .active').removeClass('active');
                          $('.oe_secondary_menu a[data-action-id=' + res.id + ']').parent().addClass('active');
                      });
                  });
               });

           });
           this.$el.find('.nh_kanban_show_list').click(function(){
               var ds = $(this).attr('data-state');
               var state = get_action_from_state(ds);
              self.rpc('/web/action/load', {action_id: 'nh_etake_list.action_show_'+state}).done(function(result) {


                  instance.client.on_menu_action({'action_id': result.id}).done(function(){
                      $('.oe_secondary_menu .active').removeClass('active');
                      $('.oe_secondary_menu a[data-action-id='+result.id+']').parent().addClass('active');
                      //$('.oe_list_buttons .oe_list_add').trigger('click');
                  });

              });
           });
           // Add bounce effect on image '+' of kanban header when click on empty space of kanban grouped column.
           this.$records.on('click', '.oe_kanban_show_more', this.do_show_more);
           if (this.state.folded) {
               this.do_toggle_fold();
           }
           this.$el.data('widget', this);
           this.$records.data('widget', this);
           this.$has_been_started.resolve();
           var add_btn = this.$el.find('.oe_kanban_add');
           add_btn.tooltip({delay: { show: 500, hide:1000 }});
           this.$records.find(".oe_kanban_column_cards").click(function (ev) {
               if (ev.target == ev.currentTarget) {
                   if (!self.state.folded) {
                       add_btn.openerpBounce();
                   }
               }
           });
           this.is_started = true;
           var def_tooltip = this.fetch_tooltip();
           return $.when(def_tooltip);
       },
    });


    instance.web.ListView.include({
        start: function(){
            this.$el.addClass('oe_list');
            this._template = "NHListView";
            return this._super();
        },
        compute_aggregates: function(records) {
            var application_height = $(window).height();
            var table_offset = $('.nh_list_scroll_fix').offset();
            var vertical_padding = 15;
            $('.nh_list_scroll_fix').css('height', ((application_height-table_offset.top) - (vertical_padding*2)));



            var table_header_width = $('.nh_list_scroll_fix_body thead').width();
            $('.nh_list_scroll_fix_header').css('width', table_header_width);
            $('.nh_list_scroll_fix_header thead').css('width', table_header_width);
            var fixed_headers = $('.nh_list_scroll_fix_header .oe_list_header_columns th');
            $('.nh_list_scroll_fix_body .oe_list_header_columns th').each(function(i){
                $(fixed_headers[i]).find('div').css('width', $(this).find('div').width());
            });
            this._super(records);
        },
    })
}


function get_action_from_state(state){
    switch (state) {
        case 'Referral':
            return 'referrals';
            break;
        case 'TCI':
            return 'tci';
            break;
        case 'To be Clerked':
            return 'tbc';
            break;
        case 'Senior Review':
            return 'senior_reviews';
            break;
        case 'Consultant Review':
            return 'consultant_reviews';
            break;
        case 'Discharged':
            return 'discharged';
            break;
        case 'To Be Discharged':
            return 'tbd';
            break;
        case 'Other':
            return 'overview_kanban';
            break;
        case 'Clerking in Progress':
            return 'clerkings';
            break;
        case 'Done':
            return 'overview_kanban';
            break;
        case 'dna':
            return 'overview_kanban';
            break;
        case 'to_dna':
            return 'overview_kanban';
            break;
        case 'admitted':
            return 'admitted';
            break;
    }
}