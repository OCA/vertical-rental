/* global vis, py */
odoo.define("rental_timeline.RentalTimelineRenderer", function(require) {
    "use strict";

    var _TimelineRenderer = require("web_timeline.TimelineRenderer");
    var Popup = require("rental_timeline.Popup");

    var time = require("web.time");

    var is_default_product_id = true;
    var group_categ_again = 0;

    var RentalTimelineRenderer = _TimelineRenderer.extend({
        /**
         * Get the groups.
         *
         * @param {Object[]} events
         * @param {String[]} group_bys
         * @private
         * @returns {Array}
         */
        split_groups: function(events, group_bys) {
            if (group_bys.length === 0) {
                return events;
            }

            var groups = [];
            var self = this;
            // Groups.push({id: -1, content: _t('-')});

            _.each(events, function(event) {
                var product_group_name = event[_.first(["product_id"])];
                if (product_group_name) {
                    if (product_group_name instanceof Array) {
                        let group = _.find(groups, function(existing_group) {
                            return _.isEqual(existing_group.id, product_group_name[0]);
                        });

                        if (_.isUndefined(group)) {
                            var tooltip = null;
                            if (self.qweb.has_template("tooltip-item-group")) {
                                tooltip = self.qweb.render("tooltip-item-group", {
                                    record: event,
                                });
                            }
                            if (product_group_name[1].slice(0, 3) !== "All") {
                                group = {
                                    id: product_group_name[0],
                                    content: product_group_name[1],
                                    tooltip: tooltip,
                                    partner_id: event.partner_id,
                                    order_name: event.order_name,
                                    product_id: event.product_id,
                                };
                                groups.push(group);
                            }
                        }
                    }
                }
            });

            if (!is_default_product_id) {
                if (group_bys[0] === "product_categ_id") {
                    var group_categs = [];

                    _.each(events, function(event) {
                        var group_name = event[_.first(group_bys)];

                        if (group_name) {
                            if (group_name instanceof Array) {
                                let group = _.find(group_categs, function(
                                    existing_group
                                ) {
                                    return _.isEqual(
                                        existing_group.content,
                                        group_name[1]
                                    );
                                });

                                if (_.isUndefined(group)) {
                                    var tooltip = null;
                                    if (self.qweb.has_template("tooltip-item-group")) {
                                        tooltip = self.qweb.render(
                                            "tooltip-item-group",
                                            {
                                                record: event,
                                            }
                                        );
                                    }

                                    const nested_groups = [];
                                    _.each(events, function(event_p) {
                                        if (
                                            event_p.product_categ_name ===
                                            event.product_categ_name
                                        ) {
                                            if (
                                                !nested_groups.includes(
                                                    event_p.product_id[0]
                                                )
                                            ) {
                                                nested_groups.push(
                                                    event_p.product_id[0]
                                                );
                                            }
                                            console.log(
                                                `event_p.product_categ_name ${event_p.product_categ_name}`
                                            );
                                        }
                                    });

                                    group = {
                                        id: group_name[0] + 1000000,
                                        // Id: 100000 + counter,
                                        content: group_name[1],
                                        nestedGroups: nested_groups,
                                        tooltip: tooltip,
                                    };

                                    group_categs.push(group);
                                }
                            }
                        }
                    });
                    groups = groups.concat(group_categs);
                } else if (group_bys[0] === "order_name") {
                    var group_order_names = [];

                    _.each(events, function(event) {
                        var group_name = event[_.first(group_bys)];
                        if (group_name) {
                            if (group_name) {
                                let group = _.find(group_order_names, function(
                                    existing_group
                                ) {
                                    return _.isEqual(
                                        existing_group.content,
                                        group_name
                                    );
                                });
                                if (_.isUndefined(group)) {
                                    var tooltip = null;
                                    if (self.qweb.has_template("tooltip-item-group")) {
                                        tooltip = self.qweb.render(
                                            "tooltip-item-group",
                                            {
                                                record: event,
                                            }
                                        );
                                    }
                                    const nested_groups = [];
                                    _.each(events, function(event_o) {
                                        if (event_o.order_name === event.order_name) {
                                            if (
                                                !nested_groups.includes(
                                                    event_o.product_id[0]
                                                )
                                            ) {
                                                nested_groups.push(
                                                    event_o.product_id[0]
                                                );
                                            }
                                        }
                                    });
                                    group = {
                                        id: event.id + 1000000,
                                        content: group_name,
                                        nestedGroups: nested_groups,
                                        tooltip: tooltip,
                                        order_name: group_name,
                                    };
                                    group_order_names.push(group);
                                }
                            }
                        }
                    });

                    const groups_and_layersGroup = self.generate_sub_groups(
                        groups,
                        group_order_names,
                        "order_name"
                    );
                    groups = groups_and_layersGroup[0];
                    group_order_names = groups_and_layersGroup[1];

                    groups = groups.concat(group_order_names);
                } else if (group_bys[0] === "partner_id") {
                    var group_partners = [];

                    _.each(events, function(event) {
                        var group_name = event[_.first(group_bys)];
                        if (group_name) {
                            if (group_name instanceof Array) {
                                let group = _.find(group_partners, function(
                                    existing_group
                                ) {
                                    return _.isEqual(
                                        existing_group.content,
                                        group_name[1]
                                    );
                                });

                                if (_.isUndefined(group)) {
                                    var tooltip = null;
                                    if (self.qweb.has_template("tooltip-item-group")) {
                                        tooltip = self.qweb.render(
                                            "tooltip-item-group",
                                            {
                                                record: event,
                                            }
                                        );
                                    }

                                    const nested_groups = [];
                                    _.each(events, function(event_p) {
                                        if (
                                            event_p.partner_id[1] ===
                                            event.partner_id[1]
                                        ) {
                                            if (
                                                !nested_groups.includes(
                                                    event_p.product_id[0]
                                                )
                                            ) {
                                                nested_groups.push(
                                                    event_p.product_id[0]
                                                );
                                            }
                                        }
                                    });

                                    group = {
                                        id: group_name[0] + 1000000,
                                        content: group_name[1],
                                        nestedGroups: nested_groups,
                                        tooltip: tooltip,
                                        partner_id: group_name,
                                    };

                                    group_partners.push(group);
                                }
                            }
                        }
                    });

                    const groups_and_layersGroup = self.generate_sub_groups(
                        groups,
                        group_partners,
                        "partner_id"
                    );
                    groups = groups_and_layersGroup[0];
                    group_partners = groups_and_layersGroup[1];

                    groups = groups.concat(group_partners);
                }
            }

            is_default_product_id = true;
            return groups;
        },

        /**
         * Generate new sub group if the old sub groups have the same group ID.
         *
         * @param {String[]} groups
         * @param {String[]} layer_groups
         * @param {String} group_by
         * @private
         * @returns {[groups, layer_groups]}
         */
        generate_sub_groups: function(groups, layer_groups, group_by) {
            var ids = groups.map(group => {
                return group.id;
            });
            var max_id = Math.max(...ids);

            for (let i = 0; i < layer_groups.length - 1; i++) {
                for (let k = 0; k < layer_groups[i].nestedGroups.length; k++) {
                    for (let j = i + 1; j < layer_groups.length; j++) {
                        for (let m = 0; m < layer_groups[j].nestedGroups.length; m++) {
                            if (
                                layer_groups[i].nestedGroups[k] ===
                                layer_groups[j].nestedGroups[m]
                            ) {
                                const group = groups.find(
                                    elem => elem.id === layer_groups[j].nestedGroups[m]
                                );
                                const newGroup = Object.assign({}, group);
                                newGroup.original_id = newGroup.id;

                                max_id++;
                                newGroup.id = max_id;
                                if (group_by === "partner_id") {
                                    newGroup.partner_id = layer_groups[j].partner_id;
                                } else if (group_by === "order_name") {
                                    newGroup.order_name = layer_groups[j].order_name;
                                }
                                groups.push(newGroup);
                                layer_groups[j].nestedGroups[m] = newGroup.id;
                            }
                        }
                    }
                }
            }

            return [groups, layer_groups];
        },

        /**
         * Transform Odoo event object to timeline event object.
         *
         * @param {TransformEvent} evt
         * @private
         * @returns {Object}
         */
        event_data_transform: function(evt) {
            var self = this;
            var date_start = new moment();
            var date_stop = null;

            var date_delay = evt[this.date_delay] || false,
                all_day = this.all_day ? evt[this.all_day] : false;

            if (all_day) {
                date_start = time.auto_str_to_date(
                    evt[this.date_start].split(" ")[0],
                    "start"
                );
                if (this.no_period) {
                    date_stop = date_start;
                } else {
                    date_stop = this.date_stop
                        ? time.auto_str_to_date(
                              evt[this.date_stop].split(" ")[0],
                              "stop"
                          )
                        : null;
                }
            } else {
                date_start = time.auto_str_to_date(evt[this.date_start]);
                date_stop = this.date_stop
                    ? time.auto_str_to_date(evt[this.date_stop])
                    : null;
            }

            if (!date_stop && date_delay) {
                date_stop = moment(date_start)
                    .add(date_delay, "hours")
                    .toDate();
            }

            var group = evt.product_id;
            if (
                self.last_group_bys[0] !== "product_categ_id" &&
                self.last_group_bys[0] !== "order_name" &&
                self.last_group_bys[0] !== "partner_id"
            ) {
                group = evt[self.last_group_bys[0]];
            }
            if (group) {
                if (group instanceof Array) {
                    group = _.first(group);
                }
            } else {
                group = -1;
            }
            var color = null;
            if (self.arch.attrs.color_field !== undefined) {
                color = evt[self.arch.attrs.color_field];
            } else if (self.arch.attrs.color_field === undefined) {
                _.each(self.colors, function(col) {
                    if (py.eval(`'${evt[col.field]}' ${col.opt} '${col.value}'`)) {
                        color = col.color;
                    }
                });
            }

            var content = _.isUndefined(evt.__name) ? evt.display_name : evt.__name;
            if (this.arch.children.length) {
                content = this.render_timeline_item(evt);
            }

            var title = "";
            if (content) {
                var doc = document.createElement("html");
                doc.innerHTML = "<html><body>" + content + "</body></html>";
                var tt_content = doc.getElementsByClassName("tooltip_content");
                if (tt_content && tt_content.length) {
                    title = tt_content[0].innerHTML;
                }
            }

            var r = {
                title: title,
                start: date_start,
                content: content,
                id: evt.id,
                group: group,
                evt: evt,
                style: "background-color: " + color + ";",
            };
            // Check if the event is instantaneous, if so, display it with a point on the timeline (no 'end')
            if (date_stop && !moment(date_start).isSame(date_stop)) {
                r.end = date_stop;
            }
            return r;
        },

        init_timeline: function() {
            var self = this;
            var util = vis.util;
            is_default_product_id = false;

            this._super();
            this.options.editable = {
                add: false,
                updateTime: false,
                updateGroup: false,
                remove: false,
            };
            this.options.orientation = {
                item: "top",
                axis: "top",
            };
            this.options.verticalScroll = true;
            this.options.rtl = false;
            this.timeline.setOptions(this.options);

            // This.timeline.on('click', self.on_parent_group_click)

            this.timeline.on("doubleClick", self.on_group_double_click);
            // This.timeline.on('click', self.on_group_click);
            this.timeline.on("click", function(props) {
                props.event.preventDefault();
            });

            // Turn off the internal hammer tap event listener
            this.timeline.off("changed").on("changed", function() {
                this.options.orientation = {
                    item: "top",
                    axis: "top",
                };
                self.draw_canvas();
                self.canvas.$el.attr(
                    "style",
                    self.$el.find(".vis-content").attr("style") +
                        self.$el.find(".vis-itemset").attr("style")
                );
            });

            (function(_create, setData) {
                vis.timeline.components.Group.prototype.setData = function(data) {
                    setData.apply(this, [data]);
                    this.copy_data = data;
                };
                vis.timeline.components.Group.prototype._create = function() {
                    _create.apply(this);
                    this.popup = null;
                    this.dom.label.addEventListener(
                        "mouseover",
                        this._onMouseOver.bind(this)
                    );
                    this.dom.label.addEventListener(
                        "mouseout",
                        this._onMouseOut.bind(this)
                    );
                    this.dom.label.addEventListener(
                        "mousemove",
                        this._onMouseMove.bind(this)
                    );
                };
                vis.timeline.components.Group.prototype._onMouseOver = function(event) {
                    if (this.copy_data.tooltip === null) return;
                    if (this.popup === null)
                        this.popup = new Popup(this.itemSet.body.dom.root, "flip");
                    this.popup.setText(this.copy_data.tooltip);
                    var container = this.itemSet.body.dom.centerContainer;
                    this.popup.setPosition(
                        event.clientX -
                            util.getAbsoluteLeft(container) +
                            container.offsetLeft,
                        event.clientY -
                            util.getAbsoluteTop(container) +
                            container.offsetTop
                    );
                    this.popup.show();
                };
                vis.timeline.components.Group.prototype._onMouseOut = function(event) {
                    if (this.popup !== null) {
                        this.popup.hide();
                    }
                    console.log(event);
                };
                vis.timeline.components.Group.prototype._onMouseMove = function(event) {
                    if (this.popup) {
                        if (!this.popup.hidden) {
                            var container = this.itemSet.body.dom.centerContainer;
                            this.popup.setPosition(
                                event.clientX -
                                    util.getAbsoluteLeft(container) +
                                    container.offsetLeft,
                                event.clientY -
                                    util.getAbsoluteTop(container) +
                                    container.offsetTop
                            );
                            // Redraw
                            this.popup.show();
                        }
                    }
                };
            })(
                vis.timeline.components.Group.prototype._create,
                vis.timeline.components.Group.prototype.setData
            );

            (function(_onUpdateItem) {
                // We set the option add=false, so we must overwrite the function _onUpdateItem
                // because in the function _onUpdateItem is a check if add is true
                // now we set add to true, call the function and set add back to false
                vis.timeline.components.ItemSet.prototype._onUpdateItem = function(
                    item
                ) {
                    var add = this.options.editable.add;
                    this.options.editable.add = true;
                    _onUpdateItem.apply(this, [item]);
                    this.options.editable.add = add;
                };
            })(vis.timeline.components.ItemSet.prototype._onUpdateItem);

            (function(_repaintDragCenter) {
                // We set the option updateTime=false, so we must overwrite the function _onUpdateItem
                // because in the function _onUpdateItem is a check if updateTime is true
                // now we set updateTime to true, call the function and set updateTime back to false
                vis.timeline.components.items.Item.prototype._repaintDragCenter = function() {
                    var updateTime = this.options.editable.updateTime;
                    this.options.editable.updateTime = true;
                    _repaintDragCenter.apply(this);
                    this.options.editable.updateTime = updateTime;

                    //                     If(this.selected && !this.dom.dragCenter && false){
                    //                         hammer.off('tap');
                    //                         hammer.off('doubletap');
                    //                         hammer.on('tap', function(event){
                    //                             //event.stopPropagation();
                    //                             me.parent.itemSet._onUpdateItem(me);
                    //                             me.parent.itemSet.body.emitter.emit('click', {
                    //                                 event: event,
                    //                                 item: me.id
                    //                             });
                    //                         });
                    //                     }
                };
            })(vis.timeline.components.items.Item.prototype._repaintDragCenter);
        },

        /**
         * Handle double click on a group header.
         *
         * @param {ClickEvent} e
         * @private
         */
        on_group_double_click: function(e) {
            if (e.what === "group-label" && e.group !== -1) {
                this._trigger(
                    e,
                    function() {
                        // Do nothing
                    },
                    "onGroupDoubleClick"
                );
            }
        },

        /**
         * Set groups and events.
         *
         * @param {Object[]} events
         * @param {String[]} group_bys
         * @param {Boolean} x2x
         * @param {Boolean} adjust_window
         * @private
         */
        on_data_loaded_2: function(events, group_bys, x2x, adjust_window) {
            var self = this;
            var data = [];
            var groups = [];

            if (group_bys[0] === "product_categ_id" && group_categ_again % 2 === 0) {
                is_default_product_id = false;
                group_categ_again += 2;
            } else if (group_bys[0] === "order_name" && group_categ_again % 2 === 0) {
                is_default_product_id = false;
                group_categ_again += 2;
            } else if (group_bys[0] === "partner_id" && group_categ_again % 2 === 0) {
                is_default_product_id = false;
                group_categ_again += 2;
            }

            if (
                group_bys[0] !== "product_categ_id" &&
                group_bys[0] !== "order_name" &&
                group_bys[0] !== "partner_id"
            ) {
                this.grouped_by = group_bys;

                _.each(events, function(event) {
                    if (event[self.date_start]) {
                        if (x2x) {
                            _.each(event[group_bys], function(gr) {
                                var x2x_object = jQuery.extend({}, event);
                                x2x_object[group_bys] = [gr];
                                // Creating a UNIQUE id with [id]_[gr].
                                // This id is unique due the unique relationship
                                // between two records in O2M or M2M
                                x2x_object.id = event.id + "_" + gr;
                                data.push(self.event_data_transform(x2x_object));
                            });
                        } else {
                            data.push(self.event_data_transform(event));
                        }
                    }
                });

                group_categ_again++;
            } else {
                this.grouped_by = "product_id";
                _.each(events, function(event) {
                    if (event[self.date_start]) {
                        if (x2x) {
                            _.each(event.product_id, function(gr) {
                                var x2x_object = jQuery.extend({}, event);
                                x2x_object.product_id = [gr];
                                // Creating a UNIQUE id with [id]_[gr].
                                // This id is unique due the unique relationship
                                // between two records in O2M or M2M
                                x2x_object.id = event.id + "_" + gr;
                                data.push(self.event_data_transform(x2x_object));
                            });
                        } else {
                            data.push(self.event_data_transform(event));
                        }
                    }
                });

                group_categ_again++;
            }

            if (typeof this.$select_groups !== "undefined") {
                this.$(".selected-groups").html("");
                this.$select_groups.remove();
            }
            groups = this.split_groups(events, group_bys);

            if (group_bys[0] === "partner_id") {
                for (let i = 0; i < groups.length; i++) {
                    data.forEach(item => {
                        if (!("nestedGroups" in groups[i])) {
                            // If(item.group === groups[i].id && !_.isEqual(item.evt.partner_id, groups[i].partner_id)){
                            //     if(i +1 < groups.length) {
                            //         for(let j = i +1 ; j < groups.length; j ++) {
                            //             if(!('nestedGroups' in groups[j])) {
                            //                 if(_.isEqual(item.evt.product_id, groups[j].product_id)){
                            //                     if(_.isEqual(item.evt.partner_id, groups[j].partner_id)) {
                            //                         item.original_group = item.group
                            //                         item.group = groups[j].id
                            //                     }
                            //                 }
                            //             }
                            //         }
                            //     }
                            // } else
                            if (
                                item.group !== groups[i].id &&
                                _.isEqual(item.evt.product_id, groups[i].product_id) &&
                                _.isEqual(item.evt.partner_id, groups[i].partner_id)
                            ) {
                                item.group = groups[i].id;
                            }
                        }
                    });
                }
            }

            if (group_bys[0] === "order_name") {
                for (let i = 0; i < groups.length; i++) {
                    data.forEach(item => {
                        if (!("nestedGroups" in groups[i])) {
                            // If(item.group === groups[i].id && item.evt.order_name !== groups[i].order_name){
                            //     if(i +1 < groups.length) {
                            //         for(let j = i +1 ; j < groups.length; j ++) {
                            //             if( item.evt.order_name === groups[j].order_name && _.isEqual(item.evt.product_id, groups[j].product_id)){
                            //                 item.original_group = item.group
                            //                 item.group = groups[j].id
                            //             }
                            //         }
                            //     }
                            // } else
                            if (
                                item.group !== groups[i].id &&
                                _.isEqual(item.evt.product_id, groups[i].product_id) &&
                                item.evt.order_name === groups[i].order_name
                            ) {
                                item.group = groups[i].id;
                            }
                        }
                    });
                }
            }

            groups = new vis.DataSet(groups);
            this.timeline.setGroups(groups);
            this.timeline.setItems(data);
            var mode = !this.mode || this.mode === "fit";
            var adjust = _.isUndefined(adjust_window) || adjust_window;
            if (mode && adjust) {
                this.timeline.fit();
            }
        },

        _do_nothing: function() {
            console.log("click event is fired");
        },

        _onTodayClicked: function() {
            this._scaleCurrentWindow(1, "days", "day");
        },

        _onScaleDayClicked: function() {
            this._scaleCurrentWindow(1, "days", "now");
        },

        _onScaleWeekClicked: function() {
            this._scaleCurrentWindow(7, "days", "now");
        },

        _onScaleMonthClicked: function() {
            this._scaleCurrentWindow(1, "months", "now");
        },

        _onScaleYearClicked: function() {
            this._scaleCurrentWindow(1, "years", "now");
        },

        _scaleCurrentWindow: function(
            factor,
            time_unit = "hours",
            startOf = "current_window"
        ) {
            if (this.timeline) {
                var start = null;
                if (startOf === "current_window") {
                    start = this.timeline.getWindow().start;
                } else {
                    var moment_now = new moment();
                    start =
                        startOf === "now" ? moment_now : moment_now.startOf(startOf);
                }
                this.current_window = {
                    start: start,
                    end: moment(start).add(factor, time_unit),
                };
                this.timeline.setWindow(this.current_window);
            }
        },
    });

    return RentalTimelineRenderer;
});
