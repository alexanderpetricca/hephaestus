function focusBarcodeInput () {
    const barcodeInput = document.querySelector('#item-barcode-scan')
    barcodeInput.focus()
}

document.addEventListener('DOMContentLoaded', function() {
    focusBarcodeInput();
});