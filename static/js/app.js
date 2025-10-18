// Financial Intelligence System - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Financial Intelligence System loaded');
    
    // Auto-uppercase stock symbols
    const symbolInputs = document.querySelectorAll('input[name="symbol"]');
    symbolInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });
    
    // Form submission loading state - ONLY for analyze forms
    const analyzeForms = document.querySelectorAll('form[action="/analyze"]');
    analyzeForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
            }
        });
    });
});

// API Helper Functions
async function analyzeStock(symbol, period = '1y') {
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol, period })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        return await response.json();
    } catch (error) {
        console.error('Health check failed:', error);
        return null;
    }
}

// Export functions
window.FinancialIntelligence = {
    analyzeStock,
    checkSystemHealth
};