$(document).ready(function() {
    // Find the index of the column with the header "Status"
    var columnIndex = $('th:contains("Status")').index() + 1; // Adding 1 to convert to 1-based index

    // Loop through each cell in the identified column and apply styling
    $('td:nth-child(' + columnIndex + ')').each(function() {
        var value = $(this).text().trim(); // Trim any leading or trailing whitespaces
        
        // Customize the conditions and colors based on your string values
        if (value === 'Pending') {
            $(this).addClass('pending-value');
        } else if (value === 'Approved') {
            $(this).addClass('approved-value');
        } else if (value === 'Denied') {
            $(this).addClass('denied-value');
        } else if (value === 'Linked') {
            $(this).addClass('linked-value');
        }
    });
});
