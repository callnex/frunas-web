(() => {
    const cards = document.querySelectorAll('.candy-card');
    const summaryItems = document.getElementById('summaryItems');
    const summaryEmpty = document.getElementById('summaryEmpty');
    const summaryTotal = document.getElementById('summaryTotal');
    const cartDataInput = document.getElementById('cartDataInput');
    const checkoutForm = document.getElementById('checkoutForm');

    if (!cards.length || !summaryItems || !summaryTotal || !cartDataInput || !checkoutForm) {
        return;
    }

    const CART_STORAGE_KEY = 'sugar_rush_cart';
    const cart = new Map();
    const priceFormatter = new Intl.NumberFormat('es-CO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });

    const parsePrice = (rawValue) => {
        if (typeof rawValue === 'number') {
            return rawValue;
        }

        const compact = String(rawValue).trim().replace(/\s/g, '');
        let normalized = compact;

        if (compact.includes(',') && compact.includes('.')) {
            normalized = compact.replace(/\./g, '').replace(',', '.');
        } else if (compact.includes(',')) {
            normalized = compact.replace(',', '.');
        }

        return Number(normalized);
    };

    const formatPrice = (value) => `$${priceFormatter.format(parsePrice(value))}`;

    const loadStoredCart = () => {
        try {
            const storedValue = window.localStorage.getItem(CART_STORAGE_KEY);
            return storedValue ? JSON.parse(storedValue) : [];
        } catch (error) {
            window.localStorage.removeItem(CART_STORAGE_KEY);
            return [];
        }
    };

    const persistCart = () => {
        const payload = Array.from(cart.entries()).map(([candyId, item]) => ({
            candy_id: Number(candyId),
            quantity: item.quantity,
        }));

        if (!payload.length) {
            window.localStorage.removeItem(CART_STORAGE_KEY);
            return;
        }

        window.localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(payload));
    };

    const syncHiddenInput = () => {
        const payload = Array.from(cart.entries()).map(([candyId, item]) => ({
            candy_id: Number(candyId),
            quantity: item.quantity,
        }));
        cartDataInput.value = JSON.stringify(payload);
    };

    const renderSummary = () => {
        summaryItems.querySelectorAll('.summary-item').forEach((node) => node.remove());

        if (!cart.size) {
            summaryEmpty.classList.remove('d-none');
            summaryTotal.textContent = formatPrice(0);
            syncHiddenInput();
            persistCart();
            return;
        }

        summaryEmpty.classList.add('d-none');

        let total = 0;
        cart.forEach((item) => {
            total += item.price * item.quantity;
            const wrapper = document.createElement('article');
            wrapper.className = 'summary-item';
            wrapper.innerHTML = `
                <div>
                    <div class="summary-item-name">${item.name}</div>
                    <span class="summary-item-meta">x${item.quantity}</span>
                </div>
                <strong>${formatPrice(item.price * item.quantity)}</strong>
            `;
            summaryItems.appendChild(wrapper);
        });

        summaryTotal.textContent = formatPrice(total);
        syncHiddenInput();
        persistCart();
    };

    const storedCart = new Map(
        loadStoredCart()
            .map((item) => [String(item.candy_id), Number(item.quantity)])
            .filter(([, quantity]) => Number.isFinite(quantity) && quantity > 0)
    );

    cards.forEach((card) => {
        const candyId = card.dataset.candyId;
        const name = card.dataset.candyName;
        const price = parsePrice(card.dataset.candyPrice);
        const stock = Number(card.dataset.candyStock);
        const qtyValue = card.querySelector('.qty-value');
        const incrementBtn = card.querySelector('.increment');
        const decrementBtn = card.querySelector('.decrement');

        let currentQty = Math.min(storedCart.get(candyId) || 0, stock);

        const syncCardWithCart = () => {
            if (currentQty > 0) {
                cart.set(candyId, { name, price, quantity: currentQty });
            } else {
                cart.delete(candyId);
            }
            renderSummary();
        };

        const updateCardState = () => {
            qtyValue.textContent = currentQty;
            decrementBtn.disabled = currentQty === 0;
            incrementBtn.disabled = currentQty >= stock || stock === 0;
        };

        incrementBtn?.addEventListener('click', () => {
            if (currentQty < stock) {
                currentQty += 1;
                syncCardWithCart();
                updateCardState();
            }
        });

        decrementBtn?.addEventListener('click', () => {
            if (currentQty > 0) {
                currentQty -= 1;
                syncCardWithCart();
                updateCardState();
            }
        });

        updateCardState();
        if (currentQty > 0) {
            cart.set(candyId, { name, price, quantity: currentQty });
        }
    });

    checkoutForm.addEventListener('submit', (event) => {
        syncHiddenInput();
        if (!cart.size) {
            event.preventDefault();
            window.alert('Selecciona al menos un dulce antes de confirmar.');
        }
    });

    renderSummary();
})();
