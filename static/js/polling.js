// ============================================
// Real-time Polling System for Auction Website
// ============================================

// --- Time Synchronization Logic ---
// Global object to manage server-client time offset
const ServerTime = {
    offset: 0, // ms: server_time - local_time
    isSynced: false,

    sync(serverIsoString) {
        if (!serverIsoString) return;
        const serverTime = new Date(serverIsoString).getTime();
        const localTime = Date.now();
        this.offset = serverTime - localTime;
        this.isSynced = true;
        // console.log(`🕒 Time Synced. Offset: ${this.offset}ms (Server - Local)`);
    },

    now() {
        return Date.now() + this.offset;
    }
};

// Translation strings (will be injected by Django template)
let i18nStrings = {};

// ============================================
// Product List Poller Class
// ============================================
class ProductListPoller {
    constructor() {
        this.pollInterval = 1000; // 1 second
        this.isPolling = false;
        this.failCount = 0;
        this.maxRetries = 3;
        this.timeoutId = null;
    }

    start() {
        console.log('🟢 Starting product list polling...');
        this.isPolling = true;
        this.poll();
    }

    stop() {
        console.log('🔴 Stopping product list polling...');
        this.isPolling = false;
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
    }

    async poll() {
        if (!this.isPolling) return;

        try {
            const response = await fetch('/api/products/poll/');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // Sync time
                ServerTime.sync(data.timestamp);

                this.updateProducts(data.products);
                this.updateStatusCounts(data.status_counts);
                this.failCount = 0; // Reset on success
            }

        } catch (error) {
            console.warn('⚠️ Polling error:', error);
            this.handleError(error);
        }

