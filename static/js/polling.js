// ============================================
// Real-time Polling System for Auction Website
// ============================================

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
        products.forEach(newData => {
            const card = document.querySelector(`[data-product-id="${newData.id}"]`);
            if (!card) return;

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

            // Check and update status
            const oldStatus = card.dataset.status;
            if (newData.status !== oldStatus) {
                this.updateStatus(card, newData.status, newData);
            }

            // Update highest bidder for open items
            if (newData.status === 'Open') {
                this.updateHighestBidder(card, newData.highest_bidder_id);
            }

            // Update winner information for closed items
            if (['Closed', 'Ended', 'Unsold'].includes(newData.status)) {
                this.updateWinner(card, newData.winner_name);
            }

            // Check and update end_time (for anti-sniper time extension)
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

        // Fade out from current tab
        card.classList.add('card-fade-out');

        setTimeout(() => {
            card.dataset.status = newStatus;

            // Check if card should be visible in current tab
            const currentTab = document.querySelector('.tab-btn.text-blue-600')?.id.replace('tab-', '');
            let shouldBeVisible = false;

            if (currentTab === 'Closed') {
                shouldBeVisible = ['Closed', 'Ended', 'Unsold'].includes(newStatus);
            } else {
                shouldBeVisible = (newStatus === currentTab);
            }

            if (shouldBeVisible) {
                // Fade in
                card.classList.remove('card-fade-out');
                card.classList.add('card-fade-in');
                card.style.display = 'block';

                setTimeout(() => {
                    card.classList.remove('card-fade-in');
                }, 300);
            } else {
                // Hide card
                card.style.display = 'none';
                card.classList.remove('card-fade-out');
            }
        }, 300);
    }

    updateWinner(card, winnerName) {
        const winnerContainer = card.querySelector('.winner-info');
        if (!winnerContainer) return;

        const currentWinner = card.dataset.winner;
        if (currentWinner === (winnerName || '')) return; // No change

        // Update winner display
        if (winnerName) {
            // Get translated text
            const winnerLabel = i18nStrings.winner || '得標者';
            winnerContainer.innerHTML = `
        <div class="text-sm text-green-700 mb-3 font-semibold flex items-center">
          <span class="mr-1">🏆</span>
          <span>${winnerLabel}: ${winnerName}</span>
        </div>
      `;
        } else {
            const noBidsLabel = i18nStrings.noBids || '無人出價';
            winnerContainer.innerHTML = `
        <div class="text-sm text-gray-500 mb-3 flex items-center">
          <span class="mr-1">ℹ️</span>
          <span>${noBidsLabel}</span>
        </div>
      `;
        }

        card.dataset.winner = winnerName || '';
    }

    updateHighestBidder(card, bidderId) {
        const bidderDisplay = card.querySelector('.highest-bidder-display');
        if (!bidderDisplay) return;

        const bidderSpan = bidderDisplay.querySelector('span:last-child');
        if (!bidderSpan) return;

        // Get the current bidder ID from the display
        const currentText = bidderSpan.textContent;
        const currentBidderId = currentText.split(': ')[1];

        // Only update if changed
        if (currentBidderId === bidderId) return;

        // Update the bidder ID
        const highestBidLabel = currentText.split(': ')[0];
        bidderSpan.textContent = `${highestBidLabel}: ${bidderId || '---'}`;

        // Add animation
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
window.ProductListPoller = ProductListPoller;
window.ProductDetailPoller = ProductDetailPoller;
window.setupVisibilityHandling = setupVisibilityHandling;
window.setPollingI18n = function (strings) {
    i18nStrings = strings;
};
