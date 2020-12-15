// Javascript code for use within the Details page of ROCK DeCart.
//
// NOTE: URLS is a variable set in the HTML by the Django templating engine to allow for
// injection at page rendering time.
//


/*
 * Update the Funding Mechanism Table, either editing an existing row or appending a new one.
 * >> Called as part of the success function on an AJAX update to the server.
 */
function updateFundingTable(data) {
  if (data.success) {
      var rowData = '<td>' +
          '  <div class="btn-group">' +
          '    <button class="btn btn-sm edit-funding btn-success" title="Edit" type="button">' +
          '      <i class="fas fa-edit"></i>' +
          '    </button>' +
          '    <button class="btn btn-sm delete-funding btn-danger" title="Remove" type="button">' +
          '      <i class="far fa-trash-alt"></i>' +
          '    </button>' +
          '  </div>' +
          '</td>' +
          '<td>' + data.details + '</td>' +
          '<td>' + data.provider + '</td>' +
          '<td>' + data.provider_ownership + '</td>' +
          '<td>' + data.provider_type + '</td>' +
          '<td>' + data.currency + ' ' + data.amount + '</td>' +
          '<td>' + data.note + '</td>';
      
      // Check to see if this is a new funding mechanism or an existing one that was edited.
      var funding = $('#funding-' + data.pk);
      if (funding.length > 0) {
          // This is an existing funding mechanism so update the data rather than appending
          funding.html(rowData);
      } else {
          // This is a new funding mechanism so append the row to the table
          $("#project-funding").append('<tr id="funding-' + data.pk + '">' + rowData + '/<tr>');
      }

        // Bind the edit and delete buttons
        bindHandlers();
  } else {
      window.scrollTo(0, 0);
      setDecartAlertDiv('danger', 'Unable to add funding mechanism: do you have edit rights?');
  }
}


/*
 * Add a new form to the link formset and update the management form accordingly
 */
function add_link() {
    var form_idx = $('#id_form-TOTAL_FORMS').val();
    var tmp_html = $('#empty_link_form table tbody').html().replace(/__prefix__/g, form_idx);
    $('#link_table tbody').append(tmp_html);
    $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
    bindHandlers();
}


/*
 * Delete a link. We need to update the management form correctly to undo
 * additions made for records that are yet to be saved and mark those for
 * deletion that were added on page load.
 */
function delete_link(tr) {
    var result = confirm("Are you sure to delete this link?");
    if (result) {
        var delete_field = $('#id_' + tr.attr('id') + '-DELETE');
        if (delete_field.length > 0) {
            // This requires deletion on the server
            delete_field[0].value = 'on';
        }
        $(tr).hide();
    }
}


/*
 * Set _all_ of the button handlers following a page update.
 * XXX: This needs to be called any time we update the DOM otherwise the new elements won't
 *      have any registered handlers.
 */
function bindHandlers() {
    $('.btn-delete-link').unbind();
    $('.btn-delete-link').click(function() {
        var tr = $(this).closest('tr');
        delete_link(tr);
    });

    //bind edit funding mechanism function
    $('.edit-funding').on('click', function () {
        var tr = $(this).closest('tr');
        var fundingMechanismId = $(tr).attr('id').split('-')[1];
        var url = URLS.editFunding.replace(/0$/, fundingMechanismId);

        $.get(url, "", function (data) {
            if (data.success) {
                // Add in the new modal
                $('#modal-placeholder').html(data.html);

                // Bind the sumbit handler
                $('#funding-edit-form').submit(function (event) {
                    var formData = $(this).serializeArray();
                    formData.push({"name": "funding-id", "value": fundingMechanismId});

                    // Update the table if everything went ok
                    $.post(
                        url, formData, updateFundingTable, "json"
                    ).fail(
                        function() { decartServerError(); }
                    );

                    // Hide the modal again and remove the html
                    $('#funding-edit-modal').modal('hide');
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                    $('#modal-placeholder').html("");

                    // Cancel the default submission handling
                    event.preventDefault();
                });

                // Display the modal
                $('#funding-edit-modal').modal('show');
            } else {
                window.scrollTo(0, 0);
                setDecartAlertDiv('danger', 'Unable to get funding details.');
            }
        }, "json").fail(function() { decartServerError(); });
    });


    // Bind the deleteFundingMechanism function to each of the buttons in the
    // funding mechanism section.
    $('.delete-funding').on('click', function () {
        var result = confirm("Are you sure you want to remove this funding mechanism?");
        if (result) {
            var tr = $(this).closest('tr');
            var Id = $(tr).attr('id').split('-')[1];

            // Contact the server to request the delete
            decartDeleteById(
                URLS.deleteFunding,
                Id,
                function (data) { $(tr).remove(); },
                "Funding Mechanism"
            );
        }
    });


    $('.delete-partner').on('click', function () {
        var result = confirm("Are you sure you want to remove this partner?");
        if (result) {
            var tr = $(this).closest('tr');
            var Id = $(tr).attr('id').split('-')[1];
            var role = $(tr).attr('id').split('-')[2];

            // Contact the server to request the delete
            $.post(
                URLS.removeOrg,
                JSON.stringify({'id': Id, 'role': role}),
                function (data) {
                    if (data.success) {
                        $(tr).remove();
                        setDecartAlertDiv('success', 'Organisation remove successfully');
                    } else {
                        setDecartAlertDiv('danger', 'Unable to remove organisation: please try again later.');
                    }
                }, "json"
            ).fail(function() { decartServerError(); });
        }
    });
}


