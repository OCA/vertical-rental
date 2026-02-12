/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {Component, useState, onWillStart, onMounted, onWillUnmount, useRef} from "@odoo/owl";
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
            modalProducts: [], // Products filtered by modal location
            customers: [],
            rentalPeriods: [], // rental.period records

            // Calendar key for re-render
            calendarKey: 0,
            viewLoaded: false,

            // Modal state
            showModal: false,
            modalMode: 'create', // 'create', 'edit', or 'created'
            editingOrderId: null,
            createdOrderId: null,
            modalData: {
                locationId: null,
                customerId: null,
                customerSearch: '',
                startDate: null,
                endDate: null,
                state: null,
                lines: [],
            },

        });

        // Bind event handlers
        this.onCalendarClick = this.onCalendarClick.bind(this);
        this.onEventMouseOver = this.onEventMouseOver.bind(this);
        this.onEventMouseOut = this.onEventMouseOut.bind(this);

        // Tooltip tracking (plain DOM, not OWL state)
        this.tooltipTimeout = null;
        this.currentHoveredEventId = null;
        this.tooltipEl = null;

        // Track calendar cell drag for date range selection
        this.dragStartDate = null;
        this.dragEndDate = null;

        onWillStart(async () => {
            await this.loadLocations();
            await this.loadRentalPeriods();
            await this.loadProducts();
        });

        onMounted(() => {
            if (this.calendarRef.el) {
                this.calendarRef.el.addEventListener('click', this.onCalendarClick, true);
                this.calendarRef.el.addEventListener('mouseover', this.onEventMouseOver);
                this.calendarRef.el.addEventListener('mouseout', this.onEventMouseOut);

                // Track drag selection on calendar cells
                // Use elementsFromPoint to see through FC event harness overlays
                this.calendarRef.el.addEventListener('mousedown', (ev) => {
                    const elements = document.elementsFromPoint(ev.clientX, ev.clientY);
                    // Skip if clicking directly on a calendar event
                    if (elements.some(el => el.classList && el.classList.contains('fc-event') ||
                                            el.closest && el.closest('.fc-event'))) return;
                    // Find the day cell underneath
                    let date = null;
                    for (const el of elements) {
                        if (el.hasAttribute && el.hasAttribute('data-date')) {
                            date = el.getAttribute('data-date');
                            break;
                        }
                    }
                    if (date) {
                        this.dragStartDate = date;
                        this.dragEndDate = date;
                        this._isDraggingCalendar = true;
                    }
                });
                // Use mousemove + elementsFromPoint to see through FC overlay
                this._onCalendarDragMove = (ev) => {
                    if (!this._isDraggingCalendar) return;
                    const elements = document.elementsFromPoint(ev.clientX, ev.clientY);
                    for (const el of elements) {
                        if (el.hasAttribute('data-date')) {
                            this.dragEndDate = el.getAttribute('data-date');
                            break;
                        }
                    }
                };
                document.addEventListener('mousemove', this._onCalendarDragMove);
                document.addEventListener('mouseup', () => {
                    this._isDraggingCalendar = false;
                });
            }
            // Create tooltip element (plain DOM, no OWL re-render)
            this.tooltipEl = document.createElement('div');
            this.tooltipEl.className = 'rental-event-tooltip';
            this.tooltipEl.style.display = 'none';
            document.body.appendChild(this.tooltipEl);

            // Watch for calendar re-renders to apply date range highlighting
            this.highlightDebounce = null;
            this.calendarObserver = new MutationObserver(() => {
                // Debounce to avoid excessive calls during render
                if (this.highlightDebounce) clearTimeout(this.highlightDebounce);
                this.highlightDebounce = setTimeout(() => this.applyDateRangeHighlight(), 200);
            });
            if (this.calendarRef.el) {
                this.calendarObserver.observe(this.calendarRef.el, { childList: true, subtree: true });
            }

            // Watch for Odoo form dialogs opening/closing
            this.dialogObserver = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    // Intercept dialog OPENING: redirect to our modal
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === 1) {
                            const isDialog = node.classList?.contains('o_dialog') ||
                                node.classList?.contains('modal') ||
                                node.querySelector?.('.o_form_view') ||
                                node.querySelector?.('.modal-dialog');
                            if (isDialog && this.dragStartDate) {
                                // Close the Odoo dialog
                                const closeBtn = node.querySelector('.btn-close, .o_form_button_cancel, .close');
                                if (closeBtn) {
                                    closeBtn.click();
                                } else {
                                    node.remove();
                                }
                                // Open our modal with the dragged dates
                                const startDate = this.dragStartDate;
                                const endDate = this.dragEndDate || this.dragStartDate;
                                // Ensure start <= end
                                const sortedStart = startDate < endDate ? startDate : endDate;
                                const sortedEnd = startDate < endDate ? endDate : startDate;
                                this.dragStartDate = null;
                                this.dragEndDate = null;
                                this.openCreateModalWithDates(sortedStart, sortedEnd);
                                return;
                            }
                        }
                    }
                    // Dialog CLOSING: reload products
                    for (const node of mutation.removedNodes) {
                        if (node.nodeType === 1) {
                            const isDialog = node.classList?.contains('o_dialog') ||
                                node.classList?.contains('o_technical_modal') ||
                                node.classList?.contains('modal') ||
                                node.classList?.contains('o_FormViewDialog') ||
                                node.querySelector?.('.o_form_view') ||
                                node.querySelector?.('.modal-dialog');
                            if (isDialog) {
                                setTimeout(() => this.loadProducts(), 300);
                            }
                        }
                    }
                }
            });
            this.dialogObserver.observe(document.body, { childList: true, subtree: true });

            this.state.viewLoaded = true;
        });

        onWillUnmount(() => {
            if (this.calendarRef.el) {
                this.calendarRef.el.removeEventListener('click', this.onCalendarClick, true);
                this.calendarRef.el.removeEventListener('mouseover', this.onEventMouseOver);
                this.calendarRef.el.removeEventListener('mouseout', this.onEventMouseOut);
            }
            if (this.calendarObserver) {
                this.calendarObserver.disconnect();
            }
            if (this.dialogObserver) {
                this.dialogObserver.disconnect();
            }
            if (this.tooltipEl) {
                this.tooltipEl.remove();
            }
            if (this.tooltipTimeout) {
                clearTimeout(this.tooltipTimeout);
            }
        });
    }

    onCalendarClick(ev) {
        this.hideTooltip();

        // If clicking "+n more" link, let FC handle it
        if (ev.target.closest('.fc-more-link, .fc-daygrid-more-link, .fc-more')) {
            return;
        }

        // Find if click was on a calendar event
        const eventEl = ev.target.closest('.fc-event');
        if (eventEl) {
            // Stop the event from reaching the calendar's handler
            ev.stopPropagation();
            ev.preventDefault();

            // Try multiple ways to get the record ID
            let recordId = null;

            // Method 1: Check data attribute
            recordId = eventEl.dataset.eventId || eventEl.getAttribute('data-event-id');

            // Method 2: Try FullCalendar's internal data structure
            if (!recordId && eventEl.fcSeg) {
                const fcEvent = eventEl.fcSeg.eventRange?.def;
                recordId = fcEvent?.publicId || fcEvent?.extendedProps?.recordId;
            }

            // Method 3: Look for fc-event link with href containing the ID
            if (!recordId) {
                const link = eventEl.querySelector('a[href*="id="]');
                if (link) {
                    const match = link.href.match(/id=(\d+)/);
                    if (match) recordId = match[1];
                }
            }

            // Method 4: Check the event's title element for data
            if (!recordId) {
                const eventData = eventEl.__data__ || eventEl._fc_event;
                if (eventData) {
                    recordId = eventData.id || eventData.publicId;
                }
            }

            if (recordId) {
                this.openEditModal(parseInt(recordId));
            }
        }
    }

    onEventMouseOver(ev) {
        const eventEl = ev.target.closest('.fc-event');
        if (!eventEl) return;

        if (this.state.showModal) return;

        let recordId = eventEl.dataset.eventId || eventEl.getAttribute('data-event-id');
        if (!recordId && eventEl.fcSeg) {
            const fcEvent = eventEl.fcSeg.eventRange?.def;
            recordId = fcEvent?.publicId || fcEvent?.extendedProps?.recordId;
        }

        if (!recordId) return;

        // Already showing for this event
        if (this.currentHoveredEventId === recordId && this.tooltipEl.style.display !== 'none') {
            return;
        }

        if (this.tooltipTimeout) {
            clearTimeout(this.tooltipTimeout);
            this.tooltipTimeout = null;
        }

        this.currentHoveredEventId = recordId;

        this.orm.searchRead(
            "sale.order.line",
            [["id", "=", parseInt(recordId)]],
            ["id", "product_id", "start_datetime", "end_datetime", "order_partner_id", "order_id", "rental_qty", "state"]
        ).then(([soLine]) => {
            if (this.currentHoveredEventId !== recordId) return;
            if (this.state.showModal) return;

            if (soLine) {
                const rect = eventEl.getBoundingClientRect();
                const productName = soLine.product_id ? soLine.product_id[1] : 'No product';
                const startDate = this.formatTooltipDate(soLine.start_datetime);
                const endDate = this.formatTooltipDate(soLine.end_datetime);
                const customer = soLine.order_partner_id ? soLine.order_partner_id[1] : 'No customer';
                const orderName = soLine.order_id ? soLine.order_id[1] : '';

                this.tooltipEl.innerHTML = `
                    <div class="tooltip-content">
                        <div class="tooltip-title fw-bold mb-2">${_.escape(productName)}</div>
                        <div class="tooltip-dates mb-2">${_.escape(startDate)} - ${_.escape(endDate)}</div>
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
                this.tooltipEl.style.left = (rect.left + rect.width / 2) + 'px';
                this.tooltipEl.style.top = (rect.top - 10) + 'px';
                this.tooltipEl.style.display = '';
            }
        });
    }

    onEventMouseOut(ev) {
        const eventEl = ev.target.closest('.fc-event');
        if (!eventEl) return;

        const relatedTarget = ev.relatedTarget;
        if (relatedTarget && eventEl.contains(relatedTarget)) {
            return;
        }

        this.tooltipTimeout = setTimeout(() => {
            if (this.tooltipEl) this.tooltipEl.style.display = 'none';
            this.currentHoveredEventId = null;
        }, 100);
    }

    hideTooltip() {
        if (this.tooltipTimeout) {
            clearTimeout(this.tooltipTimeout);
        }
        if (this.tooltipEl) this.tooltipEl.style.display = 'none';
        this.currentHoveredEventId = null;
    }

    formatTooltipDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const year = String(date.getFullYear()).slice(-2);
        return `${month}/${day}/${year}`;
    }

    async loadRentalPeriods() {
        this.state.rentalPeriods = await this.orm.searchRead(
            "rental.period",
            [["active", "=", true]],
            ["id", "name", "code", "hours_per_unit"],
            {order: "sequence, id"}
        );
    }

    async loadLocations() {
        // Load only rental_in locations from rental-enabled warehouses
        const warehouses = await this.orm.searchRead(
            "stock.warehouse",
            [["rental_allowed", "=", true]],
            ["id", "name", "rental_in_location_id", "rental_out_location_id"]
        );
        this.state.warehouses = warehouses;
        this.state.locations = warehouses.map(wh => ({
            id: wh.rental_in_location_id[0],
            name: wh.rental_in_location_id[1],
            display_name: wh.name,
            rental_out_location_id: wh.rental_out_location_id[0],
            warehouse_id: wh.id,
        }));
    }

    async loadProducts() {
        // Physical products that have a rental service linked
        const domain = [["rental_service_ids", "!=", false]];

        // Collect rental_in and rental_out location IDs
        let rentalInIds = [];
        let rentalOutIds = [];

        if (this.state.selectedLocation) {
            // Single selected rental_in location
            rentalInIds = [this.state.selectedLocation];
            const loc = this.state.locations.find(l => l.id === this.state.selectedLocation);
            rentalOutIds = loc ? [loc.rental_out_location_id] : [];
        } else {
            // All rental locations
            rentalInIds = this.state.locations.map(l => l.id);
            rentalOutIds = this.state.locations.map(l => l.rental_out_location_id);
        }

        const allLocationIds = [...rentalInIds, ...rentalOutIds];

        // Get stock at rental locations
        const quants = await this.orm.searchRead(
            "stock.quant",
            [
                ["location_id", "in", allLocationIds],
                ["quantity", ">", 0],
            ],
            ["product_id", "quantity", "location_id"]
        );
        // Build maps: rental_in qty (available) and total qty (rental_in + rental_out)
        const rentalInQtyMap = {};
        const totalQtyMap = {};
        quants.forEach(q => {
            const pid = q.product_id[0];
            const qty = q.quantity;
            totalQtyMap[pid] = (totalQtyMap[pid] || 0) + qty;
            if (rentalInIds.includes(q.location_id[0])) {
                rentalInQtyMap[pid] = (rentalInQtyMap[pid] || 0) + qty;
            }
        });


        // Get committed rental qty from active sale.rental records
        // "ordered" = confirmed but not yet picked from rental_in
        // Filter by out_picking_id.location_id to match selected location(s)
        // Filter by date range overlap if dates are selected
        const rentalDomain = [["state", "=", "ordered"]];
        if (rentalInIds.length > 0) {
            rentalDomain.push(["out_picking_id.location_id", "in", rentalInIds]);
        }
        if (this.state.dateFrom) {
            rentalDomain.push(["start_datetime", "<=", this.state.dateTo || this.state.dateFrom]);
        }
        if (this.state.dateTo) {
            rentalDomain.push(["end_datetime", ">=", this.state.dateFrom || this.state.dateTo]);
        }
        const rentals = await this.orm.searchRead(
            "sale.rental",
            rentalDomain,
            ["rented_product_id", "rental_qty"]
        );
        const committedQtyMap = {};
        rentals.forEach(r => {
            const pid = r.rented_product_id[0];
            committedQtyMap[pid] = (committedQtyMap[pid] || 0) + r.rental_qty;
        });

        // If location selected, filter to products with stock at those locations
        const productIdsAtLocation = Object.keys(totalQtyMap).map(Number);
        if (this.state.selectedLocation) {
            if (productIdsAtLocation.length > 0) {
                domain.push(["id", "in", productIdsAtLocation]);
            } else {
                this.state.products = [];
                return;
            }
        }

        const products = await this.orm.searchRead(
            "product.product",
            domain,
            ["id", "name", "default_code", "rental_color"]
        );

        // qty_total = rental_in + rental_out (total fleet)
        // qty_available = rental_in - committed rental qty (truly available)
        products.forEach(p => {
            p.qty_total = totalQtyMap[p.id] || 0;
            const rentalInQty = rentalInQtyMap[p.id] || 0;
            const committed = committedQtyMap[p.id] || 0;
            p.qty_available = Math.max(0, rentalInQty - committed);

            if (p.qty_available > 5) {
                p.availability_status = 'available';
            } else if (p.qty_available > 0) {
                p.availability_status = 'low';
            } else {
                p.availability_status = 'unavailable';
            }
        });
        this.state.products = products;
    }

    async loadModalProducts() {
        const locationId = this.state.modalData.locationId;

        // Determine rental_in location(s)
        let rentalInIds = [];
        if (locationId) {
            rentalInIds = [locationId];
        } else {
            rentalInIds = this.state.locations.map(l => l.id);
        }

        // Get stock at rental_in location(s) for physical products
        const quants = await this.orm.searchRead(
            "stock.quant",
            [
                ["location_id", "in", rentalInIds],
                ["quantity", ">", 0],
            ],
            ["product_id", "quantity"]
        );
        const rentalInQtyMap = {};
        quants.forEach(q => {
            const pid = q.product_id[0];
            rentalInQtyMap[pid] = (rentalInQtyMap[pid] || 0) + q.quantity;
        });

        // Get committed rental qty filtered by location
        const rentalDomain = [["state", "=", "ordered"]];
        if (rentalInIds.length > 0) {
            rentalDomain.push(["out_picking_id.location_id", "in", rentalInIds]);
        }
        const rentals = await this.orm.searchRead(
            "sale.rental",
            rentalDomain,
            ["rented_product_id", "rental_qty"]
        );
        const committedQtyMap = {};
        rentals.forEach(r => {
            const pid = r.rented_product_id[0];
            committedQtyMap[pid] = (committedQtyMap[pid] || 0) + r.rental_qty;
        });

        // Load physical products to get their rental_service_ids
        const physicalDomain = [["rental_service_ids", "!=", false]];
        if (locationId) {
            const productIdsAtLocation = Object.keys(rentalInQtyMap).map(Number);
            if (productIdsAtLocation.length > 0) {
                physicalDomain.push(["id", "in", productIdsAtLocation]);
            } else {
                this.state.modalProducts = [];
                return;
            }
        }

        const physicalProducts = await this.orm.searchRead(
            "product.product",
            physicalDomain,
            ["id", "name", "rental_service_ids"]
        );

        // Build availability map for physical products
        const availMap = {};
        physicalProducts.forEach(p => {
            const rentalInQty = rentalInQtyMap[p.id] || 0;
            const committed = committedQtyMap[p.id] || 0;
            availMap[p.id] = Math.max(0, rentalInQty - committed);
        });

        // Collect all rental service IDs
        const allServiceIds = [];
        physicalProducts.forEach(p => {
            allServiceIds.push(...p.rental_service_ids);
        });

        if (allServiceIds.length === 0) {
            this.state.modalProducts = [];
            return;
        }

        // Load service products
        const serviceProducts = await this.orm.searchRead(
            "product.product",
            [["id", "in", allServiceIds]],
            ["id", "name", "rented_product_id"]
        );

        // Attach physical product availability to each service product
        serviceProducts.forEach(sp => {
            const physicalId = sp.rented_product_id ? sp.rented_product_id[0] : null;
            sp.physicalProductId = physicalId;
            sp.qty_available = physicalId ? (availMap[physicalId] || 0) : 0;
        });

        this.state.modalProducts = serviceProducts;
    }

    get filteredProducts() {
        let products = this.state.products;

        if (this.state.showAvailableOnly) {
            products = products.filter(p => p.qty_available > 0);
        }

        return products;
    }

    get calendarDomain() {
        // Only rental SO lines, exclude cancelled orders
        const domain = [
            ["rental", "=", true],
            ["state", "not in", ["cancel"]],
        ];

        // Filter by warehouse matching the selected rental_in location
        if (this.state.selectedLocation) {
            const loc = this.state.locations.find(l => l.id === this.state.selectedLocation);
            if (loc) {
                domain.push(["order_id.warehouse_id", "=", loc.warehouse_id]);
            }
        }

        // Filter by date range (overlapping)
        if (this.state.dateFrom) {
            domain.push(["end_datetime", ">=", this.state.dateFrom]);
        }
        if (this.state.dateTo) {
            domain.push(["start_datetime", "<=", this.state.dateTo]);
        }

        // Filter by selected products (physical) via rental_service_ids
        if (this.state.selectedProducts.length > 0) {
            domain.push(["product_id.rented_product_id", "in", this.state.selectedProducts]);
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
            display: {
                // controlPanel: false,
            },
        };
    }


    // Actions
    async onLocationChange(ev) {
        const value = ev.target.value;
        this.state.selectedLocation = value ? parseInt(value) : null;
        this.state.selectedProducts = []; // Clear product selection when location changes
        await this.loadProducts(); // Reload products for new location
        this.state.calendarKey++; // Force calendar re-render
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
        this.state.calendarKey++; // Force calendar re-render
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
        await this.loadProducts(); // Reload all products
        this.state.calendarKey++;
    }

    // Date filter functions
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
        this.state.calendarKey++;
        await this.loadProducts(); // Recalculate availability based on date range
        // Delay to let calendar re-render, then highlight
        setTimeout(() => this.applyDateRangeHighlight(), 500);
    }

    async clearDateFilter() {
        this.state.dateFrom = null;
        this.state.dateTo = null;
        this.state.showDatePicker = false;
        this.state.calendarKey++;
        await this.loadProducts(); // Recalculate availability
        this.applyDateRangeHighlight();
    }

    applyDateRangeHighlight() {
        if (!this.calendarRef.el) return;

        // Try multiple selectors for different FullCalendar versions
        let dayCells = this.calendarRef.el.querySelectorAll('.fc-daygrid-day[data-date]');
        if (!dayCells.length) {
            dayCells = this.calendarRef.el.querySelectorAll('td[data-date]');
        }
        if (!dayCells.length) {
            dayCells = this.calendarRef.el.querySelectorAll('.fc-day[data-date]');
        }
        if (!dayCells.length) return;

        // Remove existing classes first
        dayCells.forEach(cell => {
            cell.classList.remove('date-in-range', 'date-outside-range');
        });

        // If no date range selected, don't highlight anything
        if (!this.state.dateFrom || !this.state.dateTo) return;

        const fromDate = new Date(this.state.dateFrom + 'T00:00:00');
        const toDate = new Date(this.state.dateTo + 'T23:59:59');

        dayCells.forEach(cell => {
            const dateAttr = cell.getAttribute('data-date');
            if (!dateAttr) return;

            const cellDate = new Date(dateAttr + 'T12:00:00');

            if (cellDate >= fromDate && cellDate <= toDate) {
                cell.classList.add('date-in-range');
            } else {
                cell.classList.add('date-outside-range');
            }
        });
    }

    formatDateRange() {
        if (!this.state.dateFrom || !this.state.dateTo) return '';

        const from = new Date(this.state.dateFrom);
        const to = new Date(this.state.dateTo);

        // Calculate days difference
        const diffTime = Math.abs(to - from);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

        // Format dates as M/D/YY
        const formatDate = (date) => {
            const month = date.getMonth() + 1;
            const day = date.getDate();
            const year = String(date.getFullYear()).slice(-2);
            return `${month}/${day}/${year}`;
        };

        return `${formatDate(from)} - ${formatDate(to)} (${diffDays} days)`;
    }

    // Modal functions
    async openCreateModal() {
        this.state.modalMode = 'create';
        this.state.editingOrderId = null;
        this.state.modalData = {
            locationId: this.state.selectedLocation,
            customerId: null,
            customerSearch: '',
            startDate: this.state.dateFrom || this.formatDateForInput(new Date()),
            endDate: this.state.dateTo || this.formatDateForInput(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)),
            state: null,
            lines: [],
        };

        await this.loadModalProducts();

        // Initialize lines from pre-selected physical products (sidebar)
        // Map physical product IDs to their service products
        const lines = [];
        if (this.state.selectedProducts.length > 0) {
            for (const physicalId of this.state.selectedProducts) {
                // Find the first service product for this physical product
                const service = this.state.modalProducts.find(p => p.physicalProductId === physicalId);
                if (service) {
                    // Load available periods from product.rental.pricing
                    const pricings = await this.orm.searchRead(
                        "product.rental.pricing",
                        [["product_id", "=", service.id]],
                        ["period_id"]
                    );
                    const availablePeriodIds = pricings.map(p => p.period_id[0]);
                    const rentalPeriodId = availablePeriodIds.length > 0 ? availablePeriodIds[0] : null;
                    const priceUnit = rentalPeriodId ? await this.computePriceUnit(service.id, rentalPeriodId) : 0;

                    lines.push({
                        id: Date.now() + Math.random(),
                        productId: service.id,
                        rentalType: 'new_rental',
                        rentalPeriodId: rentalPeriodId,
                        availablePeriodIds: availablePeriodIds,
                        rentalQty: 1,
                        priceUnit: priceUnit,
                        available: service.qty_available || 0,
                    });
                }
            }
        }

        this.state.modalData.lines = lines.length > 0 ? lines : [this.createEmptyLine()];

        this.hideTooltip();
        this.state.showModal = true;
    }

    async openCreateModalWithDates(startDate, endDate) {
        this.state.modalMode = 'create';
        this.state.editingOrderId = null;
        this.state.modalData = {
            locationId: this.state.selectedLocation,
            customerId: null,
            customerSearch: '',
            startDate: startDate,
            endDate: endDate,
            state: null,
            lines: [],
        };

        await this.loadModalProducts();
        this.state.modalData.lines = [this.createEmptyLine()];

        this.hideTooltip();
        this.state.showModal = true;
    }

    async openEditModal(soLineId) {
        try {
            // Load the SO line to get order_id
            const [soLine] = await this.orm.searchRead(
                "sale.order.line",
                [["id", "=", soLineId]],
                ["order_id"]
            );
            if (!soLine) {
                console.error("SO line not found:", soLineId);
                return;
            }

            const orderId = soLine.order_id[0];

            // Load the sale order
            const [order] = await this.orm.searchRead(
                "sale.order",
                [["id", "=", orderId]],
                ["id", "partner_id", "warehouse_id", "state"]
            );
            if (!order) {
                console.error("Sale order not found:", orderId);
                return;
            }

            // Find location from warehouse
            const loc = this.state.locations.find(l => l.warehouse_id === order.warehouse_id[0]);

            // Load all rental SO lines for this order
            const orderLines = await this.orm.searchRead(
                "sale.order.line",
                [["order_id", "=", orderId], ["rental", "=", true]],
                ["id", "product_id", "rental_type", "rental_period_id", "rental_qty",
                 "price_unit", "start_datetime", "end_datetime"]
            );

            // Use dates from first line
            const firstLine = orderLines[0];
            const startDt = firstLine ? firstLine.start_datetime : null;
            const endDt = firstLine ? firstLine.end_datetime : null;

            // Set up modal data (need locationId for loadModalProducts)
            this.state.modalMode = 'edit';
            this.state.editingOrderId = orderId;
            this.state.modalData = {
                locationId: loc ? loc.id : null,
                customerId: order.partner_id[0],
                customerSearch: order.partner_id[1],
                startDate: startDt ? startDt.split(' ')[0] : null,
                endDate: endDt ? endDt.split(' ')[0] : null,
                state: order.state,
                lines: [],
            };

            await this.loadModalProducts();

            // Map SO lines: product_id is the service product directly
            const lines = [];
            for (const line of orderLines) {
                const serviceProductId = line.product_id[0];
                const modalProduct = this.state.modalProducts.find(p => p.id === serviceProductId);

                // Load available periods from product.rental.pricing
                const pricings = await this.orm.searchRead(
                    "product.rental.pricing",
                    [["product_id", "=", serviceProductId]],
                    ["period_id"]
                );

                lines.push({
                    id: line.id,
                    productId: serviceProductId,
                    rentalType: line.rental_type,
                    rentalPeriodId: line.rental_period_id ? line.rental_period_id[0] : null,
                    availablePeriodIds: pricings.map(p => p.period_id[0]),
                    rentalQty: line.rental_qty,
                    priceUnit: line.price_unit,
                    available: modalProduct ? modalProduct.qty_available : 0,
                });
            }

            this.state.modalData.lines = lines.length > 0 ? lines : [this.createEmptyLine()];

            this.hideTooltip();
            this.state.showModal = true;

        } catch (error) {
            console.error("Error loading sale order:", error);
            alert("Error loading rental data. Please try again.");
        }
    }

    createEmptyLine() {
        return {
            id: Date.now() + Math.random(),
            productId: null,       // service product ID (sale.order.line.product_id)
            rentalType: 'new_rental',
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
            await this.orm.call("sale.order", "action_confirm", [this.state.editingOrderId]);
            this.state.modalData.state = 'sale';
            this.state.calendarKey++;
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
            await this.orm.call("sale.order", "action_confirm", [this.state.createdOrderId]);
            this.state.showModal = false;
            this.state.createdOrderId = null;
            this.state.calendarKey++;
            await this.loadProducts();
        } catch (error) {
            console.error("Error confirming order:", error);
            alert("Error confirming order. Please try again.");
        }
    }

    formatDateForInput(date) {
        return date.toISOString().split('T')[0];
    }

    async onModalLocationChange(ev) {
        this.state.modalData.locationId = ev.target.value ? parseInt(ev.target.value) : null;
        // Reload products for the new location
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

    async onLineProductChange(line, ev) {
        const productId = ev.target.value ? parseInt(ev.target.value) : null;
        line.productId = productId;
        line.availablePeriodIds = [];
        line.rentalPeriodId = null;
        line.priceUnit = 0;

        if (productId) {
            const product = this.state.modalProducts.find(p => p.id === productId);
            if (product) {
                line.available = product.qty_available || 0;

                // Load available periods from product.rental.pricing
                const pricings = await this.orm.searchRead(
                    "product.rental.pricing",
                    [["product_id", "=", productId]],
                    ["period_id"]
                );
                line.availablePeriodIds = pricings.map(p => p.period_id[0]);

                // Auto-select first available period
                if (line.availablePeriodIds.length > 0) {
                    line.rentalPeriodId = line.availablePeriodIds[0];
                    line.priceUnit = await this.computePriceUnit(productId, line.rentalPeriodId);
                }
            }
        }
    }

    getLineAvailablePeriods(line) {
        if (!line.availablePeriodIds || line.availablePeriodIds.length === 0) {
            return [];
        }
        return this.state.rentalPeriods.filter(p => line.availablePeriodIds.includes(p.id));
    }

    onLineRentalTypeChange(line, ev) {
        line.rentalType = ev.target.value || 'new_rental';
    }

    async onLineRentalPeriodChange(line, ev) {
        line.rentalPeriodId = ev.target.value ? parseInt(ev.target.value) : null;
        if (line.productId && line.rentalPeriodId) {
            line.priceUnit = await this.computePriceUnit(line.productId, line.rentalPeriodId);
        }
    }

    onLineRentalQtyChange(line, ev) {
        line.rentalQty = parseFloat(ev.target.value) || 1;
    }

    onLinePriceUnitChange(line, ev) {
        line.priceUnit = parseFloat(ev.target.value) || 0;
    }

    async computePriceUnit(serviceProductId, periodId) {
        if (!serviceProductId || !periodId) return 0;

        // Get base price per period from product.rental.pricing
        const [pricing] = await this.orm.searchRead(
            "product.rental.pricing",
            [["product_id", "=", serviceProductId], ["period_id", "=", periodId]],
            ["price"]
        );
        if (!pricing) return 0;

        const basePrice = pricing.price;
        const period = this.state.rentalPeriods.find(p => p.id === periodId);
        if (!period) return basePrice;

        // Match sale_rental _compute_price_unit:
        // duration = diff_hours / hours_per_unit
        // number_of_days = diff_hours / 24
        // price_unit = (base_price * duration) / number_of_days
        const diffHours = this.getDiffHours();
        if (diffHours <= 0) return basePrice;

        const duration = diffHours / period.hours_per_unit;
        const numberOfDays = diffHours / 24;
        return (basePrice * duration) / numberOfDays;
    }

    getDiffHours() {
        if (!this.state.modalData.startDate || !this.state.modalData.endDate) return 0;
        const from = new Date(this.state.modalData.startDate + 'T00:00:00');
        const to = new Date(this.state.modalData.endDate + 'T00:00:00');
        return Math.max(0, (to - from) / (1000 * 60 * 60));
    }

    getNumberOfDays() {
        const diffHours = this.getDiffHours();
        return diffHours > 0 ? diffHours / 24 : 1;
    }

    getLineSubtotal(line) {
        // Match sale_rental: price_subtotal = price_unit * product_uom_qty
        // where product_uom_qty = rental_qty * number_of_days
        return line.priceUnit * line.rentalQty * this.getNumberOfDays();
    }

    getLineTotal(line) {
        return this.getLineSubtotal(line);
    }

    get modalSubtotal() {
        return this.state.modalData.lines.reduce((sum, line) => sum + this.getLineSubtotal(line), 0);
    }

    get modalTotal() {
        return this.modalSubtotal;
    }

    addLine() {
        this.state.modalData.lines.push(this.createEmptyLine());
    }

    removeLine(lineId) {
        const index = this.state.modalData.lines.findIndex(l => l.id === lineId);
        if (index > -1 && this.state.modalData.lines.length > 1) {
            this.state.modalData.lines.splice(index, 1);
        }
    }

    formatCurrency(amount) {
        return '$' + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    async checkAvailability(validLines, locationId, startDate, endDate) {
        const rentalInIds = [locationId];

        // Get stock at rental_in location
        const quants = await this.orm.searchRead(
            "stock.quant",
            [["location_id", "in", rentalInIds], ["quantity", ">", 0]],
            ["product_id", "quantity"]
        );
        const rentalInQtyMap = {};
        quants.forEach(q => {
            const pid = q.product_id[0];
            rentalInQtyMap[pid] = (rentalInQtyMap[pid] || 0) + q.quantity;
        });

        // Get committed rentals overlapping with the date range
        const rentalDomain = [
            ["state", "=", "ordered"],
            ["out_picking_id.location_id", "in", rentalInIds],
            ["start_datetime", "<=", endDate + " 00:00:00"],
            ["end_datetime", ">=", startDate + " 00:00:00"],
        ];
        // Exclude current order when editing
        if (this.state.modalMode === 'edit' && this.state.editingOrderId) {
            rentalDomain.push(["start_order_id", "!=", this.state.editingOrderId]);
        }
        const rentals = await this.orm.searchRead(
            "sale.rental",
            rentalDomain,
            ["rented_product_id", "rental_qty"]
        );
        const committedQtyMap = {};
        rentals.forEach(r => {
            const pid = r.rented_product_id[0];
            committedQtyMap[pid] = (committedQtyMap[pid] || 0) + r.rental_qty;
        });

        // Check each line: find physical product via modalProducts, then check availability
        // Also aggregate qty per physical product across lines
        const requestedQtyMap = {};
        for (const line of validLines) {
            const modalProduct = this.state.modalProducts.find(p => p.id === line.productId);
            const physicalId = modalProduct ? modalProduct.physicalProductId : null;
            if (physicalId) {
                requestedQtyMap[physicalId] = (requestedQtyMap[physicalId] || 0) + line.rentalQty;
            }
        }

        const errors = [];
        for (const [physicalId, requestedQty] of Object.entries(requestedQtyMap)) {
            const rentalInQty = rentalInQtyMap[physicalId] || 0;
            const committed = committedQtyMap[physicalId] || 0;
            const available = Math.max(0, rentalInQty - committed);
            if (requestedQty > available) {
                // Find product name from modal products
                const product = this.state.modalProducts.find(p => p.physicalProductId === parseInt(physicalId));
                const name = product ? product.name : 'Unknown';
                errors.push(`${name}: requested ${requestedQty}, available ${available}`);
            }
        }

        return errors;
    }

    async confirmRental() {
        const data = this.state.modalData;

        // Validation
        if (!data.locationId) {
            alert('Please select a location');
            return;
        }
        if (!data.customerId) {
            alert('Please select a customer');
            return;
        }
        if (!data.startDate || !data.endDate) {
            alert('Please select start and end dates');
            return;
        }

        const validLines = data.lines.filter(l => l.productId && l.rentalQty > 0);
        if (validLines.length === 0) {
            alert('Please add at least one equipment with a rental service configured');
            return;
        }

        // Get warehouse from selected location
        const loc = this.state.locations.find(l => l.id === data.locationId);
        if (!loc) {
            alert('Invalid location');
            return;
        }

        // Check availability before saving
        const availErrors = await this.checkAvailability(validLines, data.locationId, data.startDate, data.endDate);
        if (availErrors.length > 0) {
            alert('Insufficient availability:\n\n' + availErrors.join('\n'));
            return;
        }

        const startDatetime = data.startDate + ' 00:00:00';
        const endDatetime = data.endDate + ' 00:00:00';
        const diffHours = this.getDiffHours();
        const numberOfDays = diffHours / 24;

        try {
            if (this.state.modalMode === 'edit' && this.state.editingOrderId) {
                // Update existing SO (only if draft)
                await this.orm.write("sale.order", [this.state.editingOrderId], {
                    partner_id: data.customerId,
                    warehouse_id: loc.warehouse_id,
                });

                // Delete old rental lines and create new ones
                const oldLines = await this.orm.searchRead(
                    "sale.order.line",
                    [["order_id", "=", this.state.editingOrderId], ["rental", "=", true]],
                    ["id"]
                );
                if (oldLines.length > 0) {
                    await this.orm.unlink("sale.order.line", oldLines.map(l => l.id));
                }

                for (const line of validLines) {
                    await this.orm.create("sale.order.line", [{
                        order_id: this.state.editingOrderId,
                        product_id: line.productId,
                        rental: true,
                        rental_type: line.rentalType,
                        rental_qty: line.rentalQty,
                        rental_period_id: line.rentalPeriodId,
                        start_datetime: startDatetime,
                        end_datetime: endDatetime,
                        product_uom_qty: line.rentalQty * numberOfDays,
                        price_unit: line.priceUnit,
                    }]);
                }

            } else {
                // Create new sale order
                const orderId = await this.orm.create("sale.order", [{
                    partner_id: data.customerId,
                    warehouse_id: loc.warehouse_id,
                }]);
                this.state.createdOrderId = orderId;

                // Create SO lines
                for (const line of validLines) {
                    await this.orm.create("sale.order.line", [{
                        order_id: orderId,
                        product_id: line.productId,
                        rental: true,
                        rental_type: line.rentalType,
                        rental_qty: line.rentalQty,
                        rental_period_id: line.rentalPeriodId,
                        start_datetime: startDatetime,
                        end_datetime: endDatetime,
                        product_uom_qty: line.rentalQty * numberOfDays,
                        price_unit: line.priceUnit,
                    }]);
                }

            }

            // Refresh calendar and products
            this.state.calendarKey++;
            await this.loadProducts();

            if (this.state.modalMode === 'create' && this.state.createdOrderId) {
                // Show success state with action buttons
                this.state.modalMode = 'created';
            } else {
                this.state.showModal = false;
            }

        } catch (error) {
            console.error('Error saving rental:', error);
            alert('Error saving rental. Please try again.');
        }
    }

    getAvailabilityClass(product) {
        if (product.availability_status === 'available') return 'bg-success';
        if (product.availability_status === 'low') return 'bg-warning';
        return 'bg-danger';
    }

    getAvailabilityText(product) {
        const available = product.qty_available || 0;
        const total = product.qty_total;
        if (total !== undefined && total !== available) {
            if (available > 0) return `${available} of ${total} available`;
            return `0 of ${total} available`;
        }
        if (available > 0) return `${available} available`;
        return 'Unavailable';
    }

    getProductColorStyle(product) {
        const colors = ['#CCCCCC', '#F06050', '#F4A460', '#F7CD1F', '#6CC1ED', '#814968', '#EB7E7F', '#2C8397', '#475577', '#D6145F', '#30C381', '#9365B8'];
        const color = colors[product.rental_color || 0];
        return `background-color: ${color};`;
    }

    getStatusBadgeClass(state) {
        const classes = {
            'draft': 'bg-secondary',
            'sent': 'bg-info',
            'sale': 'bg-primary',
            'done': 'bg-success',
            'cancel': 'bg-danger',
        };
        return classes[state] || 'bg-secondary';
    }

    getStatusLabel(state) {
        const labels = {
            'draft': 'Quotation',
            'sent': 'Sent',
            'sale': 'Confirmed',
            'done': 'Done',
            'cancel': 'Cancelled',
        };
        return labels[state] || state;
    }

    async openCalendar() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Rental Calendar",
            res_model: "sale.order.line",
            views: [[false, "calendar"], [false, "form"]],
            target: "current",
            domain: [["rental", "=", true]],
        });
    }
}

RentalDashboard.template = "rental_dashboard.RentalDashboard";
RentalDashboard.components = {View};
RentalDashboard.props = {"*": true};

registry.category("actions").add("rental_dashboard.dashboard", RentalDashboard);
