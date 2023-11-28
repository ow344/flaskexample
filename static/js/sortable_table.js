$(document).ready(function() {
    // Function to toggle sorting on column header click
    $('th').click(function() {
        var table = $(this).parents('table').eq(0);
        var rows = table.find('tr:gt(0)').toArray().sort(comparator($(this).index()));

        this.asc = !this.asc;
        if (!this.asc) {
            rows = rows.reverse();
        }
        for (var i = 0; i < rows.length; i++) {
            table.append(rows[i]);
        }
    });

    // Comparator function for sorting
    function comparator(index) {
        return function(a, b) {
            var valA = $(a).children('td').eq(index).text().toUpperCase();
            var valB = $(b).children('td').eq(index).text().toUpperCase();
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.localeCompare(valB);
        };
    }
});