odoo.define("rental_timeline.RentalTimelineView", function(require) {
    "use strict";

    var core = require("web.core");
    var view_registry = require("web.view_registry");
    var TimelineModel = require("web_timeline.TimelineModel");
    var _TimelineView = require("web_timeline.TimelineView");
    var RentalTimelineRenderer = require("rental_timeline.RentalTimelineRenderer");
    var RentalTimelineController = require("rental_timeline.RentalTimelineController");
    var _lt = core._lt;

    var RentalTimelineView = _TimelineView.extend({
        display_name: _lt("Rental Timeline"),
        config: {
            Model: TimelineModel,
            Controller: RentalTimelineController,
            Renderer: RentalTimelineRenderer,
        },
    });

    view_registry.add("rental_timeline", RentalTimelineView);

    return RentalTimelineView;
});
