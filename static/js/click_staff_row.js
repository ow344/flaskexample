// script.js

// Add an event listener to table rows
document.addEventListener('DOMContentLoaded', function() {
    var tableRows = document.querySelectorAll('table tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            var entryId = this.getAttribute('data-entry-id');
            if (entryId) {
                window.location.href = '/user/stafflist/staff/' + entryId;
            }
        });
    });
});
