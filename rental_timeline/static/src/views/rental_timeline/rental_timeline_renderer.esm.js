/** @odoo-module **/

import {TimelineRenderer} from "@web_timeline/views/timeline/timeline_renderer.esm";

export class RentalTimelineRenderer extends TimelineRenderer {
    setup() {
        super.setup();
    }
    async init_timeline() {
        this.options.tooltip = {
            followMouse: true,
            overflowMethod: "flip",
        };
        super.init_timeline();
    }
}
