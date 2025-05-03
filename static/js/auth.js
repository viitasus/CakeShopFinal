/**
 * Happy Cake - Cart JavaScript
 * Handles shopping cart functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const cartItemsContainer = document.getElementById('cart-items');
    const emptyCartMessage = document.getElementById('empty-cart');
    const cartSummary = document.querySelector('.cart-summary');
    const checkoutBtn = document.getElementById('checkout-btn');
    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    
    // Load cart data
    if (cartItemsContainer) {
        loadCartItems();
    }
    
    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    if (addToCartButtons.length > 0) {
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function() {
                const cakeId = this.getAttribute('data-cake-id');
                const cakeName = this.getAttribute('data-cake-name');
                const price = parseFloat(this.getAttribute('data-price'));
                
                // Get quantity if in modal
                let quantity = 1;
                const quantityInput = document.getElementById('modal-cake-quantity');
                if (quantityInput) {
                    quantity = parseInt(quantityInput.value) || 1;
                }
                
                addToCart(cakeId, cakeName, price, quantity);
            });
        });
    }
    
    // Apply coupon functionality
    if (applyCouponBtn) {
        applyCouponBtn.addEventListener('click', function() {
            const couponInput = document.getElementById('coupon-code');
            const couponCode = couponInput.value.trim();
            
            if (!couponCode) {
                showNotification('Please enter a coupon code', 'error');
                return;
            }
            
            applyCoupon(couponCode);
        });
    }
    
    // Checkout button functionality
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            window.location.href = '/checkout';
        });
    }
    
    // Load cart items function
    function loadCartItems() {
        fetch('/api/cart')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const cartItems = data.cart_items;
                    
                    if (cartItems.length === 0) {
                        // Show empty cart message
                        if (cartItemsContainer) cartItemsContainer.parentElement.style.display = 'none';
                        if (emptyCartMessage) emptyCartMessage.style.display = 'block';
                        if (cartSummary) cartSummary.style.display = 'none';
                    } else {
                        // Show cart items
                        if (cartItemsContainer) cartItemsContainer.parentElement.style.display = 'flex';
                        if (emptyCartMessage) emptyCartMessage.style.display = 'none';
                        if (cartSummary) cartSummary.style.display = 'block';
                        
                        // Render cart items
                        renderCartItems(cartItems);
                        
                        // Update cart summary
                        updateCartSummary(data.cart_total);
                    }
                } else {
                    showNotification('Failed to load cart items', 'error');
                }
            })
            .catch(error => {
                console.error('Error loading cart items:', error);
                showNotification('An error occurred while loading your cart', 'error');
            });
    }
    
    // Render cart items function
    function renderCartItems(cartItems) {
        if (!cartItemsContainer) return;
        
        let html = '';
        cartItems.forEach(item => {
            html += `
                <div class="cart-item" data-id="${item.id}">
                    <div class="cart-item-image">
                        <img src="${item.image}" alt="${item.cake_name}">
                    </div>
                    <div class="cart-item-details">
                        <h3>${item.cake_name}</h3>
                        <p class="cart-item-price">₹${item.price.toLocaleString()}</p>
                    </div>
                    <div class="cart-item-quantity">
                        <button class="quantity-btn minus-btn" onclick="updateCartItemQuantity(${item.id}, ${item.quantity - 1})">
                            <i class="fas fa-minus"></i>
                        </button>
                        <input type="number" value="${item.quantity}" min="1" max="10" 
                               onchange="updateCartItemQuantity(${item.id}, this.value)">
                        <button class="quantity-btn plus-btn" onclick="updateCartItemQuantity(${item.id}, ${item.quantity + 1})">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <div class="cart-item-total">
                        <p>₹${item.total.toLocaleString()}</p>
                    </div>
                    <button class="remove-item-btn" onclick="removeCartItem(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        });
        
        cartItemsContainer.innerHTML = html;
    }
    
    // Update cart summary function
    function updateCartSummary(subtotal) {
        if (!cartSummary) return;
        
        // Get elements
        const subtotalElement = cartSummary.querySelector('.summary-row:first-child span:last-child');
        const discountElement = cartSummary.querySelector('.summary-row.discount span:last-child');
        const totalElement = cartSummary.querySelector('.summary-row.total span:last-child');
        
        // Update subtotal
        if (subtotalElement) {
            subtotalElement.textContent = `₹${subtotal.toLocaleString()}`;
        }
        
        // Get discount amount
        let discount = 0;
        if (discountElement) {
            const discountText = discountElement.textContent;
            discount = parseInt(discountText.replace(/[^\d]/g, '')) || 0;
        }
        
        // Fixed delivery fee
        const deliveryFee = 50;
        
        // Calculate total
        const total = subtotal + deliveryFee - discount;
        
        // Update total
        if (totalElement) {
            totalElement.textContent = `₹${total.toLocaleString()}`;
        }
    }
    
    // Add to cart function
    function addToCart(cakeId, cakeName, price, quantity = 1) {
        fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cake_id: cakeId,
                cake_name: cakeName,
                price: price,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message || 'Item added to cart', 'success');
                
                // Update cart count
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.cart_count;
                    cartCount.style.display = 'block';
                }
                
                // Close modal if open
                const modal = document.getElementById('cake-modal');
                if (modal && modal.style.display === 'flex') {
                    modal.style.display = 'none';
                    document.body.style.overflow = 'auto';
                }
                
                // Reload cart if on cart page
                if (cartItemsContainer) {
                    loadCartItems();
                }
            } else {
                showNotification(data.message || 'Failed to add item to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            showNotification('An error occurred while adding to cart', 'error');
        });
    }
    
    // Apply coupon function
    function applyCoupon(couponCode) {
        fetch('/api/coupon/apply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: couponCode
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message || 'Coupon applied successfully', 'success');
                
                // Update discount in summary
                const discountElement = document.querySelector('.summary-row.discount span:last-child');
                if (discountElement) {
                    discountElement.textContent = `-₹${data.discount.toLocaleString()}`;
                }
                
                // Recalculate total
                updateCartSummary(parseFloat(document.querySelector('.summary-row:first-child span:last-child').textContent.replace(/[^\d]/g, '')));
            } else {
                showNotification(data.message || 'Invalid coupon code', 'error');
            }
        })
        .catch(error => {
            console.error('Error applying coupon:', error);
            showNotification('An error occurred while applying the coupon', 'error');
        });
    }
    
    // Expose functions to global scope
    window.updateCartItemQuantity = function(itemId, quantity) {
        // Convert to integer and validate
        quantity = parseInt(quantity);
        if (isNaN(quantity) || quantity < 1) quantity = 1;
        if (quantity > 10) quantity = 10;
        
        fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cart_item_id: itemId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload cart items
                loadCartItems();
            } else {
                showNotification(data.message || 'Failed to update cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error updating cart:', error);
            showNotification('An error occurred while updating your cart', 'error');
        });
    };
    
    window.removeCartItem = function(itemId) {
        fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cart_item_id: itemId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message || 'Item removed from cart', 'success');
                
                // Reload cart items
                loadCartItems();
                
                // Update cart count
                updateCartCount();
            } else {
                showNotification(data.message || 'Failed to remove item from cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error removing item from cart:', error);
            showNotification('An error occurred while removing the item from your cart', 'error');
        });
    };
    
    window.clearCart = function() {
        if (!confirm('Are you sure you want to clear your cart?')) return;
        
        fetch('/api/cart/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message || 'Cart cleared successfully', 'success');
                
                // Reload cart items
                loadCartItems();
                
                // Update cart count
                updateCartCount();
            } else {
                showNotification(data.message || 'Failed to clear cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing cart:', error);
            showNotification('An error occurred while clearing your cart', 'error');
        });
    };
    
    // Update cart count
    function updateCartCount() {
        fetch('/api/cart/count')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const cartCount = document.getElementById('cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_count;
                        cartCount.style.display = data.cart_count > 0 ? 'block' : 'none';
                    }
                }
            })
            .catch(error => {
                console.error('Error updating cart count:', error);
            });
    }
});