        // Schedule next poll
        this.timeoutId = setTimeout(() => this.poll(), this.pollInterval);
    }

    updateProducts(products) {
        let needsRefresh = false;
        let missingCards = false;

        products.forEach(newData => {
            const card = document.querySelector(`[data-product-id="${newData.id}"]`);

            // Detection: If a product exists in API but not in DOM, we need a full reload
            if (!card) {
                missingCards = true;
                return;
            }

            // Check and update price
            const oldPrice = parseInt(card.dataset.price);
            if (newData.current_price !== oldPrice) {
                this.updatePrice(card, newData.current_price);
            }

            // Check and update bids count
            const oldBidsCount = parseInt(card.dataset.bidsCount);
            if (newData.bids_count !== oldBidsCount) {
                this.updateBidsCount(card, newData.bids_count);
            }

            // Check and update status - BE AGGRESSIVE
            // Even if status matches, check if the button is actually the right one
            const currentStatus = card.dataset.status;
            const hasCorrectButton = (newData.status === 'Open' && card.querySelector('a')) ||
                (newData.status !== 'Open' && card.querySelector('button'));

            if (newData.status !== currentStatus || !hasCorrectButton) {
                console.log(`🔄 Syncing UI state for product ${newData.id} (${newData.status})`);
                this.updateStatus(card, newData.status, newData);
                needsRefresh = true;
            }

            // Update highest bidder for open items
            if (newData.status === 'Open') {
                this.updateHighestBidder(card, newData.highest_bidder_id);
            }

            // Update winner information for closed items
            if (['Closed', 'Ended', 'Unsold'].includes(newData.status)) {
                this.updateWinner(card, newData.winner_name);
            }

            // Check and update end_time
            const oldEndTime = card.dataset.end;
            if (newData.end_time && newData.end_time !== oldEndTime) {
                this.updateEndTime(card, newData.end_time);
            }

            // Update data attributes
            card.dataset.price = newData.current_price;
            card.dataset.bidsCount = newData.bids_count;
            card.dataset.status = newData.status;
            card.dataset.winner = newData.winner_name || '';
            if (newData.end_time) {
                card.dataset.end = newData.end_time;
            }
        });

        // Trigger global filter refresh if any status changed
        if (needsRefresh && typeof window.refreshFilters === 'function') {
            window.refreshFilters();
        }

        // If cards are missing or counts mismatch significantly, reload
        if (missingCards) {
            console.warn('🚩 Missing cards detected in DOM. Reloading page...');
            setTimeout(() => window.location.reload(), 1000);
        }
    }

    updatePrice(card, newPrice) {
        const priceElement = card.querySelector('.price-display');
        if (!priceElement) return;

        // Update price text
        priceElement.textContent = `$${Math.floor(newPrice).toLocaleString()}`;

        // Add animation
        priceElement.classList.add('price-updated');
        setTimeout(() => {
            priceElement.classList.remove('price-updated');
        }, 500);
    }

    updateBidsCount(card, newCount) {
        const bidsElement = card.querySelector('.bids-count-display');
        if (!bidsElement) return;

        // Get translated text for "次出價"
        const bidsText = bidsElement.textContent.match(/\d+(.+)/)?.[1] || '次出價';
        bidsElement.textContent = `${newCount}${bidsText}`;
    }

    updateEndTime(card, newEndTime) {
        const productId = card.dataset.productId;
        const oldEndTime = card.dataset.end;

        console.log(`⏰ Anti-sniper: End time updated for product ${productId}: ${oldEndTime} → ${newEndTime}`);

        // Update the data attribute - the countdown timer will pick up the new time on next cycle
        card.dataset.end = newEndTime;
    }

    updateStatus(card, newStatus, productData) {
        console.log(`📦 Product ${productData.id} status changed: ${card.dataset.status} → ${newStatus}`);

        // Update the action button based on the new status
        this.updateActionButton(card, newStatus, productData.id);

        // Update the info area (winner/highest bidder)
        this.updateWinner(card, productData.winner_name, newStatus, productData.highest_bidder_id);

        // Update card's data-status attribute IMMEDIATELY
        card.dataset.status = newStatus;
        card.setAttribute('data-status', newStatus);

        // If on products list page, use the global refresh function to handle visibility
        if (typeof window.refreshFilters === 'function') {
            window.refreshFilters();
        } else {
            // Fallback for pages without refreshFilters
            card.style.display = 'block';
        }
    }

    updateActionButton(card, status, productId) {
        const buttonContainer = card.querySelector('.text-center:last-child');
        if (!buttonContainer) return;

        let buttonHtml = '';
        if (status === 'Open') {
            const bidLabel = i18nStrings.bid || '出價';
            // Use window.location.origin to get base URL as we can't easily use reverse in JS
            // But we know the pattern is /{{lang}}/products/{{id}}/
            const langPrefix = window.location.pathname.split('/')[1] || 'zh-hant';
            const detailUrl = `/${langPrefix}/products/${productId}/`;

            buttonHtml = `
                <a href="${detailUrl}" class="block w-full py-2.5 font-bold rounded-full shadow-md transition text-sm" style="background-color: #1E40AF; color: white;" onmouseover="this.style.backgroundColor='#1a3a9e'" onmouseout="this.style.backgroundColor='#1E40AF'">
                    ${bidLabel}
                </a>
            `;
        } else if (status === 'Upcoming') {
            const notStartedLabel = i18nStrings.notStarted || '尚未開標';
            buttonHtml = `
                <button disabled class="block w-full py-2.5 bg-white font-bold rounded-full cursor-not-allowed text-sm" style="border: 2px solid #9492a4; color: #9492a4;">
                    ${notStartedLabel}
                </button>
            `;
        } else {
            const endedLabel = i18nStrings.ended || '已結標';
            buttonHtml = `
                <button disabled class="block w-full py-2.5 font-bold rounded-full cursor-not-allowed text-sm" style="background-color: #9492a4; color: white;">
                    ${endedLabel}
                </button>
            `;
        }

        buttonContainer.innerHTML = buttonHtml;
    }

    updateWinner(card, winnerName, status = null, highestBidderId = null) {
        const winnerContainer = card.querySelector('.winner-info');
        if (!winnerContainer) return;

        const currentStatus = status || card.dataset.status;
        const currentWinner = card.dataset.winner;

        // Only skip if nothing changed and we aren't forcing a status update
        if (!status && currentWinner === (winnerName || '')) return;

        let html = '';
        if (['Closed', 'Ended', 'Unsold'].includes(currentStatus)) {
            if (winnerName) {
                const winnerLabel = i18nStrings.winner || '得標者';
                html = `
                    <div class="text-sm text-green-700 font-semibold flex items-center">
                      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
                      <span>${winnerLabel}: ${winnerName}</span>
                    </div>
                `;
            } else {
                const noBidsLabel = i18nStrings.noBids || '無人出價';
                html = `
                    <div class="text-sm text-gray-500 flex items-center">
                      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                      <span>${noBidsLabel}</span>
                    </div>
                `;
            }
        } else if (currentStatus === 'Open') {
            if (highestBidderId) {
                const highestBidLabel = i18nStrings.highestBid || '最高出價';
                html = `
                    <div class="text-sm font-medium flex items-center highest-bidder-display" style="color: #1E40AF;">
                      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                      <span>${highestBidLabel}: ${highestBidderId}</span>
                    </div>
                `;
            } else {
                const waitingBidLabel = i18nStrings.waitingBid || '等待首次出價';
                html = `
                    <div class="text-sm text-gray-400 flex items-center">
                      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                      <span>${waitingBidLabel}</span>
                    </div>
                `;
            }
        }

        winnerContainer.innerHTML = html;
        card.dataset.winner = winnerName || '';
    }

    updateHighestBidder(card, bidderId) {
        // This is handled by updateWinner now during status changes, 
        // but we still update the ID if it changes while Open.
        const bidderDisplay = card.querySelector('.highest-bidder-display');
        if (!bidderDisplay) {
            // If it's Open but display is missing (transitioned recently), force a refresh
            if (card.dataset.status === 'Open') {
                this.updateWinner(card, null, 'Open', bidderId);
            }
            return;
        }

        const bidderSpan = bidderDisplay.querySelector('span:last-child');
        if (!bidderSpan) return;

        const currentText = bidderSpan.textContent;
        const currentBidderId = currentText.split(': ')[1];

        if (currentBidderId === bidderId) return;

        const highestBidLabel = currentText.split(': ')[0];
        bidderSpan.textContent = `${highestBidLabel}: ${bidderId || '---'}`;

        bidderDisplay.classList.add('price-updated');
        setTimeout(() => {
            bidderDisplay.classList.remove('price-updated');
        }, 500);
    }


    updateStatusCounts(counts) {
        Object.keys(counts).forEach(status => {
            const countElement = document.getElementById(`count-${status}`);
            if (countElement) {
                countElement.textContent = `(${counts[status]})`;
            }
        });
    }

    handleError(error) {
        this.failCount++;

        if (this.failCount >= this.maxRetries) {
            console.warn(`⚠️ Failed ${this.failCount} times, waiting 5 seconds...`);
            this.pollInterval = 5000; // Slow down to 5 seconds

            // Reset after 10 seconds
            setTimeout(() => {
                this.pollInterval = 1000;
                this.failCount = 0;
            }, 10000);
        }
    }
}