/*
 * Main jQuery handler function for page animations/form actions etc.
 */
$(document).ready(function() {
    // Set up the CSRF token details for use with AJAX requests
    setCSRFHeader();

    // Activate the selection boxes
    $('.select2-selection-box').select2();

    $('#add-funding-btn').click(function() {
        $('#funding-creator-modal').modal('show');
    });

    $('#add_link').click(function() { add_link(); });

    // Intercept the add funding mechanism form submission so we can inject the project ID
    $('#funding-creator-form').submit(function (event) {
        var formData = $(this).serializeArray();
        // Set in edit_project.html

        $.post(
            URLS.addFunding,
            formData,
            updateFundingTable,
            "json"
        ).fail(function() {
            decartServerError();
        });

        $('#funding-creator-modal').modal('hide');
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();

        // Cancel the default submission handling
        event.preventDefault();
    });
    
    $('#add-partner-btn').click(function() {
        $('#add-partner-modal').modal('show');
    });

    $('#btn-create-org').click(function() {
        $('#org-modal').modal('show');
    });

    $('#org-form').submit(function (event) {
        var formData = $(this).serializeArray();

        $.post(
            URLS.newOrg,
            formData,
            function(data) {
                if (data.success) {
                    var newOption = new Option(data.name, data.pk, true, true);
                    $("#partner-selector").append(newOption).trigger('change');
                    setDecartAlertDiv('success', 'Organisation created successfully');
                } else {
                    setDecartAlertDiv('danger', 'Unable to create new organisation: please try again later.');
                }
            }, "json"
        ).fail(function() { decartServerError(); });

        // Hide the modal
        $('#org-modal').modal('hide');

        // Cancel the default submission handling
        event.preventDefault();
    });

    $('#add-partner-form').submit(function (event) {
        var formData = $(this).serializeArray();

        $.post(
            URLS.addOrg,
            JSON.stringify({'id': formData[1].value, 'role': formData[2].value}),
            function(data) {
                if (data.success) {
                    var tmpContent = '<tr id="partner-' + data.pk + '">' +
                        '  <td>' + data.name + '</td>' +
                        '  <td>' + data.role + '</td>' +
                        '  <td>' + data.scale + '</td>' +
                        '  <td>' + data.type + '</td>' +
                        '  <td>' + data.email + '</td>' +
                        '  <td>' + data.phone + '</td>' +
                        '  <td>' + data.website + '</td>' +
                        '  <td>' + data.location + '</td>' +
                        '  <td>' + data.other + '</td>' +
                        '  <td class="option-1">' +
                        '    <button class="btn btn-sm delete-partner btn-danger" title="Remove" type="button">' +
                        '      <i class="far fa-trash-alt"></i>' +
                        '    </button>' +
                        '  </td>' +
                        '</tr>';

                    $("#project-partners").append(tmpContent);
                    bindHandlers();
                    setDecartAlertDiv('success', 'Organisation added successfully');
                } else {
                    setDecartAlertDiv('danger', 'Unable to add new organisation: please try again later.');
                }
            }, "json"
        ).fail(function() { decartServerError(); });

        // Hide the modal
        $('#add-partner-modal').modal('hide');

        // Cancel the default submission handling
        event.preventDefault();
    });


    // ----------------------------------------------------------------------------------------
    // Finally, bind all of the event handlers
    bindHandlers();
});
