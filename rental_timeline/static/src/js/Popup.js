odoo.define("rental_timeline.Popup", function() {
    "use strict";
    /**
     * Popup is a class to create a popup window with some text
     */
    class Popup {
        /**
         * @param {Element} container       The container object.
         * @param {String}  overflowMethod  How the popup should act to overflowing ('flip' or 'cap')
         */
        constructor(container, overflowMethod) {
            this.container = container;
            this.overflowMethod = overflowMethod || "cap";

            this.x = 0;
            this.y = 0;
            this.padding = 5;
            this.hidden = false;

            // Create the frame
            this.frame = document.createElement("div");
            this.frame.className = "vis-tooltip";
            this.container.appendChild(this.frame);
        }

        /**
         * @param {Number} x   Horizontal position of the popup window
         * @param {Number} y   Vertical position of the popup window
         */
        setPosition(x, y) {
            this.x = parseInt(x, 10);
            this.y = parseInt(y, 10);
        }

        /**
         * Set the content for the popup window. This can be HTML code or text.
         * @param {String | Element} content
         */
        setText(content) {
            if (content instanceof Element) {
                this.frame.innerHTML = "";
                this.frame.appendChild(content);
            } else {
                // String containing text or HTML
                this.frame.innerHTML = content;
            }
        }

        /**
         * Show the popup window
         * @param {Boolean} [doShow]   Show or hide the window
         */

        show(doShow) {
            var doshow = doShow;
            if (doshow === undefined) {
                doshow = true;
            }

            if (doshow === true) {
                var height = this.frame.clientHeight;
                var width = this.frame.clientWidth;
                var maxHeight = this.frame.parentNode.clientHeight;
                var maxWidth = this.frame.parentNode.clientWidth;

                var left = 0,
                    top = 0;

                if (this.overflowMethod === "flip") {
                    var isLeft = false,
                        // Where around the position it's located
                        isTop = true;

                    if (this.y - height < this.padding) {
                        isTop = false;
                    }

                    if (this.x + width > maxWidth - this.padding) {
                        isLeft = true;
                    }

                    if (isLeft) {
                        left = this.x - width;
                    } else {
                        left = this.x;
                    }

                    if (isTop) {
                        top = this.y - height;
                    } else {
                        top = this.y;
                    }
                } else {
                    top = this.y - height;
                    if (top + height + this.padding > maxHeight) {
                        top = maxHeight - height - this.padding;
                    }
                    if (top < this.padding) {
                        top = this.padding;
                    }

                    left = this.x;
                    if (left + width + this.padding > maxWidth) {
                        left = maxWidth - width - this.padding;
                    }
                    if (left < this.padding) {
                        left = this.padding;
                    }
                }

                this.frame.style.left = left + "px";
                this.frame.style.top = top + "px";
                this.frame.style.visibility = "visible";
                this.hidden = false;
            } else {
                this.hide();
            }
        }

        /**
         * Hide the popup window
         */
        hide() {
            this.hidden = true;
            this.frame.style.left = "0";
            this.frame.style.top = "0";
            this.frame.style.visibility = "hidden";
        }

        /**
         * Remove the popup window
         */
        destroy() {
            // Remove element from DOM
            this.frame.parentNode.removeChild(this.frame);
        }
    }
    return Popup;
});
