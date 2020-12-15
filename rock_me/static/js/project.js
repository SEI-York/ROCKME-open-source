/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');


// Animations //

// Rotate clockwise 90 degrees (See project.scss for animation code)
function rotateRight90(id) {
    $("#" + id).toggleClass("rotated-image");
}

// Add a datepicker to a newly created date field
function createDateField() {
    $(".datepicker:not(.hasDatepicker)").datepicker({
        format: 'dd/mm/yy',
        changeYear: true,
        changeMonth: true,
    });
}


// Pull the django CSRF token out of the environment for use within AJAX calls.
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set which methods require a CSRF token when using AJAX.
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Set the CSRF header field for AJAX requests.
function setCSRFHeader() {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}


// Set a bootstrap alert div at the head of the page.
// `type` must be one of: success, info, warning, danger.
function setDecartAlertDiv(type, message) {
    data = $('<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">'
            + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'
            + '<span aria-hidden="true">&times;</span>'
            + '</button>'
            + message
            + '</div>');

    // Set the alert with a timeout of 6 seconds
    $('#ajax-errors').html(data);
    setTimeout(function () {
        $(data).remove();
    }, 10000);
}

// Some canned default messages
function decartServerError() {
    window.scrollTo(0, 0)
    setDecartAlertDiv('danger', 'Oops! Something went wrong on the server... Please try again later')
}

function decartPermissionDenied() {
    window.scrollTo(0, 0)
    setDecartAlertDiv('warning', 'Oops! You\'re not allowed to do that!')
}


// Simple AJAX DELETE via JSON POST with id payload
function decartDeleteById(url, Id, onSuccess, name) {
    $.post(
        url,
        JSON.stringify({ id: Id }),
        function(data) {
            if (data['success']) {
                setDecartAlertDiv('success', name + ' removed successfully.');
                onSuccess(data);
            } else {
                window.scrollTo(0, 0)
                setDecartAlertDiv('danger', 'Unable to delete ' + name + '.');
            }
        },
      "json"
    ).fail(function() {
        decartServerError()
        // TODO :: Email details to the issue tracker?
    });
}

// Submit JSON data to an enpoint via AJAX
function decartAjaxJson(url, data, onSuccess) {
    $.post(
        url,
        JSON.stringify(data),
        onSuccess(data),
      "json"
    ).fail(function() {
        decartServerError()
    });
}



// Convert an HTML table to a string csv representation and then
// open a download dialogue for the user to click.
//
// Example usage:
// <button onclick="downloadTableAsCSV('#table-name', 'export.csv')">
//     Export As CSV
// </button>
function downloadTableAsCSV(tableID, filename) {
    var csv = [];
    // Glob all rows in the target table
    var rows = document.querySelectorAll(tableID + " tr");
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");

        for (var j = 0; j < cols.length; j++) {
            // Wrap in quotes so that cells with commas don't screw up the export
            row.push('"' + cols[j].innerText + '"');
        }
        csv.push(row.join(","));        
    }

    // Create our CSV file data from our csv string-array
    var csvFile = new Blob([csv.join("\n")], {type: "text/csv"});

    // Create a download link for the csv data and hide it
    var downloadLink = document.createElement("a");
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);

    // Click the download link to open the file dialogue
    downloadLink.click();
}
