/**
 * Happy Cake - Profile Management JavaScript
 * Handles user profile functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const profileTabs = document.querySelectorAll('.profile-tab');
    const profileTabContents = document.querySelectorAll('.profile-tab-content');
    
    // Address management
    const addAddressBtn = document.querySelector('.add-address-btn');
    const addAddressModal = document.getElementById('add-address-modal');
    const editAddressModal = document.getElementById('edit-address-modal');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    const newAddressForm = document.getElementById('new-address-form');
    const editAddressForm = document.getElementById('edit-address-form');
    
    // Profile settings
    const profileSettingsForm = document.getElementById('profile-settings-form');
    const passwordChangeForm = document.getElementById('password-change-form');
    const logoutBtn = document.getElementById('logout-btn');
    
    // Order management
    const loadMoreOrdersBtn = document.getElementById('load-more-orders');
    
    // Profile fields editing
    const editProfileBtns = document.querySelectorAll('.edit-profile-btn');
    const saveProfileBtns = document.querySelectorAll('.save-profile-btn');
    const cancelProfileBtns = document.querySelectorAll('.cancel-profile-btn');
    
    // Tab switching functionality
    if (profileTabs.length > 0) {
        profileTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                
                // Remove active class from all tabs and tab contents
                profileTabs.forEach(t => t.classList.remove('active'));
                profileTabContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                this.classList.add('active');
                document.getElementById(`${tabName}-tab`).classList.add('active');
                
                // Load tab-specific data if needed
                if (tabName === 'addresses') {
                    loadAddresses();
                }
                
                if (tabName === 'orders') {
                    loadOrders();
                }
            });
        });
    }
    
    // Add address modal
    if (addAddressBtn) {
        addAddressBtn.addEventListener('click', function() {
            if (addAddressModal) {
                // Reset form before showing
                if (newAddressForm) newAddressForm.reset();
                
                // Show modal
                addAddressModal.style.display = 'block';
            }
        });
    }
    
    // Close modals
    if (closeModalBtns.length > 0) {
        closeModalBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Hide all modals
                if (addAddressModal) addAddressModal.style.display = 'none';
                if (editAddressModal) editAddressModal.style.display = 'none';
            });
        });
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(e) {
        if (addAddressModal && e.target === addAddressModal) {
            addAddressModal.style.display = 'none';
        }
        if (editAddressModal && e.target === editAddressModal) {
            editAddressModal.style.display = 'none';
        }
    });
    
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
            
            // Validate required fields
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
                    
                    // Reset form and close modal
                    newAddressForm.reset();
                    if (addAddressModal) addAddressModal.style.display = 'none';
                    
                    // Reload addresses
                    loadAddresses();
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
    
    // Edit address form submission
    if (editAddressForm) {
        editAddressForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const addressId = document.getElementById('edit-address-id').value;
            const label = document.getElementById('edit-address-label').value;
            const line1 = document.getElementById('edit-address-line1').value;
            const line2 = document.getElementById('edit-address-line2').value;
            const city = document.getElementById('edit-address-city').value;
            const state = document.getElementById('edit-address-state').value;
            const postalCode = document.getElementById('edit-address-postal-code').value;
            const phone = document.getElementById('edit-address-phone').value;
            const isDefault = document.getElementById('edit-address-default').checked;
            
            // Validate required fields
            if (!label || !line1 || !city || !state || !postalCode) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Updating...';
            submitBtn.disabled = true;
            
            // Send request to update address
            fetch(`/api/user/addresses/${addressId}`, {
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
                    showNotification('Address updated successfully', 'success');
                    
                    // Close modal
                    if (editAddressModal) editAddressModal.style.display = 'none';
                    
                    // Reload addresses
                    loadAddresses();
                } else {
                    showNotification(data.message || 'Failed to update address', 'error');
                }
            })
            .catch(error => {
                console.error('Error updating address:', error);
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Profile settings form submission
    if (profileSettingsForm) {
        profileSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const name = document.getElementById('settings-name').value;
            const phone = document.getElementById('settings-phone').value;
            
            // Validate required fields
            if (!name) {
                showNotification('Please enter your name', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Saving...';
            submitBtn.disabled = true;
            
            // Send request to update profile
            fetch('/api/user/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    phone: phone
                })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    showNotification('Profile updated successfully', 'success');
                    
                    // Update profile name in header
                    const profileName = document.getElementById('profile-name');
                    if (profileName) {
                        profileName.textContent = name;
                    }
                } else {
                    showNotification(data.message || 'Failed to update profile', 'error');
                }
            })
            .catch(error => {
                console.error('Error updating profile:', error);
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Password change form submission
    if (passwordChangeForm) {
        passwordChangeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Validate fields
            if (!currentPassword || !newPassword || !confirmPassword) {
                showNotification('Please fill in all fields', 'error');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                showNotification('New passwords do not match', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Changing...';
            submitBtn.disabled = true;
            
            // Send request to change password
            fetch('/api/user/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            })
            .then(response => response.json())
            .then(data => {
                // Reset button
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    showNotification('Password changed successfully', 'success');
                    
                    // Reset form
                    passwordChangeForm.reset();
                } else {
                    showNotification(data.message || 'Failed to change password', 'error');
                }
            })
            .catch(error => {
                console.error('Error changing password:', error);
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Logout button
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            fetch('/auth/logout')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('Logged out successfully', 'success');
                        
                        // Redirect to home page
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 1000);
                    } else {
                        showNotification('Failed to logout', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error logging out:', error);
                    showNotification('An error occurred. Please try again.', 'error');
                });
        });
    }
    
    // Load more orders
    if (loadMoreOrdersBtn) {
        loadMoreOrdersBtn.addEventListener('click', function() {
            // Get current page number
            const currentPage = parseInt(this.getAttribute('data-page')) || 1;
            const nextPage = currentPage + 1;
            
            // Show loading state
            this.innerHTML = '<span class="loading-spinner"></span> Loading...';
            this.disabled = true;
            
            // Fetch next page of orders
            fetch(`/api/user/orders?page=${nextPage}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Append orders to the list
                        appendOrders(data.orders);
                        
                        // Update button
                        this.setAttribute('data-page', nextPage);
                        this.innerHTML = 'Load More Orders';
                        this.disabled = false;
                        
                        // Hide button if no more orders
                        if (!data.has_more) {
                            this.style.display = 'none';
                        }
                    } else {
                        // Reset button
                        this.innerHTML = 'Load More Orders';
                        this.disabled = false;
                        
                        showNotification(data.message || 'Failed to load more orders', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error loading more orders:', error);
                    // Reset button
                    this.innerHTML = 'Load More Orders';
                    this.disabled = false;
                    showNotification('An error occurred. Please try again.', 'error');
                });
        });
    }
    
    // Profile fields editing
    if (editProfileBtns.length > 0) {
        editProfileBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const field = this.getAttribute('data-field');
                const valueEl = document.getElementById(`profile-${field}-value`);
                const editEl = document.getElementById(`profile-${field}-edit`);
                
                if (valueEl && editEl) {
                    valueEl.style.display = 'none';
                    editEl.style.display = 'flex';
                    
                    // Focus on input
                    const input = editEl.querySelector('input');
                    if (input) input.focus();
                }
            });
        });
    }
    
    if (saveProfileBtns.length > 0) {
        saveProfileBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const field = this.getAttribute('data-field');
                const valueEl = document.getElementById(`profile-${field}-value`);
                const editEl = document.getElementById(`profile-${field}-edit`);
                const input = editEl.querySelector('input');
                
                if (valueEl && editEl && input) {
                    const value = input.value.trim();
                    
                    if (!value) {
                        showNotification(`Please enter a valid ${field}`, 'error');
                        return;
                    }
                    
                    // Show loading
                    const loadingIndicator = document.getElementById('profile-loading');
                    if (loadingIndicator) loadingIndicator.style.display = 'block';
                    
                    // Update field
                    const data = {};
                    data[field] = value;
                    
                    fetch('/api/user/profile/update-field', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (loadingIndicator) loadingIndicator.style.display = 'none';
                        
                        if (data.success) {
                            // Update value
                            valueEl.querySelector('span').textContent = value;
                            
                            // Switch back to display mode
                            valueEl.style.display = 'flex';
                            editEl.style.display = 'none';
                            
                            showNotification('Profile updated successfully', 'success');
                            
                            // Update profile name in header if changing name
                            if (field === 'name') {
                                const profileName = document.getElementById('profile-name');
                                if (profileName) {
                                    profileName.textContent = value;
                                }
                            }
                        } else {
                            showNotification(data.message || 'Failed to update profile', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error updating profile field:', error);
                        if (loadingIndicator) loadingIndicator.style.display = 'none';
                        showNotification('An error occurred. Please try again.', 'error');
                    });
                }
            });
        });
    }
    
    if (cancelProfileBtns.length > 0) {
        cancelProfileBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const field = this.getAttribute('data-field');
                const valueEl = document.getElementById(`profile-${field}-value`);
                const editEl = document.getElementById(`profile-${field}-edit`);
                const input = editEl.querySelector('input');
                
                if (valueEl && editEl && input) {
                    // Reset input value
                    const originalValue = valueEl.querySelector('span').textContent;
                    input.value = originalValue;
                    
                    // Switch back to display mode
                    valueEl.style.display = 'flex';
                    editEl.style.display = 'none';
                }
            });
        });
    }
    
    // Load user addresses
    function loadAddresses() {
        const addressesContainer = document.querySelector('.address-list');
        if (!addressesContainer) return;
        
        // Show loading
        addressesContainer.innerHTML = '<div class="loading-placeholder"></div>';
        
        fetch('/api/user/addresses')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const addresses = data.addresses;
                    
                    if (addresses.length === 0) {
                        addressesContainer.innerHTML = '<p>You have no saved addresses. Please add a new address.</p>';
                    } else {
                        let html = '';
                        addresses.forEach(address => {
                            html += `
                                <div class="address-card" data-id="${address.id}">
                                    <div class="address-header">
                                        <h5>${address.label}</h5>
                                        <div class="address-actions">
                                            <button class="edit-btn" onclick="editAddress(${address.id})">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="delete-btn" onclick="deleteAddress(${address.id})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                    <p>${address.address_line1}</p>
                                    ${address.address_line2 ? `<p>${address.address_line2}</p>` : ''}
                                    <p>${address.city}, ${address.state} ${address.postal_code}</p>
                                    ${address.phone ? `<p>Phone: ${address.phone}</p>` : ''}
                                    ${address.is_default ? '<p class="default-badge">Default</p>' : ''}
                                </div>
                            `;
                        });
                        
                        addressesContainer.innerHTML = html;
                    }
                } else {
                    addressesContainer.innerHTML = '<p class="error-message">Failed to load addresses. Please try again.</p>';
                }
            })
            .catch(error => {
                console.error('Error loading addresses:', error);
                addressesContainer.innerHTML = '<p class="error-message">An error occurred while loading addresses. Please try again.</p>';
            });
    }
    
    // Load user orders
    function loadOrders(page = 1) {
        const ordersContainer = document.querySelector('.order-list');
        if (!ordersContainer) return;
        
        // Show loading if first page
        if (page === 1) {
            ordersContainer.innerHTML = '<div class="loading-placeholder"></div>';
        }
        
        fetch(`/api/user/orders?page=${page}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const orders = data.orders;
                    
                    if (orders.length === 0 && page === 1) {
                        ordersContainer.innerHTML = '<p>You have no orders yet.</p>';
                    } else {
                        let html = '';
                        orders.forEach(order => {
                            let itemsHtml = '';
                            order.items.forEach(item => {
                                itemsHtml += `
                                    <div class="order-product">
                                        <img src="${item.image}" alt="${item.cake_name}">
                                        <div>
                                            <p class="product-name">${item.cake_name}</p>
                                            <p class="product-quantity">Qty: ${item.quantity} x ₹${item.price.toLocaleString()}</p>
                                        </div>
                                    </div>
                                `;
                            });
                            
                            html += `
                                <div class="order-item">
                                    <div class="order-header">
                                        <div>
                                            <span class="order-id">${order.order_id}</span>
                                            <span class="order-date">${order.order_date}</span>
                                        </div>
                                        <span class="order-status">${order.status}</span>
                                    </div>
                                    <div class="order-products">
                                        ${itemsHtml}
                                    </div>
                                    <div class="order-footer">
                                        <div class="order-total">Total: ₹${order.total_amount.toLocaleString()}</div>
                                        <a href="/order/${order.order_id}" class="view-order-btn">View Details</a>
                                    </div>
                                </div>
                            `;
                        });
                        
                        // If first page, replace content, otherwise append
                        if (page === 1) {
                            ordersContainer.innerHTML = html;
                        } else {
                            ordersContainer.innerHTML += html;
                        }
                        
                        // Update load more button
                        if (loadMoreOrdersBtn) {
                            loadMoreOrdersBtn.setAttribute('data-page', page);
                            loadMoreOrdersBtn.style.display = data.has_more ? 'block' : 'none';
                        }
                    }
                } else {
                    if (page === 1) {
                        ordersContainer.innerHTML = '<p class="error-message">Failed to load orders. Please try again.</p>';
                    } else {
                        showNotification('Failed to load more orders', 'error');
                    }
                }
            })
            .catch(error => {
                console.error('Error loading orders:', error);
                if (page === 1) {
                    ordersContainer.innerHTML = '<p class="error-message">An error occurred while loading orders. Please try again.</p>';
                } else {
                    showNotification('An error occurred while loading more orders', 'error');
                }
            });
    }
    
    // Append orders to the list (for load more)
    function appendOrders(orders) {
        const ordersContainer = document.querySelector('.order-list');
        if (!ordersContainer || !orders || orders.length === 0) return;
        
        let html = '';
        orders.forEach(order => {
            let itemsHtml = '';
            order.items.forEach(item => {
                itemsHtml += `
                    <div class="order-product">
                        <img src="${item.image}" alt="${item.cake_name}">
                        <div>
                            <p class="product-name">${item.cake_name}</p>
                            <p class="product-quantity">Qty: ${item.quantity} x ₹${item.price.toLocaleString()}</p>
                        </div>
                    </div>
                `;
            });
            
            html += `
                <div class="order-item">
                    <div class="order-header">
                        <div>
                            <span class="order-id">${order.order_id}</span>
                            <span class="order-date">${order.order_date}</span>
                        </div>
                        <span class="order-status">${order.status}</span>
                    </div>
                    <div class="order-products">
                        ${itemsHtml}
                    </div>
                    <div class="order-footer">
                        <div class="order-total">Total: ₹${order.total_amount.toLocaleString()}</div>
                        <a href="/order/${order.order_id}" class="view-order-btn">View Details</a>
                    </div>
                </div>
            `;
        });
        
        // Append to container
        ordersContainer.innerHTML += html;
    }
    
    // Edit address function (global scope)
    window.editAddress = function(addressId) {
        if (!editAddressModal) return;
        
        // Show loading
        editAddressModal.querySelector('form').innerHTML = '<div class="loading-placeholder"></div>';
        
        // Show modal
        editAddressModal.style.display = 'block';
        
        // Fetch address details
        fetch(`/api/user/addresses/${addressId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const address = data.address;
                    
                    // Fill form
                    document.getElementById('edit-address-id').value = address.id;
                    document.getElementById('edit-address-label').value = address.label;
                    document.getElementById('edit-address-line1').value = address.address_line1;
                    document.getElementById('edit-address-line2').value = address.address_line2 || '';
                    document.getElementById('edit-address-city').value = address.city;
                    document.getElementById('edit-address-state').value = address.state;
                    document.getElementById('edit-address-postal-code').value = address.postal_code;
                    document.getElementById('edit-address-phone').value = address.phone || '';
                    document.getElementById('edit-address-default').checked = address.is_default;
                } else {
                    // Error fetching address
                    showNotification(data.message || 'Failed to load address details', 'error');
                    editAddressModal.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error fetching address:', error);
                showNotification('An error occurred while loading address details', 'error');
                editAddressModal.style.display = 'none';
            });
    };
    
    // Delete address function (global scope)
    window.deleteAddress = function(addressId) {
        if (!confirm('Are you sure you want to delete this address?')) return;
        
        fetch(`/api/user/addresses/${addressId}/delete`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Address deleted successfully', 'success');
                    
                    // Reload addresses
                    loadAddresses();
                } else {
                    showNotification(data.message || 'Failed to delete address', 'error');
                }
            })
            .catch(error => {
                console.error('Error deleting address:', error);
                showNotification('An error occurred while deleting the address', 'error');
            });
    };
    
    // Initialize - load addresses and orders if on profile page
    const activeTab = document.querySelector('.profile-tab.active');
    if (activeTab) {
        const tabName = activeTab.getAttribute('data-tab');
        
        if (tabName === 'addresses') {
            loadAddresses();
        }
        
        if (tabName === 'orders') {
            loadOrders();
        }
    }
});