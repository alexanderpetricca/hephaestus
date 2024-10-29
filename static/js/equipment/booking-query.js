function initializeListJS() {
    let options = {
        valueNames: [
            'sort-reference',
            'sort-bookedby',
            { attr: 'data-sort-start', name: 'sort-start'},
            { attr: 'data-sort-end', name: 'sort-end'},
            'sort-status',
        ],
        sortClass: 'listjs-sorter',
    };

    // Initialize List.js and store it in a global variable
    window.productList = new List('bookings', options);
}

// Call the initialization function when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeListJS();
});