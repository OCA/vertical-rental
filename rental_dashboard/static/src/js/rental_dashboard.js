/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {
    Component,
    useState,
    onWillStart,
    onMounted,
    onWillUnmount,
    useRef,
} from "@odoo/owl";
import {View} from "@web/views/view";

export class RentalDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.viewService = useService("view");

        this.calendarRef = useRef("calendarContainer");

        this.state = useState({
            // Filters
            selectedLocation: null,
            dateFrom: null,
            dateTo: null,
            showDatePicker: false,
            showAvailableOnly: false,
            selectedProducts: [],

            // Data
            locations: [],
            warehouses: [],
            products: [],
            modalProducts: [],
            customers: [],
            rentalPeriods: [],

            // Calendar key for re-render
            calendarKey: 0,
            viewLoaded: false,

            // Modal state
            showModal: false,
            modalMode: "create",
            editingOrderId: null,
            createdOrderId: null,
            modalData: {
                locationId: null,
                customerId: null,
                customerSearch: "",
                startDate: null,
                endDate: null,
                state: null,
                lines: [],
            },
        });

        // Bind event handlers once (for proper removeEventListener)
        this.onCalendarClick = this.onCalendarClick.bind(this);
        this.onEventMouseOver = this.onEventMouseOver.bind(this);
        this.onEventMouseOut = this.onEventMouseOut.bind(this);

        // Tooltip tracking (plain DOM, not OWL state)
        this.tooltipTimeout = null;
        this.currentHoveredEventId = null;
        this.tooltipEl = null;
        this.tooltipCache = new Map();

        // Track calendar cell drag for date range selection
        this.dragStartDate = null;
        this.dragEndDate = null;
        this._isDraggingCalendar = false;

        // ── Lifecycle ──

        onWillStart(async () => {
            // Single RPC replaces loadLocations + loadRentalPeriods + loadProducts
            const data = await this.orm.call(
                "product.product",
                "get_rental_dashboard_data",
                [],
                {location_id: null, date_from: null, date_to: null}
            );
            this.state.locations = data.locations;
            this.state.warehouses = data.warehouses;
            this.state.rentalPeriods = data.rental_periods;
            this.state.products = data.products;
        });

        onMounted(() => {
            this._setupCalendarListeners();
            this._setupTooltipElement();
            this._setupCalendarObserver();
            this._setupDialogObserver();
            this.state.viewLoaded = true;
        });

        onWillUnmount(() => {
            // Calendar listeners
            if (this.calendarRef.el) {
                this.calendarRef.el.removeEventListener(
                    "click",
                    this.onCalendarClick,
                    true
                );
                this.calendarRef.el.removeEventListener(
                    "mouseover",
                    this.onEventMouseOver
                );
                this.calendarRef.el.removeEventListener(
                    "mouseout",
                    this.onEventMouseOut
                );
            }
            // Document-level listeners (fix memory leak)
            if (this._onCalendarDragMove) {
                document.removeEventListener("mousemove", this._onCalendarDragMove);
            }
            if (this._onCalendarDragEnd) {
                document.removeEventListener("mouseup", this._onCalendarDragEnd);
            }
            // Observers
            if (this.calendarObserver) this.calendarObserver.disconnect();
            if (this.dialogObserver) this.dialogObserver.disconnect();
            // Tooltip
            if (this.tooltipEl) this.tooltipEl.remove();
            if (this.tooltipTimeout) clearTimeout(this.tooltipTimeout);
            if (this.highlightDebounce) clearTimeout(this.highlightDebounce);
        });
    }

    // ── Setup helpers (extracted from onMounted for readability) ──

    _setupCalendarListeners() {
        if (!this.calendarRef.el) return;

        this.calendarRef.el.addEventListener("click", this.onCalendarClick, true);
        this.calendarRef.el.addEventListener("mouseover", this.onEventMouseOver);
        this.calendarRef.el.addEventListener("mouseout", this.onEventMouseOut);

        // Drag selection on calendar cells
        this.calendarRef.el.addEventListener("mousedown", (ev) => {
            const elements = document.elementsFromPoint(ev.clientX, ev.clientY);
            if (
                elements.some(
                    (el) =>
                        (el.classList && el.classList.contains("fc-event")) ||
                        (el.closest && el.closest(".fc-event"))
                )
            )
                return;

            let date = null;
            for (const el of elements) {
                if (el.hasAttribute && el.hasAttribute("data-date")) {
                    date = el.getAttribute("data-date");
                    break;
                }
            }
            if (date) {
                this.dragStartDate = date;
                this.dragEndDate = date;
                this._isDraggingCalendar = true;
            }
        });

        this._onCalendarDragMove = (ev) => {
            if (!this._isDraggingCalendar) return;
            const elements = document.elementsFromPoint(ev.clientX, ev.clientY);
            for (const el of elements) {
                if (el.hasAttribute("data-date")) {
                    this.dragEndDate = el.getAttribute("data-date");
                    break;
                }
            }
        };
        this._onCalendarDragEnd = () => {
            this._isDraggingCalendar = false;
        };
        document.addEventListener("mousemove", this._onCalendarDragMove);
        document.addEventListener("mouseup", this._onCalendarDragEnd);
    }

    _setupTooltipElement() {
        this.tooltipEl = document.createElement("div");
        this.tooltipEl.className = "rental-event-tooltip";
        this.tooltipEl.style.display = "none";
        document.body.appendChild(this.tooltipEl);
    }

    _setupCalendarObserver() {
        this.highlightDebounce = null;
        this.calendarObserver = new MutationObserver(() => {
            if (this.highlightDebounce) clearTimeout(this.highlightDebounce);
            this.highlightDebounce = setTimeout(
                () => this.applyDateRangeHighlight(),
                200
            );
        });
        if (this.calendarRef.el) {
            this.calendarObserver.observe(this.calendarRef.el, {
                childList: true,
                subtree: true,
            });
        }
    }

    _setupDialogObserver() {
        this.dialogObserver = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType !== 1) continue;
                    if (this._isOdooDialog(node) && this.dragStartDate) {
                        const closeBtn = node.querySelector(
                            ".btn-close, .o_form_button_cancel, .close"
                        );
                        if (closeBtn) {
                            closeBtn.click();
                        } else {
                            node.remove();
                        }
                        const start = this.dragStartDate;
                        const end = this.dragEndDate || this.dragStartDate;
                        const sortedStart = start < end ? start : end;
                        const sortedEnd = start < end ? end : start;
                        this.dragStartDate = null;
                        this.dragEndDate = null;
                        this.openCreateModalWithDates(sortedStart, sortedEnd);
                        return;
                    }
                }
                for (const node of mutation.removedNodes) {
                    if (node.nodeType !== 1) continue;
                    if (this._isOdooDialog(node)) {
                        setTimeout(() => this.loadProducts(), 300);
                    }
                }
            }
        });
        this.dialogObserver.observe(document.body, {childList: true, subtree: true});
    }

    _isOdooDialog(node) {
        return (
            node.classList?.contains("o_dialog") ||
            node.classList?.contains("modal") ||
            node.classList?.contains("o_technical_modal") ||
            node.classList?.contains("o_FormViewDialog") ||
            node.querySelector?.(".o_form_view") ||
            node.querySelector?.(".modal-dialog")
        );
    }

    // ── Event handlers ──

    _getRecordIdFromEvent(eventEl) {
        let recordId = eventEl.dataset.eventId || eventEl.getAttribute("data-event-id");
        if (!recordId && eventEl.fcSeg) {
            const fcEvent = eventEl.fcSeg.eventRange?.def;
            recordId = fcEvent?.publicId || fcEvent?.extendedProps?.recordId;
        }
        if (!recordId) {
            const link = eventEl.querySelector('a[href*="id="]');
            if (link) {
                const match = link.href.match(/id=(\d+)/);
                if (match) recordId = match[1];
            }
        }
        if (!recordId) {
            const eventData = eventEl.__data__ || eventEl._fc_event;
            if (eventData) recordId = eventData.id || eventData.publicId;
        }
        return recordId;
    }

    onCalendarClick(ev) {
        this.hideTooltip();
        if (ev.target.closest(".fc-more-link, .fc-daygrid-more-link, .fc-more")) return;

        const eventEl = ev.target.closest(".fc-event");
        if (eventEl) {
            ev.stopPropagation();
            ev.preventDefault();
            const recordId = this._getRecordIdFromEvent(eventEl);
            if (recordId) this.openEditModal(parseInt(recordId));
        }
    }

    onEventMouseOver(ev) {
        const eventEl = ev.target.closest(".fc-event");
        if (!eventEl || this.state.showModal) return;

        const recordId = this._getRecordIdFromEvent(eventEl);
        if (!recordId) return;

        if (
            this.currentHoveredEventId === recordId &&
            this.tooltipEl.style.display !== "none"
        )
            return;

        if (this.tooltipTimeout) {
            clearTimeout(this.tooltipTimeout);
            this.tooltipTimeout = null;
        }

        this.currentHoveredEventId = recordId;

        // Use cached data if available
        if (this.tooltipCache.has(recordId)) {
            this._showTooltip(eventEl, this.tooltipCache.get(recordId));
        } else {
            this.orm
                .searchRead(
                    "sale.order.line",
                    [["id", "=", parseInt(recordId)]],
                    [
                        "id",
                        "product_id",
                        "start_datetime",
                        "end_datetime",
                        "order_partner_id",
                        "order_id",
                        "rental_qty",
                        "state",
                    ]
                )
                .then(([soLine]) => {
                    if (this.currentHoveredEventId !== recordId) return;
                    if (this.state.showModal) return;
                    if (soLine) {
                        this.tooltipCache.set(recordId, soLine);
                        this._showTooltip(eventEl, soLine);
                    }
                });
        }
    }

    _showTooltip(eventEl, soLine) {
        const rect = eventEl.getBoundingClientRect();
        const productName = soLine.product_id ? soLine.product_id[1] : "No product";
        const startDate = this._formatTooltipDate(soLine.start_datetime);
        const endDate = this._formatTooltipDate(soLine.end_datetime);
        const customer = soLine.order_partner_id
            ? soLine.order_partner_id[1]
            : "No customer";
        const orderName = soLine.order_id ? soLine.order_id[1] : "";

        this.tooltipEl.innerHTML = `
            <div class="tooltip-content">
                <div class="tooltip-title fw-bold mb-2">${_.escape(productName)}</div>
                <div class="tooltip-dates mb-2">${_.escape(startDate)} - ${_.escape(
            endDate
        )}</div>
                <div class="tooltip-info">
                    <div class="d-flex align-items-center mb-1">
                        <i class="fa fa-file-text-o me-2 text-muted"></i>
                        <span>${_.escape(orderName)}</span>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <i class="fa fa-user me-2 text-muted"></i>
                        <span>${_.escape(customer)}</span>
                    </div>
                    <div class="d-flex align-items-center">
                        <i class="fa fa-cubes me-2 text-muted"></i>
                        <span>Qty: ${soLine.rental_qty}</span>
                    </div>
                </div>
            </div>`;
        this.tooltipEl.style.left = rect.left + rect.width / 2 + "px";
        this.tooltipEl.style.top = rect.top - 10 + "px";
        this.tooltipEl.style.display = "";
    }

    onEventMouseOut(ev) {
        const eventEl = ev.target.closest(".fc-event");
        if (!eventEl) return;
        if (ev.relatedTarget && eventEl.contains(ev.relatedTarget)) return;

        this.tooltipTimeout = setTimeout(() => {
            if (this.tooltipEl) this.tooltipEl.style.display = "none";
            this.currentHoveredEventId = null;
        }, 100);
    }

    hideTooltip() {
        if (this.tooltipTimeout) clearTimeout(this.tooltipTimeout);
        if (this.tooltipEl) this.tooltipEl.style.display = "none";
        this.currentHoveredEventId = null;
    }

    _formatTooltipDate(dateStr) {
        if (!dateStr) return "";
        const date = new Date(dateStr);
        return `${date.getMonth() + 1}/${date.getDate()}/${String(
            date.getFullYear()
        ).slice(-2)}`;
    }

    // ── Data loading ──

    async loadProducts() {
        // Single RPC replaces 3 separate searchRead calls
        const products = await this.orm.call(
            "product.product",
            "get_rental_products",
            [],
            {
                location_id: this.state.selectedLocation,
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
            }
        );
        this.state.products = products;
    }

    async loadModalProducts() {
        // Single RPC replaces 4+ separate searchRead calls
        // Also includes pricings so no separate pricing lookups needed
        this.state.modalProducts = await this.orm.call(
            "product.product",
            "get_rental_modal_products",
            [],
            {location_id: this.state.modalData.locationId}
        );
    }

    get filteredProducts() {
        let products = this.state.products;
        if (this.state.showAvailableOnly) {
            products = products.filter((p) => p.qty_available > 0);
        }
        return products;
    }

    get calendarDomain() {
        const domain = [
            ["rental", "=", true],
            ["state", "not in", ["cancel"]],
        ];

        if (this.state.selectedLocation) {
            const loc = this.state.locations.find(
                (l) => l.id === this.state.selectedLocation
            );
            if (loc) domain.push(["order_id.warehouse_id", "=", loc.warehouse_id]);
        }
        if (this.state.dateFrom)
            domain.push(["end_datetime", ">=", this.state.dateFrom]);
        if (this.state.dateTo) domain.push(["start_datetime", "<=", this.state.dateTo]);
        if (this.state.selectedProducts.length > 0) {
            domain.push([
                "product_id.rented_product_id",
                "in",
                this.state.selectedProducts,
            ]);
        }
        return domain;
    }

    get calendarProps() {
        if (!this.state.viewLoaded) return null;
        return {
            resModel: "sale.order.line",
            type: "calendar",
            domain: this.calendarDomain,
            context: this.props.context || {},
            display: {},
        };
    }

    // ── Filter actions ──

    async onLocationChange(ev) {
        const value = ev.target.value;
        this.state.selectedLocation = value ? parseInt(value) : null;
        this.state.selectedProducts = [];
        await this.loadProducts();
        this._refreshCalendar();
    }

    onShowAvailableChange(ev) {
        this.state.showAvailableOnly = ev.target.checked;
    }

    onProductSelect(productId) {
        const index = this.state.selectedProducts.indexOf(productId);
        if (index > -1) {
            this.state.selectedProducts.splice(index, 1);
        } else {
            this.state.selectedProducts.push(productId);
        }
        this._refreshCalendar();
    }

    isProductSelected(productId) {
        return this.state.selectedProducts.includes(productId);
    }

    async clearFilters() {
        this.state.selectedLocation = null;
        this.state.dateFrom = null;
        this.state.dateTo = null;
        this.state.showDatePicker = false;
        this.state.showAvailableOnly = false;
        this.state.selectedProducts = [];
        await this.loadProducts();
        this._refreshCalendar();
    }

    // ── Date filter ──

    toggleDatePicker() {
        this.state.showDatePicker = !this.state.showDatePicker;
    }

    onDateFromChange(ev) {
        this.state.dateFrom = ev.target.value || null;
    }

    onDateToChange(ev) {
        this.state.dateTo = ev.target.value || null;
    }

    async applyDateFilter() {
        this.state.showDatePicker = false;
        this._refreshCalendar();
        await this.loadProducts();
        setTimeout(() => this.applyDateRangeHighlight(), 500);
    }

    async clearDateFilter() {
        this.state.dateFrom = null;
        this.state.dateTo = null;
        this.state.showDatePicker = false;
        this._refreshCalendar();
        await this.loadProducts();
        this.applyDateRangeHighlight();
    }

    applyDateRangeHighlight() {
        if (!this.calendarRef.el) return;

        let dayCells = this.calendarRef.el.querySelectorAll(
            ".fc-daygrid-day[data-date]"
        );
        if (!dayCells.length)
            dayCells = this.calendarRef.el.querySelectorAll("td[data-date]");
        if (!dayCells.length)
            dayCells = this.calendarRef.el.querySelectorAll(".fc-day[data-date]");
        if (!dayCells.length) return;

        dayCells.forEach((cell) =>
            cell.classList.remove("date-in-range", "date-outside-range")
        );

        if (!this.state.dateFrom || !this.state.dateTo) return;

        const fromDate = new Date(this.state.dateFrom + "T00:00:00");
        const toDate = new Date(this.state.dateTo + "T23:59:59");

        dayCells.forEach((cell) => {
            const dateAttr = cell.getAttribute("data-date");
            if (!dateAttr) return;
            const cellDate = new Date(dateAttr + "T12:00:00");
            cell.classList.add(
                cellDate >= fromDate && cellDate <= toDate
                    ? "date-in-range"
                    : "date-outside-range"
            );
        });
    }

    formatDateRange() {
        if (!this.state.dateFrom || !this.state.dateTo) return "";
        const from = new Date(this.state.dateFrom);
        const to = new Date(this.state.dateTo);
        const diffDays = Math.ceil(Math.abs(to - from) / (1000 * 60 * 60 * 24)) + 1;
        const fmt = (d) =>
            `${d.getMonth() + 1}/${d.getDate()}/${String(d.getFullYear()).slice(-2)}`;
        return `${fmt(from)} - ${fmt(to)} (${diffDays} days)`;
    }

    // ── Calendar helpers ──

    _refreshCalendar() {
        this.tooltipCache.clear();
        this.state.calendarKey++;
    }

    // ── Modal: create ──

    async openCreateModal() {
        this.state.modalMode = "create";
        this.state.editingOrderId = null;
        this.state.modalData = {
            locationId: this.state.selectedLocation,
            customerId: null,
            customerSearch: "",
            startDate: this.state.dateFrom || this._formatDateForInput(new Date()),
            endDate:
                this.state.dateTo ||
                this._formatDateForInput(
                    new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                ),
            state: null,
            lines: [],
        };

        await this.loadModalProducts();

        // Build lines from pre-selected products (synchronous — pricings are cached)
        const lines = [];
        for (const physicalId of this.state.selectedProducts) {
            const service = this.state.modalProducts.find(
                (p) => p.physicalProductId === physicalId
            );
            if (service) {
                const availablePeriodIds = service.pricings.map((p) => p.period_id);
                const rentalPeriodId =
                    availablePeriodIds.length > 0 ? availablePeriodIds[0] : null;
                const priceUnit = rentalPeriodId
                    ? this._computePriceUnit(service.id, rentalPeriodId)
                    : 0;
                lines.push({
                    id: Date.now() + Math.random(),
                    productId: service.id,
                    rentalType: "new_rental",
                    rentalPeriodId,
                    availablePeriodIds,
                    rentalQty: 1,
                    priceUnit,
                    available: service.qty_available || 0,
                });
            }
        }

        this.state.modalData.lines =
            lines.length > 0 ? lines : [this._createEmptyLine()];
        this.hideTooltip();
        this.state.showModal = true;
    }

    async openCreateModalWithDates(startDate, endDate) {
        this.state.modalMode = "create";
        this.state.editingOrderId = null;
        this.state.modalData = {
            locationId: this.state.selectedLocation,
            customerId: null,
            customerSearch: "",
            startDate,
            endDate,
            state: null,
            lines: [],
        };

        await this.loadModalProducts();
        this.state.modalData.lines = [this._createEmptyLine()];
        this.hideTooltip();
        this.state.showModal = true;
    }

    // ── Modal: edit ──

    async openEditModal(soLineId) {
        try {
            // Single RPC replaces 3 sequential RPCs + loadModalProducts (4+ RPCs)
            const data = await this.orm.call(
                "sale.order.line",
                "get_rental_order_edit_data",
                [soLineId]
            );
            if (!data) {
                console.error("SO line not found:", soLineId);
                return;
            }

            const {order, lines: orderLines, location_id, modal_products} = data;
            this.state.modalProducts = modal_products;

            const loc = this.state.locations.find((l) => l.id === location_id);
            const firstLine = orderLines[0];

            this.state.modalMode = "edit";
            this.state.editingOrderId = order.id;
            this.state.modalData = {
                locationId: location_id,
                customerId: order.partner_id[0],
                customerSearch: order.partner_id[1],
                startDate: firstLine?.start_datetime
                    ? firstLine.start_datetime.split(" ")[0]
                    : null,
                endDate: firstLine?.end_datetime
                    ? firstLine.end_datetime.split(" ")[0]
                    : null,
                state: order.state,
                lines: [],
            };

            // Map SO lines — pricings come from modal_products (no extra RPCs)
            const modalLines = orderLines.map((line) => {
                const serviceProductId = line.product_id[0];
                const modalProduct = modal_products.find(
                    (p) => p.id === serviceProductId
                );
                const availablePeriodIds = modalProduct
                    ? modalProduct.pricings.map((p) => p.period_id)
                    : [];

                return {
                    id: line.id,
                    productId: serviceProductId,
                    rentalType: line.rental_type,
                    rentalPeriodId: line.rental_period_id
                        ? line.rental_period_id[0]
                        : null,
                    availablePeriodIds,
                    rentalQty: line.rental_qty,
                    priceUnit: line.price_unit,
                    available: modalProduct ? modalProduct.qty_available : 0,
                };
            });

            this.state.modalData.lines =
                modalLines.length > 0 ? modalLines : [this._createEmptyLine()];
            this.hideTooltip();
            this.state.showModal = true;
        } catch (error) {
            console.error("Error loading sale order:", error);
            alert("Error loading rental data. Please try again.");
        }
    }

    // ── Modal: shared ──

    _createEmptyLine() {
        return {
            id: Date.now() + Math.random(),
            productId: null,
            rentalType: "new_rental",
            rentalPeriodId: null,
            availablePeriodIds: [],
            rentalQty: 1,
            priceUnit: 0,
            available: 0,
        };
    }

    closeModal() {
        this.state.showModal = false;
        this.state.createdOrderId = null;
    }

    openEditingOrder() {
        if (!this.state.editingOrderId) return;
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: this.state.editingOrderId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async confirmEditingOrder() {
        if (!this.state.editingOrderId) return;
        try {
            await this.orm.call("sale.order", "action_confirm", [
                this.state.editingOrderId,
            ]);
            this.state.modalData.state = "sale";
            this._refreshCalendar();
            await this.loadProducts();
        } catch (error) {
            console.error("Error confirming order:", error);
            alert("Error confirming order. Please try again.");
        }
    }

    openCreatedOrder() {
        if (!this.state.createdOrderId) return;
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "sale.order",
            res_id: this.state.createdOrderId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async confirmCreatedOrder() {
        if (!this.state.createdOrderId) return;
        try {
            await this.orm.call("sale.order", "action_confirm", [
                this.state.createdOrderId,
            ]);
            this.state.showModal = false;
            this.state.createdOrderId = null;
            this._refreshCalendar();
            await this.loadProducts();
        } catch (error) {
            console.error("Error confirming order:", error);
            alert("Error confirming order. Please try again.");
        }
    }

    _formatDateForInput(date) {
        return date.toISOString().split("T")[0];
    }

    // ── Modal: field handlers ──

    async onModalLocationChange(ev) {
        this.state.modalData.locationId = ev.target.value
            ? parseInt(ev.target.value)
            : null;
        await this.loadModalProducts();
    }

    async onCustomerSearch(ev) {
        const search = ev.target.value;
        this.state.modalData.customerSearch = search;
        if (search.length >= 2) {
            this.state.customers = await this.orm.searchRead(
                "res.partner",
                ["|", ["name", "ilike", search], ["email", "ilike", search]],
                ["id", "name", "email"],
                {limit: 10}
            );
        } else {
            this.state.customers = [];
        }
    }

    selectCustomer(customer) {
        this.state.modalData.customerId = customer.id;
        this.state.modalData.customerSearch = customer.name;
        this.state.customers = [];
    }

    onModalStartDateChange(ev) {
        this.state.modalData.startDate = ev.target.value;
    }

    onModalEndDateChange(ev) {
        this.state.modalData.endDate = ev.target.value;
    }

    // ── Modal: line handlers (now synchronous — no RPC calls) ──

    onLineProductChange(line, ev) {
        const productId = ev.target.value ? parseInt(ev.target.value) : null;
        line.productId = productId;
        line.availablePeriodIds = [];
        line.rentalPeriodId = null;
        line.priceUnit = 0;

        if (productId) {
            const product = this.state.modalProducts.find((p) => p.id === productId);
            if (product) {
                line.available = product.qty_available || 0;
                line.availablePeriodIds = product.pricings.map((p) => p.period_id);
                if (line.availablePeriodIds.length > 0) {
                    line.rentalPeriodId = line.availablePeriodIds[0];
                    line.priceUnit = this._computePriceUnit(
                        productId,
                        line.rentalPeriodId
                    );
                }
            }
        }
    }

    getLineAvailablePeriods(line) {
        if (!line.availablePeriodIds || line.availablePeriodIds.length === 0) return [];
        return this.state.rentalPeriods.filter((p) =>
            line.availablePeriodIds.includes(p.id)
        );
    }

    onLineRentalTypeChange(line, ev) {
        line.rentalType = ev.target.value || "new_rental";
    }

    onLineRentalPeriodChange(line, ev) {
        line.rentalPeriodId = ev.target.value ? parseInt(ev.target.value) : null;
        if (line.productId && line.rentalPeriodId) {
            line.priceUnit = this._computePriceUnit(
                line.productId,
                line.rentalPeriodId
            );
        }
    }

    onLineRentalQtyChange(line, ev) {
        line.rentalQty = parseFloat(ev.target.value) || 1;
    }

    onLinePriceUnitChange(line, ev) {
        line.priceUnit = parseFloat(ev.target.value) || 0;
    }

    // ── Pricing (now synchronous — uses cached pricings from modalProducts) ──

    _computePriceUnit(serviceProductId, periodId) {
        if (!serviceProductId || !periodId) return 0;

        const product = this.state.modalProducts.find((p) => p.id === serviceProductId);
        if (!product) return 0;

        const pricing = product.pricings.find((p) => p.period_id === periodId);
        if (!pricing) return 0;

        const basePrice = pricing.price;
        const period = this.state.rentalPeriods.find((p) => p.id === periodId);
        if (!period) return basePrice;

        const diffHours = this._getDiffHours();
        if (diffHours <= 0) return basePrice;

        const duration = diffHours / period.hours_per_unit;
        const numberOfDays = diffHours / 24;
        return (basePrice * duration) / numberOfDays;
    }

    _getDiffHours() {
        if (!this.state.modalData.startDate || !this.state.modalData.endDate) return 0;
        const from = new Date(this.state.modalData.startDate + "T00:00:00");
        const to = new Date(this.state.modalData.endDate + "T00:00:00");
        return Math.max(0, (to - from) / (1000 * 60 * 60));
    }

    _getNumberOfDays() {
        const diffHours = this._getDiffHours();
        return diffHours > 0 ? diffHours / 24 : 1;
    }

    getLineSubtotal(line) {
        return line.priceUnit * line.rentalQty * this._getNumberOfDays();
    }

    get modalSubtotal() {
        return this.state.modalData.lines.reduce(
            (sum, line) => sum + this.getLineSubtotal(line),
            0
        );
    }

    addLine() {
        this.state.modalData.lines.push(this._createEmptyLine());
    }

    removeLine(lineId) {
        const index = this.state.modalData.lines.findIndex((l) => l.id === lineId);
        if (index > -1 && this.state.modalData.lines.length > 1) {
            this.state.modalData.lines.splice(index, 1);
        }
    }

    formatCurrency(amount) {
        return "$" + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // ── Save rental order ──

    async confirmRental() {
        const data = this.state.modalData;

        if (!data.locationId) {
            alert("Please select a location");
            return;
        }
        if (!data.customerId) {
            alert("Please select a customer");
            return;
        }
        if (!data.startDate || !data.endDate) {
            alert("Please select start and end dates");
            return;
        }

        const validLines = data.lines.filter((l) => l.productId && l.rentalQty > 0);
        if (validLines.length === 0) {
            alert("Please add at least one equipment with a rental service configured");
            return;
        }

        const loc = this.state.locations.find((l) => l.id === data.locationId);
        if (!loc) {
            alert("Invalid location");
            return;
        }

        // Server-side availability check (1 RPC replaces 2)
        const availErrors = await this.orm.call(
            "product.product",
            "check_rental_availability",
            [
                data.locationId,
                data.startDate,
                data.endDate,
                validLines.map((l) => ({
                    product_id: l.productId,
                    rental_qty: l.rentalQty,
                })),
                this.state.modalMode === "edit" ? this.state.editingOrderId : null,
            ]
        );
        if (availErrors.length > 0) {
            alert("Insufficient availability:\n\n" + availErrors.join("\n"));
            return;
        }

        const startDatetime = data.startDate + " 00:00:00";
        const endDatetime = data.endDate + " 00:00:00";
        const numberOfDays = this._getNumberOfDays();

        const lineVals = validLines.map((line) => ({
            product_id: line.productId,
            rental_type: line.rentalType,
            rental_qty: line.rentalQty,
            rental_period_id: line.rentalPeriodId,
            start_datetime: startDatetime,
            end_datetime: endDatetime,
            product_uom_qty: line.rentalQty * numberOfDays,
            price_unit: line.priceUnit,
        }));

        const orderVals = {
            partner_id: data.customerId,
            warehouse_id: loc.warehouse_id,
            lines: lineVals,
        };

        try {
            if (this.state.modalMode === "edit" && this.state.editingOrderId) {
                // Single RPC replaces N+3 calls
                await this.orm.call("sale.order.line", "update_rental_order", [
                    this.state.editingOrderId,
                    orderVals,
                ]);
            } else {
                // Single RPC replaces N+1 calls
                const orderId = await this.orm.call(
                    "sale.order.line",
                    "create_rental_order",
                    [orderVals]
                );
                this.state.createdOrderId = orderId;
            }

            this._refreshCalendar();
            await this.loadProducts();

            if (this.state.modalMode === "create" && this.state.createdOrderId) {
                this.state.modalMode = "created";
            } else {
                this.state.showModal = false;
            }
        } catch (error) {
            console.error("Error saving rental:", error);
            alert("Error saving rental. Please try again.");
        }
    }

    // ── Display helpers ──

    getAvailabilityClass(product) {
        if (product.availability_status === "available") return "bg-success";
        if (product.availability_status === "low") return "bg-warning";
        return "bg-danger";
    }

    getAvailabilityText(product) {
        const available = product.qty_available || 0;
        const total = product.qty_total;
        if (total !== undefined && total !== available) {
            return available > 0
                ? `${available} of ${total} available`
                : `0 of ${total} available`;
        }
        return available > 0 ? `${available} available` : "Unavailable";
    }

    getProductColorStyle(product) {
        const colors = [
            "#CCCCCC",
            "#F06050",
            "#F4A460",
            "#F7CD1F",
            "#6CC1ED",
            "#814968",
            "#EB7E7F",
            "#2C8397",
            "#475577",
            "#D6145F",
            "#30C381",
            "#9365B8",
        ];
        return `background-color: ${colors[product.rental_color || 0]};`;
    }

    getStatusBadgeClass(state) {
        const classes = {
            draft: "bg-secondary",
            sent: "bg-info",
            sale: "bg-primary",
            done: "bg-success",
            cancel: "bg-danger",
        };
        return classes[state] || "bg-secondary";
    }

    getStatusLabel(state) {
        const labels = {
            draft: "Quotation",
            sent: "Sent",
            sale: "Confirmed",
            done: "Done",
            cancel: "Cancelled",
        };
        return labels[state] || state;
    }

    async openCalendar() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Rental Calendar",
            res_model: "sale.order.line",
            views: [
                [false, "calendar"],
                [false, "form"],
            ],
            target: "current",
            domain: [["rental", "=", true]],
        });
    }
}

RentalDashboard.template = "rental_dashboard.RentalDashboard";
RentalDashboard.components = {View};
RentalDashboard.props = {"*": true};

registry.category("actions").add("rental_dashboard.dashboard", RentalDashboard);
