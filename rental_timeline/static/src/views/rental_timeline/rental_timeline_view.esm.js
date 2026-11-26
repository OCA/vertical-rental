/** @odoo-module **/

import {RentalTimelineController} from "./rental_timeline_controller.esm";
import {RentalTimelineModel} from "./rental_timeline_model.esm";
import {RentalTimelineRenderer} from "./rental_timeline_renderer.esm";
import {TimelineView} from "@web_timeline/views/timeline/timeline_view.esm";
import {_lt} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

const viewRegistry = registry.category("views");

export const RentalTimelineView = {
    ...TimelineView,
    display_name: _lt("Rental Timeline"),
    Controller: RentalTimelineController,
    Model: RentalTimelineModel,
    Renderer: RentalTimelineRenderer,
};

viewRegistry.add("rental_timeline", RentalTimelineView);
