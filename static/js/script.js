/**
 * Happy Cake - Main JavaScript File
 * Handles common functionality across the website
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize cart count badge
    updateCartCount();
    
    // Search functionality
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', function() {
            performSearch();
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    // Close flash messages
    const closeButtons = document.querySelectorAll('.close-flash');
    if (closeButtons.length > 0) {
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                this.parentElement.remove();
            });
        });
        
        // Auto-hide flash messages after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.flash-message').forEach(message => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 500);
            });
        }, 5000);
    }
    
    // Search function
    function performSearch() {
        const searchTerm = searchInput.value.trim();
        
        if (searchTerm === '') {
            showNotification('Please enter a search term', 'error');
            return;
        }
        
        // Redirect to menu page with search parameter
        window.location.href = `/menu?search=${encodeURIComponent(searchTerm)}`;
    }
    
    // Function to show notification
    window.showNotification = function(message, type = 'success') {
        const notificationContainer = document.getElementById('notification-container');
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = message;
        
        // Add to container
        notificationContainer.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    };
    
    // Function to update cart count badge
    function updateCartCount() {
        // Only fetch cart count if user is logged in
        if (document.getElementById('profile-btn')) {
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
                    console.error('Error fetching cart count:', error);
                });
        }
    }
    
    // Expose updateCartCount to global scope
    window.updateCartCount = updateCartCount;
});