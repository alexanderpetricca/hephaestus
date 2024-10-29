document.addEventListener('DOMContentLoaded', function () {
    
    // Category Field
    const categoryField = document.getElementById("id_category");
    if (categoryField && !categoryField.classList.contains('choices__input')) {
        new Choices(categoryField, {
            searchEnabled: true,
            shouldSort: false,
            placeholder: true,
            placeholderValue: 'Search categories',
            searchPlaceholderValue: 'Search categories',
            searchFields: ['label',],            
            allowHTML: false,
        });
    }

    // Manufacturing Field
    const manufacturerField = document.getElementById("id_manufacturer");
    if (manufacturerField && !manufacturerField.classList.contains('choices__input')) {
        new Choices(manufacturerField, {
            searchEnabled: true,
            shouldSort: false,
            placeholder: true,
            placeholderValue: 'Search manufacturers',
            searchPlaceholderValue: 'Search manufacturers',
            searchFields: ['label',],            
            allowHTML: false,
        });
    }        
})