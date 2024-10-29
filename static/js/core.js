// Disables button and displays spinner icon on submit button when clicked
function buttonSpinner(formID, buttonID){
    const form = document.getElementById(formID)
    const button = document.getElementById(buttonID)

    form.addEventListener('submit', (e) => {
        button.disabled = true
        button.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>';
    });
}


// Copies the provided data to the clipboard
function clickToCopyData(clickedID, data='') {

    const clicked = document.getElementById(clickedID)
    const currentContent = clicked.innerHTML
  
    navigator.clipboard.writeText(data).then(() => {
            console.log('Copied to clipboard.');
        }, (err) => {
            console.error('Async: Could not copy text: ', err);
        });
  
    clicked.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" width="18" height="18" fill="currentColor">
            <path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/>
        </svg>
    `

    // Revert the button content after 1 second
    setTimeout(function () {
        clicked.innerHTML = currentContent;
    }, 1000);
}