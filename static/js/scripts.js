// scripts.js

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeModals();
    initializeForms();
    initializeCharts();
    setupEventListeners();
});

// Modal functionality
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close-modal, .btn-secondary');
    
    // Close modal when clicking close button
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    // Close modal when clicking outside
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        }
    });
}

// Form validation and handling
function initializeForms() {
    // Auto-calculate totals in sale form
    const saleForms = document.querySelectorAll('form');
    
    saleForms.forEach(form => {
        const quantityInput = form.querySelector('input[name="quantity"]');
        const priceInput = form.querySelector('input[name="price_per_unit"]');
        const totalInput = form.querySelector('input[name="total_amount"]');
        
        if (quantityInput && priceInput && totalInput) {
            function calculateTotal() {
                const quantity = parseFloat(quantityInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                totalInput.value = (quantity * price).toFixed(2);
            }
            
            quantityInput.addEventListener('input', calculateTotal);
            priceInput.addEventListener('input', calculateTotal);
        }
        
        // Form submission with validation
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const requiredInputs = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#e74c3c';
                    input.focus();
                } else {
                    input.style.borderColor = '#ddd';
                }
            });
            
            if (isValid) {
                // Show success message
                showAlert('Form submitted successfully!', 'success');
                
                // Close modal if in one
                const modal = this.closest('.modal');
                if (modal) {
                    modal.style.display = 'none';
                }
                
                // Reset form
                this.reset();
                
                // In a real app, you would send data to server here
                console.log('Form data:', new FormData(this));
            } else {
                showAlert('Please fill in all required fields.', 'error');
            }
        });
    });
}

// Chart initialization
function initializeCharts() {
    // This function can be extended for dynamic chart creation
    console.log('Charts initialized');
}

// Setup additional event listeners
function setupEventListeners() {
    // Logout confirmation
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    });
    
    // Table row actions
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on action buttons
            if (!e.target.closest('.btn')) {
                console.log('Row clicked:', this);
                // Add your row click logic here
            }
        });
    });
}

// Alert/Notification system
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-temporary');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-temporary`;
    alertDiv.textContent = message;
    
    // Style for temporary alerts
    Object.assign(alertDiv.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '9999',
        minWidth: '300px',
        maxWidth: '400px',
        padding: '15px',
        borderRadius: '5px',
        boxShadow: '0 5px 15px rgba(0,0,0,0.2)',
        animation: 'slideIn 0.3s ease'
    });
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        position: absolute;
        top: 5px;
        right: 10px;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: inherit;
        line-height: 1;
    `;
    
    closeBtn.addEventListener('click', () => alertDiv.remove());
    alertDiv.appendChild(closeBtn);
    
    // Add to document
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => alertDiv.remove(), 300);
        }
    }, 5000);
}

// Export data functions
function exportToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('th, td');
        
        cells.forEach(cell => {
            // Skip action columns
            if (!cell.closest('.actions')) {
                rowData.push(`"${cell.textContent.trim()}"`);
            }
        });
        
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = `${filename || 'export'}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Search functionality
function setupTableSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Date formatting helper
function formatDate(date) {
    if (!date) return 'N/A';
    
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Number formatting helper
function formatNumber(num) {
    return new Intl.NumberFormat('en-KE', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}

// Initialize tooltips (if using Bootstrap tooltips)
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.getAttribute('title');
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 0.85rem;
                z-index: 9999;
                white-space: nowrap;
            `;
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - 40) + 'px';
            tooltip.style.left = rect.left + 'px';
            
            this.appendChild(tooltip);
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            });
        });
    });
}

// Print report
function printReport() {
    window.print();
}

// Open modal function (for use in templates)
window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
};

// Close modal function
window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
};

// Dashboard refresh function
function refreshDashboard() {
    showAlert('Refreshing data...', 'info');
    
    // In a real app, you would fetch fresh data from the server
    setTimeout(() => {
        showAlert('Dashboard refreshed successfully!', 'success');
    }, 1000);
}

// Role-based UI adjustments
function applyRoleBasedUI() {
    const role = document.body.getAttribute('data-role') || 'user';
    
    // Hide admin-only elements for non-admin users
    if (role !== 'admin') {
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = 'none';
        });
    }
    
    // Hide financial elements for non-accountant users
    if (!['admin', 'accountant'].includes(role)) {
        document.querySelectorAll('.financial-only').forEach(el => {
            el.style.display = 'none';
        });
    }
}

// Initialize everything when page loads
window.addEventListener('load', function() {
    applyRoleBasedUI();
    initializeTooltips();
});