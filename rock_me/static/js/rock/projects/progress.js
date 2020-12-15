// Javascript code for use within the Progress page of ROCK DeCart.
//
// NOTE: URLS is a variable set in the HTML by the Django templating engine to allow for
// injection at page rendering time.
//

/*
 * Handle the submission of the dynamically added state edit form.
 * NOTE: The url is specific to the state being edited and is passed in by the caller
 *       which is the submission handler for the edit-state-form
 */
function updateStateTable(data, indicatorPk) {
    if (data.success) {
        var dateString =  moment(data.start_date).format('DD/MM/YYYY') ;
        if(data.end_date){
            dateString+= ' - '+moment(data.end_date).format('DD/MM/YYYY');
        }


        var rowData = '<td  class="option-2">' +
          '  <div class="btn-group btn-group-sm" role="group">' +
          '    <button class="btn edit-state btn-success" title="Edit" type="button">' +
          '      <i class="fas fa-edit"></i>' +
          '    </button>' +
          '    <button class="btn delete-state btn-danger" title="Delete" type="button">' +
          '      <i class="far fa-trash-alt"></i>' +
          '    </button>' +
          '  </div>' +
          '</td>' +
          '<td>' + data.state + '</td>' +
          '<td>' +dateString+ '</td>';

        // Check to see if this is a new marker or an existing one that was edited.
        var state = $('#state-' + indicatorPk + '-' + data.pk);
        if (state.length > 0) {
            // This is an existing state so update the data rather than appending
            state.html(rowData);
        } else {
            // This is a new state so append the row to the table
            $('#indicator-' + indicatorPk).append(
                '<tr id="state-' + indicatorPk + '-' + data.pk + '">' + rowData + '/<tr>'
            );
        }
    } else {
        window.scrollTo(0, 0);
        setDecartAlertDiv('danger', 'Unable to add state: do you have edit rights?');
    }
}

/**
 * Reset data in state form
 */
function restStateForm(){
    //remove stashed data
    $('#state-modal').removeData('indicator-id');

    $('#state-form').trigger("reset");
    $('#link_table tbody').empty();
    $('#id_form-TOTAL_FORMS').val(0);
    //add one row for link
    $('#add_link').click();
}


/*
 * Set the button handlers for states following a page update.
 * XXX: This needs to be called any time we update the DOM otherwise the new elements won't
 *      have any registered handlers.
 */
function bindStateHandlers() {
    $('#wrapper').on('click', '.btn-delete', function() {
        var tr = $(this).closest('tr');
        delete_record(tr);
    });

    // ADD an indicator state - inline with each indicator.
    $('#wrapper').on('click', '.add-state', function () {
        // Relies on the ID being `add-state-<indicator_id>`
        var ID = $(this).attr('id').split("-")[2];

        //clear state form data
        restStateForm();

        //update form action
        $('#state-form').attr('action', URLS.addState.replace(/0$/, ID));

        // Set the indicator ID for the form to pick up later
        $('#state-modal').data('indicator-id', ID);

        $('#state-modal .modal-title').text('Add A New State');

        // Show the user the modal.
        $('#state-modal').modal('show');
    });
    

    // EDIT a state - inline with each state.
    // This fetches and displays the form while the inner function handles the submission
    $('#wrapper').on('click', '.edit-state', function () {
        var tr = $(this).closest('tr');
        var indicatorId = tr[0].id.split('-')[1];
        var stateId = tr[0].id.split('-')[2];
        var url = URLS.editState.replace(/0$/, stateId);

        $.get(url, "", function (data) {
            if (data.success) {
                //update form URL (might not needed)
                $('#state-form').attr('action', url);

                // Add data to form
                restStateForm();
                $('#state-modal').data('indicator-id', indicatorId);
                $('#state-form input[name="state"]').val(data.data['state']);
                $('#state-form input[name="start_date"]').val(data.data['start_date']);
                $('#state-form input[name="end_date"]').val(data.data['end_date']);
                $('#state-form textarea[name="evidence"]').val(data.data['evidence']);
                for (var i = 0; i < data.data['external_links'].length; i++) {
                    var form_idx = $('#id_form-TOTAL_FORMS').val() - 1;
                    var name = 'form-'+form_idx+'-url';
                    $('#state-form input[name="'+name+'"]').val(data.data['external_links'][i]);
                    //add more rows
                    add_record();
                }
                
                $('#state-modal .modal-title').text('Edit State');

                // Display the modal
                $('#state-modal').modal('show');
            } else {
                window.scrollTo(0, 0);
                setDecartAlertDiv('danger', 'Unable to get state details.');
            }
        }, "json").fail(function() { decartServerError(); });
    });


    // DELETE an indicator state - inline with each state.
    $('#wrapper').on('click', '.delete-state', function () {
        var result = confirm("Are you sure you want to remove this indicator state?");
        if (result) {
            var tr = $(this).closest('tr');
            // state-<indicator_id><state_id>
            var Id = tr[0].id.split('-')[2];

            // Contact the server to request the delete
            decartDeleteById(
                URLS.deleteState,
                Id,
                function (data) { $(tr).remove(); },
                "Indicator State"
            );
        }
    });
}

/*
 * Add a new form to the link formset and update the management form accordingly
 */
function add_record() {
    var form_idx = $('#id_form-TOTAL_FORMS').val();
    var tmp_html = $('#empty_link_form table tbody').html().replace(/__prefix__/g, form_idx);
    $('#link_table tbody').append(tmp_html);
    $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
}


/*
 * Delete a link. We need to update the management form correctly to undo
 * additions made for records that are yet to be saved and mark those for
 * deletion that were added on page load.
 */
function delete_record(tr) {
    var result = confirm("Are you sure to delete this link?");
    if (result) {
        $(tr).remove();
    }
}

/*
 * Main jQuery handler function for page animations/form actions etc.
 */
$(document).ready(function() {
    // Set up the CSRF token details for validating AJAX requests.
    setCSRFHeader();

    // Catch the submission of the modal and inject the table ID from the button.
    $('#state-form').submit(function (event) {
        var formData = $(this).serializeArray();
        var indicatorId = $('#state-modal').data('indicator-id');
        formData.push({"name": "indicator-id", "value": indicatorId});

        $.post(
            $(this).attr('action'),
            formData,
            function(data) { updateStateTable(data, indicatorId); },
            "json"
        ).fail(function() { decartServerError(); });

        // Hide the modal again
        $('#state-modal').modal('hide');

        // Cancel the default submission handling
        event.preventDefault();
    });


    $('#add_link').click(function() { add_record(); });

    // ----------------------------------------------------------------------------------------
    // Finally, bind all of the event handlers
    bindStateHandlers();
});
