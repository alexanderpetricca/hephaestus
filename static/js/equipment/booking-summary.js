function initializeListJS() {
    let options = {
        valueNames: [
            'sort-manufacturer',
            'sort-name',
            'sort-mount',
            'sort-category',
            'sort-serial',
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