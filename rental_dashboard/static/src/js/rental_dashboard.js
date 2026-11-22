/** @odoo-module **/

import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";
import {View} from "@web/views/view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class RentalDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.ui = useService("ui");
        this.viewService = useService("view");

        this.calendarRef = useRef("calendarContainer");

        this.state = useState({
            // Filters
            selectedLocation: null,
            locationSearch: "",
            locationResults: [],
            locationHasMore: false,
            locationDropdownOpen: false,
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
            modalLocationResults: [],
            modalLocationHasMore: false,
            customers: [],
            customerHasMore: false,
            rentalPeriods: [],

            // Calendar key for re-render
            calendarKey: 0,
            viewLoaded: false,
            filtersChanged: false,

            // Applied filters — only update on applySearch / clearFilters
            appliedLocation: null,
            appliedDateFrom: null,
            appliedDateTo: null,
            appliedProducts: [],

            // Date range picker calendar state
            calendarViewYear: new Date().getFullYear(),
            calendarViewMonth: new Date().getMonth(),
            // "from" | "to"
            datePickerStep: "from",
            hoverDate: null,

            // Modal state
            showModal: false,
            modalMode: "create",
            editingOrderId: null,
            createdOrderId: null,
            modalData: {
                locationId: null,
                locationSearch: "",
                customerId: null,
                customerSearch: "",
                startDate: null,
                endDate: null,
                state: null,
                lines: [],
            },
        });

        // Pin env.config.getDisplayName to the base action name ("Rental Dashboard").
        // CalendarController builds its title as `getDisplayName() + " (Month Year)"`.
        // Without this, each navigation/remount reads the already-modified name and
        // appends another month, producing "Rental Dashboard (Feb) (March) (Feb) ...".
        if (this.env.config?.getDisplayName) {
            const baseName = this.env.config.getDisplayName();
            this.env.config.getDisplayName = () => baseName;
        }

        // Cached calendar props — rebuilt only in onMounted and applySearch so
        // the View child never receives a new object reference from unrelated renders.
        this._calendarPropsCache = null;

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

        // Debounced search handlers (prevent RPC on every keystroke)
        this._debouncedLocationSearch = this._debounce(async (search) => {
            const {results, hasMore} = await this._searchLocations(search);
            this.state.locationResults = results;
            this.state.locationHasMore = hasMore;
        });
        this._debouncedModalLocationSearch = this._debounce(async (search) => {
            const {results, hasMore} = await this._searchLocations(search);
            this.state.modalLocationResults = results;
            this.state.modalLocationHasMore = hasMore;
        });
        this._debouncedCustomerSearch = this._debounce(async (search) => {
            const {results, hasMore} = await this._searchCustomers(search);
            this.state.customers = results;
            this.state.customerHasMore = hasMore;
        });
        this._debouncedRefreshCalendar = this._debounce(() => {
            this._refreshCalendar();
        }, 150);

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
            this._calendarPropsCache = this._buildCalendarProps();
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

    _debounce(fn, delay = 300) {
        let timer = null;
        return (...args) => {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => {
                timer = null;
                fn(...args);
            }, delay);
        };
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
            if (recordId) this.openEditModal(parseInt(recordId, 10));
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
                    [["id", "=", parseInt(recordId, 10)]],
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
                location_id: this.state.appliedLocation,
                date_from: this.state.appliedDateFrom,
                date_to: this.state.appliedDateTo,
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
            {
                location_id: this.state.modalData.locationId,
                date_from: this.state.modalData.startDate || null,
                date_to: this.state.modalData.endDate || null,
            }
        );
    }

    get filteredProducts() {
        let products = this.state.products;
        if (this.state.showAvailableOnly) {
            products = products.filter((p) => p.qty_available > 0);
        }
        return products;
    }

    _buildCalendarProps() {
        const domain = [
            ["rental", "=", true],
            ["state", "not in", ["cancel"]],
        ];
        if (this.state.appliedLocation) {
            const loc = this.state.locations.find(
                (l) => l.id === this.state.appliedLocation
            );
            if (loc) domain.push(["order_id.warehouse_id", "=", loc.warehouse_id]);
        }
        if (this.state.appliedDateFrom)
            domain.push(["end_datetime", ">=", this.state.appliedDateFrom]);
        if (this.state.appliedDateTo)
            domain.push(["start_datetime", "<=", this.state.appliedDateTo]);
        if (this.state.appliedProducts.length > 0) {
            domain.push([
                "product_id.rented_product_id",
                "in",
                this.state.appliedProducts,
            ]);
        }
        return {
            resModel: "sale.order.line",
            type: "calendar",
            domain,
            context: this.props.context || {},
            display: {},
        };
    }

    get calendarProps() {
        if (!this.state.viewLoaded) return null;
        return this._calendarPropsCache;
    }

    // ── Filter actions ──

    async _searchLocations(search, limit = 20) {
        const domain = [["rental_allowed", "=", true]];
        if (search) domain.push(["rental_in_location_id.name", "ilike", search]);
        const warehouses = await this.orm.searchRead(
            "stock.warehouse",
            domain,
            ["id", "name", "rental_in_location_id", "rental_out_location_id"],
            {limit}
        );
        const results = warehouses
            .filter((wh) => wh.rental_in_location_id)
            .map((wh) => ({
                id: wh.rental_in_location_id[0],
                name: wh.rental_in_location_id[1],
                display_name: wh.name,
                warehouse_id: wh.id,
                rental_out_location_id: wh.rental_out_location_id
                    ? wh.rental_out_location_id[0]
                    : null,
            }));
        return {results, hasMore: warehouses.length === limit};
    }

    async _searchCustomers(search, limit = 20) {
        const domain = search
            ? ["|", ["name", "ilike", search], ["email", "ilike", search]]
            : [["customer_rank", ">", 0]];
        const partners = await this.orm.searchRead(
            "res.partner",
            domain,
            ["id", "name", "email"],
            {limit}
        );
        return {results: partners, hasMore: partners.length === limit};
    }

    onLocationSearchInput(ev) {
        const search = ev.target.value;
        this.state.locationSearch = search;
        if (!search) {
            this.state.selectedLocation = null;
            this.state.selectedProducts = [];
            this.state.filtersChanged = true;
        }
        this._debouncedLocationSearch(search);
    }

    async onLocationSearchFocus() {
        this.state.locationDropdownOpen = true;
        if (this.state.locationResults.length === 0) {
            const {results, hasMore} = await this._searchLocations(
                this.state.locationSearch
            );
            this.state.locationResults = results;
            this.state.locationHasMore = hasMore;
        }
    }

    onLocationSearchBlur() {
        // Delay so a click on a dropdown item registers before the dropdown closes
        setTimeout(() => {
            this.state.locationDropdownOpen = false;
        }, 200);
    }

    async loadMoreLocations() {
        const {results} = await this._searchLocations(this.state.locationSearch, 100);
        this.state.locationResults = results;
        this.state.locationHasMore = false;
    }

    selectLocation(loc) {
        this.state.selectedLocation = loc.id;
        this.state.locationSearch = loc.name;
        this.state.locationResults = [];
        this.state.locationHasMore = false;
        this.state.locationDropdownOpen = false;
        this.state.selectedProducts = [];
        this.state.filtersChanged = true;
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
        this.state.filtersChanged = true;
    }

    isProductSelected(productId) {
        return this.state.selectedProducts.includes(productId);
    }

    clearFilters() {
        this.state.selectedLocation = null;
        this.state.locationSearch = "";
        this.state.locationResults = [];
        this.state.locationHasMore = false;
        this.state.locationDropdownOpen = false;
        this.state.dateFrom = null;
        this.state.dateTo = null;
        this.state.showDatePicker = false;
        this.state.datePickerStep = "from";
        this.state.hoverDate = null;
        this.state.showAvailableOnly = false;
        this.state.selectedProducts = [];
        this.state.filtersChanged = true;
    }

    async applySearch() {
        this.state.appliedLocation = this.state.selectedLocation;
        this.state.appliedDateFrom = this.state.dateFrom;
        this.state.appliedDateTo = this.state.dateTo;
        this.state.appliedProducts = [...this.state.selectedProducts];
        this.state.filtersChanged = false;
        this._calendarPropsCache = this._buildCalendarProps();
        await this.loadProducts();
        this._debouncedRefreshCalendar();
        setTimeout(() => this.applyDateRangeHighlight(), 500);
    }

    // ── Date filter ──

    toggleDatePicker() {
        if (!this.state.showDatePicker) {
            const ref = this.state.dateFrom || null;
            const d = ref ? new Date(ref + "T00:00:00") : new Date();
            this.state.calendarViewYear = d.getFullYear();
            this.state.calendarViewMonth = d.getMonth();
            this.state.datePickerStep = "from";
            this.state.hoverDate = null;
        }
        this.state.showDatePicker = !this.state.showDatePicker;
    }

    prevMonth() {
        if (this.state.calendarViewMonth === 0) {
            this.state.calendarViewMonth = 11;
            this.state.calendarViewYear--;
        } else {
            this.state.calendarViewMonth--;
        }
    }

    nextMonth() {
        if (this.state.calendarViewMonth === 11) {
            this.state.calendarViewMonth = 0;
            this.state.calendarViewYear++;
        } else {
            this.state.calendarViewMonth++;
        }
    }

    getCalendarMonthLabel() {
        const months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ];
        return `${months[this.state.calendarViewMonth]} ${this.state.calendarViewYear}`;
    }

    getCalendarDays() {
        const year = this.state.calendarViewYear;
        const month = this.state.calendarViewMonth;
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const cells = [];
        for (let i = 0; i < firstDay; i++) {
            cells.push({key: `empty-${i}`, day: null, date: null});
        }
        for (let d = 1; d <= daysInMonth; d++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(
                d
            ).padStart(2, "0")}`;
            cells.push({key: dateStr, day: d, date: dateStr});
        }
        return cells;
    }

    _applyRangeClasses(classes, date, from, to) {
        if (from && to) {
            if (date >= from && date <= to) classes.push("rdp-in-range");
            if (date === from) classes.push("rdp-range-start");
            if (date === to) classes.push("rdp-range-end");
        } else if (from && !to) {
            if (date === from)
                classes.push("rdp-in-range", "rdp-range-start", "rdp-range-end");
        }
    }

    _applyHoverClasses(classes, date, from, to, hover, step) {
        if (step !== "to" || !from || !hover || to) return;
        const start = from <= hover ? from : hover;
        const end = from <= hover ? hover : from;
        if (date >= start && date <= end) classes.push("rdp-hover-range");
        if (date === start) classes.push("rdp-hover-start");
        if (date === end) classes.push("rdp-hover-end");
    }

    getCalendarDayClass(cell) {
        if (!cell.date) return "rdp-cell rdp-empty";
        const classes = ["rdp-cell", "rdp-day"];
        const {
            dateFrom: from,
            dateTo: to,
            hoverDate: hover,
            datePickerStep: step,
        } = this.state;
        const date = cell.date;
        this._applyRangeClasses(classes, date, from, to);
        this._applyHoverClasses(classes, date, from, to, hover, step);
        return classes.join(" ");
    }

    onCalendarDayClick(cell) {
        if (!cell.date) return;
        if (this.state.datePickerStep === "from") {
            this.state.dateFrom = cell.date;
            this.state.dateTo = null;
            this.state.hoverDate = null;
            this.state.datePickerStep = "to";
            this.state.filtersChanged = true;
        } else {
            if (cell.date < this.state.dateFrom) {
                this.state.dateTo = this.state.dateFrom;
                this.state.dateFrom = cell.date;
            } else {
                this.state.dateTo = cell.date;
            }
            this.state.datePickerStep = "from";
            this.state.hoverDate = null;
            this.state.showDatePicker = false;
            this.state.filtersChanged = true;
        }
    }

    onCalendarDayHover(cell) {
        if (this.state.datePickerStep === "to") {
            this.state.hoverDate = cell.date;
        }
    }

    onDateFromChange(ev) {
        this.state.dateFrom = ev.target.value || null;
        this.state.filtersChanged = true;
    }

    onDateToChange(ev) {
        this.state.dateTo = ev.target.value || null;
        this.state.filtersChanged = true;
    }

    applyDateFilter() {
        this.state.showDatePicker = false;
    }

    clearDateFilter() {
        this.state.dateFrom = null;
        this.state.dateTo = null;
        this.state.showDatePicker = false;
        this.state.datePickerStep = "from";
        this.state.hoverDate = null;
        this.state.filtersChanged = true;
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
        const fmt = (dateStr) => {
            const d = new Date(dateStr + "T00:00:00");
            const m = String(d.getMonth() + 1).padStart(2, "0");
            const day = String(d.getDate()).padStart(2, "0");
            return `${m}/${day}/${d.getFullYear()}`;
        };
        if (this.state.dateFrom && this.state.dateTo) {
            return `${fmt(this.state.dateFrom)} - ${fmt(this.state.dateTo)}`;
        }
        if (this.state.dateFrom) return fmt(this.state.dateFrom);
        return "";
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
        const selectedLoc = this.state.locations.find(
            (l) => l.id === this.state.selectedLocation
        );
        this.state.modalData = {
            locationId: this.state.selectedLocation,
            locationSearch: selectedLoc ? selectedLoc.name : "",
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
                    productSearch: service.name,
                    productResults: [],
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
        const selectedLoc = this.state.locations.find(
            (l) => l.id === this.state.selectedLocation
        );
        this.state.modalData = {
            locationId: this.state.selectedLocation,
            locationSearch: selectedLoc ? selectedLoc.name : "",
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
                locationSearch: loc ? loc.name : "",
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
                    productSearch: modalProduct
                        ? modalProduct.name
                        : line.product_id[1] || "",
                    productResults: [],
                    productHasMore: false,
                    rentalType: line.rental_type,
                    extensionRentalId: line.extension_rental_id
                        ? line.extension_rental_id[0]
                        : null,
                    extensionRentalSearch: line.extension_rental_id
                        ? line.extension_rental_id[1]
                        : "",
                    extensionRentalResults: [],
                    extensionRentalHasMore: false,
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
        }
    }

    // ── Modal: shared ──

    _createEmptyLine() {
        return {
            id: Date.now() + Math.random(),
            productId: null,
            productSearch: "",
            productResults: [],
            productHasMore: false,
            rentalType: "new_rental",
            extensionRentalId: null,
            extensionRentalSearch: "",
            extensionRentalResults: [],
            extensionRentalHasMore: false,
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

    async openEditingOrder() {
        if (!this.state.editingOrderId) return;
        this.ui.block();
        try {
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "sale.order",
                res_id: this.state.editingOrderId,
                views: [[false, "form"]],
                target: "current",
            });
        } finally {
            this.ui.unblock();
        }
    }

    async confirmEditingOrder() {
        if (!this.state.editingOrderId) return;
        this.ui.block();
        try {
            await this.orm.call("sale.order", "action_confirm", [
                this.state.editingOrderId,
            ]);
            this.state.modalData.state = "sale";
            this._debouncedRefreshCalendar();
            await this.loadProducts();
        } catch (error) {
            console.error("Error confirming order:", error);
        } finally {
            this.ui.unblock();
        }
    }

    async openCreatedOrder() {
        if (!this.state.createdOrderId) return;
        this.ui.block();
        try {
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "sale.order",
                res_id: this.state.createdOrderId,
                views: [[false, "form"]],
                target: "current",
            });
        } finally {
            this.ui.unblock();
        }
    }

    async confirmCreatedOrder() {
        if (!this.state.createdOrderId) return;
        this.ui.block();
        try {
            await this.orm.call("sale.order", "action_confirm", [
                this.state.createdOrderId,
            ]);
            this.state.showModal = false;
            this.state.createdOrderId = null;
            this._debouncedRefreshCalendar();
            await this.loadProducts();
        } catch (error) {
            console.error("Error confirming order:", error);
        } finally {
            this.ui.unblock();
        }
    }

    _formatDateForInput(date) {
        return date.toISOString().split("T")[0];
    }

    // ── Modal: field handlers ──

    onModalLocationSearchInput(ev) {
        const search = ev.target.value;
        this.state.modalData.locationSearch = search;
        if (!search) this.state.modalData.locationId = null;
        this._debouncedModalLocationSearch(search);
    }

    async onModalLocationSearchFocus() {
        if (this.state.modalLocationResults.length === 0) {
            const {results, hasMore} = await this._searchLocations(
                this.state.modalData.locationSearch
            );
            this.state.modalLocationResults = results;
            this.state.modalLocationHasMore = hasMore;
        }
    }

    async loadMoreModalLocations() {
        const {results} = await this._searchLocations(
            this.state.modalData.locationSearch,
            100
        );
        this.state.modalLocationResults = results;
        this.state.modalLocationHasMore = false;
    }

    selectModalLocation(loc) {
        this.state.modalData.locationId = loc.id;
        this.state.modalData.locationSearch = loc.name;
        this.state.modalLocationResults = [];
        this.state.modalLocationHasMore = false;
        this.loadModalProducts();
    }

    async onCustomerSearchFocus() {
        if (this.state.customers.length === 0) {
            const {results, hasMore} = await this._searchCustomers(
                this.state.modalData.customerSearch
            );
            this.state.customers = results;
            this.state.customerHasMore = hasMore;
        }
    }

    onCustomerSearch(ev) {
        const search = ev.target.value;
        this.state.modalData.customerSearch = search;
        if (!search) this.state.modalData.customerId = null;
        this._debouncedCustomerSearch(search);
    }

    async loadMoreCustomers() {
        const {results} = await this._searchCustomers(
            this.state.modalData.customerSearch,
            100
        );
        this.state.customers = results;
        this.state.customerHasMore = false;
    }

    selectCustomer(customer) {
        this.state.modalData.customerId = customer.id;
        this.state.modalData.customerSearch = customer.name;
        this.state.customers = [];
        this.state.customerHasMore = false;
    }

    onModalStartDateChange(ev) {
        this.state.modalData.startDate = ev.target.value;
    }

    onModalEndDateChange(ev) {
        this.state.modalData.endDate = ev.target.value;
    }

    // ── Modal: line handlers (now synchronous — no RPC calls) ──

    _applyLineProduct(line, productId) {
        line.productId = productId;
        line.availablePeriodIds = [];
        line.rentalPeriodId = null;
        line.priceUnit = 0;
        line.available = 0;

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

    _filterLineProducts(line, search, limit = 20) {
        const all = search
            ? this.state.modalProducts.filter((p) =>
                  p.name.toLowerCase().includes(search.toLowerCase())
              )
            : this.state.modalProducts;
        return {results: all.slice(0, limit), hasMore: all.length > limit};
    }

    onLineProductSearchInput(line, ev) {
        const search = ev.target.value;
        line.productSearch = search;
        if (!search) this._applyLineProduct(line, null);
        const {results, hasMore} = this._filterLineProducts(line, search);
        line.productResults = results;
        line.productHasMore = hasMore;
    }

    onLineProductSearchFocus(line) {
        if (line.productResults.length === 0) {
            const {results, hasMore} = this._filterLineProducts(
                line,
                line.productSearch
            );
            line.productResults = results;
            line.productHasMore = hasMore;
        }
    }

    loadMoreLineProducts(line) {
        const {results} = this._filterLineProducts(line, line.productSearch, 100);
        line.productResults = results;
        line.productHasMore = false;
    }

    selectLineProduct(line, product) {
        line.productSearch = product.name;
        line.productResults = [];
        line.productHasMore = false;
        this._applyLineProduct(line, product.id);
    }

    getLineAvailablePeriods(line) {
        if (!line.availablePeriodIds || line.availablePeriodIds.length === 0) return [];
        return this.state.rentalPeriods.filter((p) =>
            line.availablePeriodIds.includes(p.id)
        );
    }

    onLineRentalTypeChange(line, ev) {
        line.rentalType = ev.target.value || "new_rental";
        // Clear extension selection when switching away from extension type
        if (line.rentalType !== "rental_extension") {
            line.extensionRentalId = null;
            line.extensionRentalSearch = "";
            line.extensionRentalResults = [];
        }
    }

    // ── Extension rental typeahead ──

    async _searchRentals(productId, search, limit = 20) {
        const domain = [
            ["rental_product_id", "=", productId],
            ["state", "in", ["ordered", "out"]],
        ];
        const results = await this.orm.call(
            "sale.rental",
            "name_search",
            [search || ""],
            {
                args: domain,
                limit: limit + 1,
            }
        );
        const hasMore = results.length > limit;
        return {
            results: results.slice(0, limit).map(([id, name]) => ({id, name})),
            hasMore,
        };
    }

    async onLineExtensionSearchFocus(line) {
        if (!line.productId) return;
        const {results, hasMore} = await this._searchRentals(line.productId, "");
        line.extensionRentalResults = results;
        line.extensionRentalHasMore = hasMore;
    }

    async onLineExtensionSearchInput(line, ev) {
        const search = ev.target.value;
        line.extensionRentalSearch = search;
        if (!search) {
            line.extensionRentalId = null;
        }
        if (!line.productId) return;
        const {results, hasMore} = await this._searchRentals(line.productId, search);
        line.extensionRentalResults = results;
        line.extensionRentalHasMore = hasMore;
    }

    selectLineExtension(line, rental) {
        line.extensionRentalId = rental.id;
        line.extensionRentalSearch = rental.name;
        line.extensionRentalResults = [];
        line.extensionRentalHasMore = false;
    }

    async loadMoreLineExtensions(line) {
        if (!line.productId) return;
        const {results, hasMore} = await this._searchRentals(
            line.productId,
            line.extensionRentalSearch,
            100
        );
        line.extensionRentalResults = results;
        line.extensionRentalHasMore = hasMore;
    }

    onLineRentalPeriodChange(line, ev) {
        line.rentalPeriodId = ev.target.value ? parseInt(ev.target.value, 10) : null;
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
            this.notification.add("Please select a location", {type: "warning"});
            return;
        }
        if (!data.customerId) {
            this.notification.add("Please select a customer", {type: "warning"});
            return;
        }
        if (!data.startDate || !data.endDate) {
            this.notification.add("Please select start and end dates", {
                type: "warning",
            });
            return;
        }

        const validLines = data.lines.filter((l) => l.productId && l.rentalQty > 0);
        if (validLines.length === 0) {
            this.notification.add(
                "Please add at least one equipment with a rental service configured",
                {type: "warning"}
            );
            return;
        }

        const loc = this.state.locations.find((l) => l.id === data.locationId);
        if (!loc) {
            this.notification.add("Invalid location", {type: "warning"});
            return;
        }

        const startDatetime = data.startDate + " 00:00:00";
        const endDatetime = data.endDate + " 00:00:00";
        const diffHours = this._getDiffHours();

        const lineVals = validLines.map((line) => {
            // Mirror Python's formula (sale_order.py line 145):
            //   product_uom_qty = rental_qty * number_of_days
            // where number_of_days = duration * hours_per_unit / 24
            // and duration is stored with digits="Product Unit of Measure" (2 dp).
            // e.g. 8 days / weekly (168 h):   duration=1.14, number_of_days=7.98
            // e.g. 28 days / monthly (730 h): duration=0.92, number_of_days=27.9833...
            const period = this.state.rentalPeriods.find(
                (p) => p.id === line.rentalPeriodId
            );
            const hoursPerUnit = period ? period.hours_per_unit : 24;
            // "Product Unit of Measure" precision
            const duration = parseFloat((diffHours / hoursPerUnit).toFixed(2));
            const numberOfDays = (duration * hoursPerUnit) / 24;
            // Exact, no extra rounding — matches Python line 145
            const uomQty = line.rentalQty * numberOfDays;
            return {
                product_id: line.productId,
                rental_type: line.rentalType,
                extension_rental_id:
                    line.rentalType === "rental_extension"
                        ? line.extensionRentalId || false
                        : false,
                rental_qty: line.rentalQty,
                rental_period_id: line.rentalPeriodId,
                start_datetime: startDatetime,
                end_datetime: endDatetime,
                product_uom_qty: uomQty,
                price_unit: line.priceUnit,
            };
        });

        const orderVals = {
            partner_id: data.customerId,
            warehouse_id: loc.warehouse_id,
            lines: lineVals,
        };

        this.ui.block();
        try {
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
                this.notification.add(
                    "Insufficient availability:\n\n" + availErrors.join("\n"),
                    {type: "warning"}
                );
                return;
            }

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

            this._debouncedRefreshCalendar();
            await this.loadProducts();

            if (this.state.modalMode === "create" && this.state.createdOrderId) {
                this.state.modalMode = "created";
            } else {
                this.state.showModal = false;
            }
        } catch (error) {
            console.error("Error saving rental:", error);
        } finally {
            this.ui.unblock();
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

    getStatusBadgeStyle(state) {
        const styles = {
            draft: "background-color:#e9ecef;color:#495057;",
            sent: "background-color:#cff4fc;color:#055160;",
            sale: "background-color:#d1e7dd;color:#0f5132;",
            done: "background-color:#198754;color:#ffffff;",
            cancel: "background-color:#f8d7da;color:#842029;",
        };
        return styles[state] || "background-color:#dee2e6;color:#212529;";
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
}

RentalDashboard.template = "rental_dashboard.RentalDashboard";
RentalDashboard.components = {View};
RentalDashboard.props = {"*": true};

registry.category("actions").add("rental_dashboard.dashboard", RentalDashboard);
