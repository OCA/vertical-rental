/** @odoo-module **/

import {KanbanCompiler} from "@web/views/kanban/kanban_compiler";
import {TimelineModel} from "@web_timeline/views/timeline/timeline_model.esm";
import {registry} from "@web/core/registry";
const formatters = registry.category("formatters");
const parsers = registry.category("parsers");
import {renderToString} from "@web/core/utils/render";
import {useViewCompiler} from "@web/views/view_compiler";

export class RentalTimelineModel extends TimelineModel {
    setup() {
        super.setup(...arguments);
        this.templates = useViewCompiler(KanbanCompiler, this.params.templateDocs);
    }

    /* Load the tooltip template (t-name="timeline-tooltip-item") */
    render_timeline_tooltip(record, template) {
        let template_tooltip = "";
        if (record)
            template_tooltip = renderToString(this.templates[template], {
                record: record,
                formatters,
                parsers,
            });
        return template_tooltip;
    }
    _event_data_transform(record) {
        var timeline_item = super._event_data_transform(record);
        const template_tooltip = this.render_timeline_tooltip(
            record,
            "timeline-tooltip-item"
        );
        timeline_item.title = `<html><body> ${template_tooltip} </body></html>`;
        return timeline_item;
    }
}
