/** @odoo-module **/

import {FormViewDialog} from "@web/views/view_dialogs/form_view_dialog";
import {TimelineController} from "@web_timeline/views/timeline/timeline_controller.esm";

export class RentalTimelineController extends TimelineController {
    // Open the document the item comes from (click_res_model and click_res_id,
    // the sale order for rentals) read-only, not the product.timeline record.
    openItem(item_id, is_editable) {
        const record = this.model.data.find((rec) => rec.id === item_id);
        if (!record || !record.click_res_model || !record.click_res_id) {
            return super.openItem(item_id, is_editable);
        }
        this.Dialog = this.dialogService.add(FormViewDialog, {
            resModel: record.click_res_model,
            resId: record.click_res_id,
            preventCreate: true,
            preventEdit: true,
        });
    }
}