// ============================================
// Product Detail Poller Class
// ============================================
class ProductDetailPoller {
    constructor(productId) {
        this.productId = productId;
        this.pollInterval = 1000;
        this.isPolling = false;
        this.failCount = 0;
        this.maxRetries = 3;
        this.timeoutId = null;
        this.lastBidIds = new Set();
    }

    start() {
        console.log(`🟢 Starting product ${this.productId} detail polling...`);
        this.isPolling = true;
        this.poll();
    }

    stop() {
        console.log(`🔴 Stopping product ${this.productId} detail polling...`);
        this.isPolling = false;
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
    }

    async poll() {
        if (!this.isPolling) return;

        try {
            const response = await fetch(`/api/products/${this.productId}/poll/`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // Sync time
                ServerTime.sync(data.timestamp);

                this.updateProduct(data.product);
                this.updateHighestBidder(data.highest_bidder);
                this.updateBidHistory(data.bids);
                this.failCount = 0;
            }

        } catch (error) {
            console.warn('⚠️ Detail polling error:', error);
            this.handleError(error);
        }

        this.timeoutId = setTimeout(() => this.poll(), this.pollInterval);
    }

    updateProduct(product) {
        // Update price
        const priceElements = document.querySelectorAll('[data-price-display]');
        priceElements.forEach(el => {
            const oldPrice = el.textContent.replace(/[^\d]/g, '');
            const newPrice = Math.floor(product.current_price);

            if (parseInt(oldPrice) !== newPrice) {
                el.textContent = `$${newPrice.toLocaleString()}`;
                el.classList.add('price-updated');
                setTimeout(() => el.classList.remove('price-updated'), 500);
            }
        });

        // Update bids count
        const bidsCountElements = document.querySelectorAll('[data-bids-count-display]');
        bidsCountElements.forEach(el => {
            const bidsText = el.textContent.match(/\d+(.+)/)?.[1] || '次出價';
            el.textContent = `${product.bids_count || 0}${bidsText}`;
        });
    }

