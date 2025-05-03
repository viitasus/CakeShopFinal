/**
 * Happy Cake - Checkout JavaScript
 * Handles checkout process functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const checkoutSteps = document.querySelectorAll('.checkout-step-content');
    const checkoutStepIndicators = document.querySelectorAll('.checkout-steps .step');
    
    const shippingStep = document.getElementById('shipping-step');
    const paymentStep = document.getElementById('payment-step');
    const confirmationStep = document.getElementById('confirmation-step');
    
    const shippingNextBtn = document.getElementById('shipping-next-btn');
    const paymentBackBtn = document.getElementById('payment-back-btn');
    const paymentNextBtn = document.getElementById('payment-next-btn');
    
    const addressesContainer = document.getElementById('addresses-container');
    const showAddressFormBtn = document.getElementById('show-address-form');
    const addAddressForm = document.getElementById('add-address-form');
    const newAddressForm = document.getElementById('new-address-form');
    const cancelAddressBtn = document.getElementById('cancel-address-btn');
    
    const deliveryDateInput = document.getElementById('delivery-date');
    const specialInstructionsInput = document.getElementById('special-instructions');
    
    const paymentMethods = document.querySelectorAll('input[name="payment-method"]');
    const cardPaymentForm = document.getElementById('card-payment-form');
    const upiPaymentForm = document.getElementById('upi-payment-form');
    
    const orderProcessing = document.querySelector('.order-processing');
    const orderConfirmation = document.querySelector('.order-confirmation');
    const orderNumber = document.getElementById('order-number');
    const orderSummary = document.getElementById('order-summary');
    const viewOrderBtn = document.getElementById('view-order-btn');
    
    const cartItemsSummary = document.getElementById('cart-items-summary');
    const summarySubtotal = document.getElementById('summary-subtotal');
    const summaryDiscount = document.getElementById('summary-discount');
    const summaryTotal = document.getElementById('summary-total');
    
    // Load cart summary
    loadCartSummary();
    
    // Load user addresses
    loadUserAddresses();
    
    // Set minimum delivery date (tomorrow)
    if (deliveryDateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        deliveryDateInput.min = tomorrow.toISOString().split('T')[0];
        deliveryDateInput.value = tomorrow.toISOString().split('T')[0];
    }
    
    // Show/hide address form
    if (showAddressFormBtn) {
        showAddressFormBtn.addEventListener('click', function() {
            addAddressForm.style.display = 'block';
            this.style.display = 'none';
        });
    }
    
    // Cancel address form
    if (cancelAddressBtn) {
        cancelAddressBtn.addEventListener('click', function() {
            addAddressForm.style.display = 'none';
            showAddressFormBtn.style.display = 'block';
            newAddressForm.reset();
        });
    }
    
    // New address form submission
    if (newAddressForm) {
        newAddressForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const label = document.getElementById('address-label').value;
            const line1 = document.getElementById('address-line1').value;
            const line2 = document.getElementById('address-line2').value;
            const city = document.getElementById('address-city').value;
            const state = document.getElementById('address-state').value;
            const postalCode = document.getElementById('address-postal-code').value;
            const phone = document.getElementById('address-phone').value;
            const isDefault = document.getElementById('address-default').checked;
            
            // Validate form
            if (!label || !line1 || !city || !state || !postalCode) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Saving...';
            submitBtn.disabled = true;
            
            // Send request to add address
            fetch('/api/user/addresses/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    label: label,
                    address_line1: line1,
                    address_line2: line2,
                    city: city,
                    state: state,
                    postal_code: postalCode,
                    phone: phone,
                    is_default: isDefault
                })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    showNotification('Address added successfully', 'success');
                    
                    // Reset form and hide it
                    newAddressForm.reset();
                    addAddressForm.style.display = 'none';
                    showAddressFormBtn.style.display = 'block';
                    
                    // Reload addresses
                    loadUserAddresses();
                } else {
                    showNotification(data.message || 'Failed to add address', 'error');
                }
            })
            .catch(error => {
                console.error('Error adding address:', error);
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Shipping step continue button
    if (shippingNextBtn) {
        shippingNextBtn.addEventListener('click', function() {
            // Get selected address
            const selectedAddress = document.querySelector('input[name="shipping-address"]:checked');
            
            if (!selectedAddress) {
                showNotification('Please select a shipping address', 'error');
                return;
            }
            
            // Get delivery date
            const deliveryDate = deliveryDateInput.value;
            
            if (!deliveryDate) {
                showNotification('Please select a delivery date', 'error');
                return;
            }
            
            // Proceed to payment step
            goToStep(1);
        });
    }
    
    // Payment step back button
    if (paymentBackBtn) {
        paymentBackBtn.addEventListener('click', function() {
            goToStep(0);
        });
    }
    
    // Payment method selection
    if (paymentMethods.length > 0) {
        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                const methodValue = this.value;
                
                // Hide all payment forms
                cardPaymentForm.style.display = 'none';
                upiPaymentForm.style.display = 'none';
                
                // Show selected payment form
                if (methodValue === 'card') {
                    cardPaymentForm.style.display = 'block';
                } else if (methodValue === 'upi') {
                    upiPaymentForm.style.display = 'block';
                }
            });
        });
    }
    
    // Payment step continue button (place order)
    if (paymentNextBtn) {
        paymentNextBtn.addEventListener('click', function() {
            // Get selected payment method
            const selectedMethod = document.querySelector('input[name="payment-method"]:checked');
            
            if (!selectedMethod) {
                showNotification('Please select a payment method', 'error');
                return;
            }
            
            const paymentMethod = selectedMethod.value;
            
            // Validate payment form if card or UPI selected
            if (paymentMethod === 'card') {
                const cardNumber = document.getElementById('card-number').value;
                const cardExpiry = document.getElementById('card-expiry').value;
                const cardCvv = document.getElementById('card-cvv').value;
                const cardName = document.getElementById('card-name').value;
                
                if (!cardNumber || !cardExpiry || !cardCvv || !cardName) {
                    showNotification('Please fill in all card details', 'error');
                    return;
                }
            } else if (paymentMethod === 'upi') {
                const upiId = document.getElementById('upi-id').value;
                
                if (!upiId) {
                    showNotification('Please enter your UPI ID', 'error');
                    return;
                }
            }
            
            // Proceed to confirmation step
            goToStep(2);
            
            // Show processing state
            orderProcessing.style.display = 'block';
            orderConfirmation.style.display = 'none';
            
            // Get selected address
            const selectedAddress = document.querySelector('input[name="shipping-address"]:checked').value;
            const deliveryDate = deliveryDateInput.value;
            const specialInstructions = specialInstructionsInput.value;
            
            // Place order
            placeOrder(selectedAddress, deliveryDate, paymentMethod, specialInstructions);
        });
    }
    
    // Load user addresses function
    function loadUserAddresses() {
        if (!addressesContainer) return;
        
        // Show loading placeholder
        addressesContainer.innerHTML = '<div class="loading-placeholder"></div>';
        
        // Fetch user addresses
        fetch('/api/user/addresses')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.addresses) {
                    if (data.addresses.length === 0) {
                        // No addresses found
                        addressesContainer.innerHTML = '<p>You have no saved addresses. Please add a new address.</p>';
                        
                        // Show address form
                        addAddressForm.style.display = 'block';
                        showAddressFormBtn.style.display = 'none';
                    } else {
                        // Render addresses
                        let html = '';
                        data.addresses.forEach((address, index) => {
                            html += `
                                <div class="address-card">
                                    <input type="radio" name="shipping-address" id="address-${address.id}" value="${address.id}" ${address.is_default ? 'checked' : ''}>
                                    <label for="address-${address.id}">
                                        <div class="address-header">
                                            <h4>${address.label}</h4>
                                            ${address.is_default ? '<span class="default-badge">Default</span>' : ''}
                                        </div>
                                        <p>${address.address_line1}</p>
                                        ${address.address_line2 ? `<p>${address.address_line2}</p>` : ''}
                                        <p>${address.city}, ${address.state} ${address.postal_code}</p>
                                        ${address.phone ? `<p>Phone: ${address.phone}</p>` : ''}
                                    </label>
                                </div>
                            `;
                        });
                        
                        addressesContainer.innerHTML = html;
                    }
                } else {
                    addressesContainer.innerHTML = '<p class="error-message">Error loading addresses. Please try again.</p>';
                }
            })
            .catch(error => {
                console.error('Error loading addresses:', error);
                addressesContainer.innerHTML = '<p class="error-message">Error loading addresses. Please try again.</p>';
            });
    }
    
    // Load cart summary function
    function loadCartSummary() {
        if (!cartItemsSummary) return;
        
        // Show loading placeholder
        cartItemsSummary.innerHTML = '<div class="loading-placeholder"></div>';
        
        // Fetch cart items
        fetch('/api/cart')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const cartItems = data.cart_items;
                    
                    if (cartItems.length === 0) {
                        // Empty cart
                        cartItemsSummary.innerHTML = '<p>Your cart is empty</p>';
                        
                        // Redirect to cart page
                        window.location.href = '/cart';
                    } else {
                        // Render cart items
                        let html = '';
                        cartItems.forEach(item => {
                            html += `
                                <div class="summary-item">
                                    <div class="summary-item-image">
                                        <img src="${item.image}" alt="${item.cake_name}">
                                    </div>
                                    <div class="summary-item-details">
                                        <h4>${item.cake_name}</h4>
                                        <p>Qty: ${item.quantity} x ₹${item.price.toLocaleString()}</p>
                                    </div>
                                    <div class="summary-item-total">
                                        ₹${item.total.toLocaleString()}
                                    </div>
                                </div>
                            `;
                        });
                        
                        cartItemsSummary.innerHTML = html;
                        
                        // Update totals
                        if (summarySubtotal) {
                            summarySubtotal.textContent = `₹${data.cart_total.toLocaleString()}`;
                        }
                        
                        // Calculate final total
                        const subtotal = data.cart_total;
                        const deliveryFee = 50;
                        const discount = parseInt(summaryDiscount.textContent.replace(/[^\d]/g, '')) || 0;
                        const total = subtotal + deliveryFee - discount;
                        
                        if (summaryTotal) {
                            summaryTotal.textContent = `₹${total.toLocaleString()}`;
                        }
                    }
                } else {
                    cartItemsSummary.innerHTML = '<p class="error-message">Error loading cart. Please try again.</p>';
                }
            })
            .catch(error => {
                console.error('Error loading cart:', error);
                cartItemsSummary.innerHTML = '<p class="error-message">Error loading cart. Please try again.</p>';
            });
    }
    
    // Place order function
    function placeOrder(addressId, deliveryDate, paymentMethod, specialInstructions) {
        // Calculate total from summary
        const subtotalText = summarySubtotal.textContent;
        const subtotal = parseInt(subtotalText.replace(/[^\d]/g, '')) || 0;
        const deliveryFee = 50;
        const discountText = summaryDiscount.textContent;
        const discount = parseInt(discountText.replace(/[^\d]/g, '')) || 0;
        const total = subtotal + deliveryFee - discount;
        
        // Get coupon code if applied
        const couponInput = document.getElementById('coupon-code');
        const couponCode = couponInput ? couponInput.value.trim() : '';
        
        // Send order request
        fetch('/api/orders/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                shipping_address_id: addressId,
                delivery_date: deliveryDate,
                payment_method: paymentMethod,
                special_instructions: specialInstructions,
                total_amount: total,
                discount_code: couponCode
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide processing state
                orderProcessing.style.display = 'none';
                
                // Show confirmation
                orderConfirmation.style.display = 'block';
                
                // Update order number
                if (orderNumber) {
                    orderNumber.textContent = data.order_id;
                }
                
                // Update view order button
                if (viewOrderBtn) {
                    viewOrderBtn.href = `/order/${data.order_id}`;
                }
                
                // Update order summary
                if (orderSummary) {
                    // Get selected address details
                    const selectedAddressLabel = document.querySelector(`label[for="address-${addressId}"]`);
                    const addressDetails = selectedAddressLabel ? selectedAddressLabel.textContent.trim() : '';
                    
                    // Format delivery date
                    const formattedDate = new Date(deliveryDate).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    });
                    
                    // Format payment method
                    let paymentMethodText = 'Cash on Delivery';
                    if (paymentMethod === 'card') {
                        paymentMethodText = 'Credit/Debit Card';
                    } else if (paymentMethod === 'upi') {
                        paymentMethodText = 'UPI Payment';
                    }
                    
                    orderSummary.innerHTML = `
                        <div class="order-detail-row">
                            <span>Order Number:</span>
                            <span>${data.order_id}</span>
                        </div>
                        <div class="order-detail-row">
                            <span>Delivery Date:</span>
                            <span>${formattedDate}</span>
                        </div>
                        <div class="order-detail-row">
                            <span>Shipping Address:</span>
                            <span>${addressDetails}</span>
                        </div>
                        <div class="order-detail-row">
                            <span>Payment Method:</span>
                            <span>${paymentMethodText}</span>
                        </div>
                        <div class="order-detail-row">
                            <span>Total Amount:</span>
                            <span>₹${total.toLocaleString()}</span>
                        </div>
                    `;
                }
                
                // Update cart count to 0
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = '0';
                    cartCount.style.display = 'none';
                }
            } else {
                // Show error
                orderProcessing.style.display = 'none';
                showNotification(data.message || 'Failed to place order. Please try again.', 'error');
                
                // Go back to shipping step
                goToStep(0);
            }
        })
        .catch(error => {
            console.error('Error placing order:', error);
            orderProcessing.style.display = 'none';
            showNotification('An error occurred while placing your order. Please try again.', 'error');
            
            // Go back to shipping step
            goToStep(0);
        });
    }
    
    // Go to step function
    function goToStep(stepIndex) {
        // Hide all steps
        checkoutSteps.forEach(step => {
            step.classList.remove('active');
        });
        
        // Update step indicators
        checkoutStepIndicators.forEach((indicator, index) => {
            if (index <= stepIndex) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
        
        // Show selected step
        checkoutSteps[stepIndex].classList.add('active');
        
        // Scroll to top
        window.scrollTo(0, 0);
    }
    
    // Apply coupon functionality
    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    const couponCodeInput = document.getElementById('coupon-code');
    
    if (applyCouponBtn && couponCodeInput) {
        applyCouponBtn.addEventListener('click', function() {
            const couponCode = couponCodeInput.value.trim();
            
            if (!couponCode) {
                showNotification('Please enter a coupon code', 'error');
                return;
            }
            
            // Apply coupon
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
                    
                    // Update discount amount
                    if (summaryDiscount) {
                        summaryDiscount.textContent = `-₹${data.discount.toLocaleString()}`;
                    }
                    
                    // Recalculate total
                    const subtotal = parseInt(summarySubtotal.textContent.replace(/[^\d]/g, '')) || 0;
                    const deliveryFee = 50;
                    const discount = data.discount;
                    const total = subtotal + deliveryFee - discount;
                    
                    if (summaryTotal) {
                        summaryTotal.textContent = `₹${total.toLocaleString()}`;
                    }
                    
                    // Disable coupon input and button
                    couponCodeInput.disabled = true;
                    applyCouponBtn.disabled = true;
                } else {
                    showNotification(data.message || 'Invalid coupon code', 'error');
                }
            })
            .catch(error => {
                console.error('Error applying coupon:', error);
                showNotification('An error occurred while applying the coupon', 'error');
            });
        });
    }
});