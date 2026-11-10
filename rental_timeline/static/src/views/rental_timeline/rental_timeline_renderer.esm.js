/** @odoo-module **/

import {TimelineRenderer} from "@web_timeline/views/timeline/timeline_renderer.esm";

export class RentalTimelineRenderer extends TimelineRenderer {
    init_timeline() {
        this.options.tooltip = {
            ...this.options.tooltip,
            followMouse: true,
            overflowMethod: "flip",
        };
        return super.init_timeline();
    }

    // Tags of the timeline-tooltip-item template, which vis-timeline would
    // otherwise escape when it shows the tooltip.
    getXSSWhiteList() {
        return {
            ...super.getXSSWhiteList(),
            table: ["class"],
            tbody: [],
            tr: [],
            td: ["id"],
        };
    }
}