    updateHighestBidder(bidder) {
        const bidderElement = document.querySelector('[data-highest-bidder]');
        if (!bidderElement) return;

        if (bidder && bidder.id) {
            bidderElement.textContent = bidder.id;  // 只顯示工號
        } else {
            bidderElement.textContent = '---';
        }
    }

    updateBidHistory(bids) {
        const historyContainer = document.querySelector('[data-bid-history]');
        if (!historyContainer) return;

        // Check for new bids
        const newBids = bids.filter(bid => !this.lastBidIds.has(bid.id));

        if (newBids.length > 0) {
            // Add new bids with animation
            newBids.forEach(bid => {
                this.addBidWithAnimation(historyContainer, bid);
                this.lastBidIds.add(bid.id);
            });
        }

        // Update all bid IDs
        this.lastBidIds = new Set(bids.map(b => b.id));
    }

    addBidWithAnimation(container, bid) {
        const bidRow = this.createBidRow(bid);
        bidRow.classList.add('bid-new');

        // Insert at the top
        if (container.firstChild) {
            container.insertBefore(bidRow, container.firstChild);
        } else {
            container.appendChild(bidRow);
        }

        // Remove animation class after it finishes
        setTimeout(() => {
            bidRow.classList.remove('bid-new');
            bidRow.style.backgroundColor = '';
        }, 400);

        // Keep only the latest 10 bids
        while (container.children.length > 10) {
            container.removeChild(container.lastChild);
        }
    }

    createBidRow(bid) {
        const row = document.createElement('tr');
        row.innerHTML = `
      <td class="py-2 px-4">${bid.bidder_name || bid.bidder_id}</td>
      <td class="py-2 px-4">$${Math.floor(bid.amount).toLocaleString()}</td>
      <td class="py-2 px-4">${this.formatTimestamp(bid.bid_timestamp)}</td>
    `;
        return row;
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString('zh-TW', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    handleError(error) {
        this.failCount++;

        if (this.failCount >= this.maxRetries) {
            console.warn(`⚠️ Failed ${this.failCount} times, waiting 5 seconds...`);
            this.pollInterval = 5000;

            setTimeout(() => {
                this.pollInterval = 1000;
                this.failCount = 0;
            }, 10000);
        }
    }
}

// ============================================
// Page Visibility API Integration
// ============================================
function setupVisibilityHandling(poller) {
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('📱 Page hidden, pausing polling...');
            poller.stop();
        } else {
            console.log('📱 Page visible, resuming polling...');
            poller.start();
        }
    });
}

// ============================================
// Export for use in templates
// ============================================
window.ServerTime = ServerTime;
window.ProductListPoller = ProductListPoller;
window.ProductDetailPoller = ProductDetailPoller;
window.setupVisibilityHandling = setupVisibilityHandling;
window.setPollingI18n = function (strings) {
    i18nStrings = strings;
};
