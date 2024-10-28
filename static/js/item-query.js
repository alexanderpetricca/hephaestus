function focusBarcodeInput () {
    const barcodeInput = document.querySelector('#item-barcode-scan')
    barcodeInput.focus()
}

document.addEventListener('DOMContentLoaded', function() {
    focusBarcodeInput();
});

function initializeListJS() {
    let options = {
        valueNames: [
            'sort-manufacturer',
            'sort-name',
            'sort-category',
            'sort-serial',
            'sort-assigned',
            'sort-status',
            'sort-availability',
        ],
        sortClass: 'listjs-sorter',
    };

    // Initialize List.js and store it in a global variable
    window.productList = new List('items', options);
}

// Call the initialization function when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeListJS();
});