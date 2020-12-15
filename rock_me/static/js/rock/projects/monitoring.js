// Javascript code for use within the monitoring and evaluation page of ROCK DeCart.
// There are a number of AJAX handlers set up for making DB edits without reloading the page
// every time a new outcome/marker is added. This means that we have a lot of state being managed
// (compared to the rest of the site).
//
// NOTE: URLS is a variable set in the HTML by the Django templating engine to allow for
// injection at page rendering time.


/*
 * Template for injecting a new outcome into the DOM once it has been approved by the server.
 * partnerPk and outcomePk are used to ensure that the accordian animations are correctly tied
 * to the toggle buttons.
 */
function getOutcomeHTML(partnerPk, outcomePk, description, outcomeNum) {
    return '<div id="outcome-' + outcomePk + '">' +
        '  <h4>' +
        '    <a class="text-info" data-toggle="collapse" href="#collapse-' + partnerPk + '-' + outcomePk + '">' +
        '      <button class="btn btn-light btn-sm btn-toggle-collapse">' +
        '        <i class="fas fa-angle-down"></i>' +
        '      </button>' +
        '    </a>' +
        '    Outcome ' + outcomeNum + ' - ' + description +
        '    <div class="float-right">' +
        '      <button class="btn btn-info add-indicator" title="Add an indicator" ' +
        '       type="button" data-partner-id="' + partnerPk + '" data-outcome-id="' + outcomePk + '">' +
        '        Add an Indicator' +
        '      </button>' +
        '      <button type="button" title="Edit outcome ' + outcomeNum + '" class="btn btn-success edit-outcome" data-id="' + outcomePk + '">' +
        '           <i class="fas fa-edit"></i>' +
        '      </button>' +
        '      <button data-id="' + outcomePk + '" class="btn btn-danger delete-outcome" title="Delete outcome ' + outcomeNum + '" type="button">' +
        '        <i class="far fa-trash-alt"></i>' +
        '      </button>' +
        '    </div>' +
        '  </h4>' +
        '  <div id="collapse-' + partnerPk + '-' + outcomePk + '" class="collapse show" role="tabpanel">' +
        '    <br/><br/>' +
        '    <table id="indicators-' + partnerPk + '-' + outcomePk + '" class="table table-bordered decart-table">' +
        '      <thead class="thead-dark">' +
        '        <tr>' +
        '          <th>Indicator</th>' +
        '          <th>Measure</th>' +
        '          <th>Means of Verification</th>' +
        '          <th>Baseline State</th>' +
        '          <th>Date of Baseline</th>' +
        '          <th class="option-2"></th>' +
        '        </tr>' +
        '      </thead>' +
        '      <tbody>' +
        '           <tr id="no-indicators-' + outcomePk + '">' +
        '               <td colspan="6">There are no indicators defined.</td>' +
        '           </tr>' +
        '      </tbody>' +
        '    </table>' +
        '  </div>' +
        '  <br>' +
        '</div>'
}


/*
 * Update the Progress Marker Table, either editing an existing row or appending a new one.
 * >> Called as part of the success function on an AJAX update to the server.
 */
function updateProgressMarkerTable(data) {
    if (data['success']) {
        var rowData = '<td>' + data['description'] + '</td>' +
            '<td>' + data['partner'] + '</td>' +
            '<td>' + data['outcome'] + '</td>' +
            '<td>' + data['level'] + '</td>' +
            '<td>' + moment(data['planned_completion_date']).format('DD/MM/YYYY') + '</td>' +
            '<td class="option-2">' +
            '<div class="btn-group btn-group-sm" role="group">' +
            '  <button class="btn edit-marker btn-success" title="Edit" type="button">' +
            '    <i class="fas fa-edit"></i>' +
            '  </button>' +
            '  <button class="btn delete-marker btn-danger" title="Delete this marker" type="button">' +
            '    <i class="far fa-trash-alt"></i>' +
            '  </button>' +
            '</div>' +
            '</td>' +
            '</tr>';

        // Check to see if this is a new marker or an existing one that was edited.
        var marker = $('#marker-' + data['pk']);
        if (marker.length > 0) {
            // This is an existing marker so update the data rather than appending
            marker.html(rowData);
        } else {
            // This is a new marker so append the row to the table
            $("#progress-markers").append('<tr id="marker-' + data['pk'] + '">' + rowData + '/<tr>');
        }
    } else {
        window.scrollTo(0, 0)
        setDecartAlertDiv('danger', 'Unable to add marker: do you have edit rights?')
    }
}


/*
 * Handle the submission of the dynamically added progress-marker edit form.
 * NOTE: The url is specific to the marker being edited and is passed in by the caller
 *       which is the submission handler for the edit-marker-form
 */
function handleMarkerEdit(formData, url, pk) {
    $.post(url, formData, updateProgressMarkerTable, "json").fail(function () {
        decartServerError()
    });

    // Hide the modal again and remove the html
    $('#marker-edit-modal').modal('hide');
    $('body').removeClass('modal-open');
    $('.modal-backdrop').remove();
    $('#edit-modal-placeholder').html("");

}


/*
 * Set _all_ of the button handlers
 */
function bindHandlers() {
    // Toggle collapse indicator
    $('#partner-accordion').on('click', 'button.btn-toggle-collapse', function () {
        $(this).find('i').toggleClass("fa-angle-right").toggleClass("fa-angle-down");
    });

    // ----------------------------------------------------------------------------------------
    // Outcome //

    // ADD an outcome handler that opens the outcomr modal and injects the correct table ID
    $('#partner-accordion').on('click', '.add-outcome', function () {
        // Reset form
        $('#outcome-modal form').trigger("reset");

        // Relies on the ID being `data-partner-id`
        var partnerId = $(this).data('partner-id');

        // Setup model and form
        $('#outcome-modal .modal-title').text('Add an outcome');
        $('#outcome-modal form').attr('action', URLS.addOutcome);

        // Show the user the modal.
        $('#outcome-modal').modal('show');
        // Pass data to form
        $('#id_boundary_partner').val(partnerId);
    });

    // EDIT an outcome
    $('#partner-accordion').on('click', '.edit-outcome', function () {
        var outcomeId = $(this).data('id');
        // Reset form
        $('#outcome-modal form').trigger("reset");

        // Get data from server
        var url = URLS.editOutcome.replace(/0$/, outcomeId);

        $.get(url, "", function (data) {
            if (data.success) {
                // Update form url
                $('#outcome-modal form').attr('action', url);
                $('#outcome-modal .modal-title').text('Edit outcome');

                // Add data to form
                $('#outcome-modal form textarea[name="description"]').val(data.description);
                $('#outcome-modal form input[name="boundary_partner"]').val(data.partnerId);


                // display the modal
                $('#outcome-modal').modal('show');
            } else {
                window.scrollTo(0, 0);
                setDecartAlertDiv('danger', 'Unable to get state details.');
            }

        }, "json").fail(function () {
            decartServerError();
        });
    });

    // DELETE an outcome - inline with each outcome.
    $('#partner-accordion').on('click', '.delete-outcome', function () {
        var result = confirm("Are you sure you want to delete this outcome?");
        if (result) {
            // delete-outcome-<PK>
            var pk = $(this).data('id');

            // Contact the server to request the delete
            decartDeleteById(
                URLS.deleteOutcome,
                pk,
                function (data) {
                    console.log(pk);
                    $('#outcome-' + pk).remove()
                },
                "Outcome"
            )
        }
    });

    // ----------------------------------------------------------------------------------------
    // Indicator //

    // ADD an indicator handler that opens the indicator modal and injects the correct table ID
    $('#partner-accordion').on('click', '.add-indicator', function () {
        // Reset form
        $('#indicator-form').trigger("reset");
        $('button.kpi-cat.kpi-cat-a').click();


        var partnerId = $(this).data('partner-id');
        var outcomeId = $(this).data('outcome-id');

        // Attach data to form
        $('#indicator-form').data('partner-id', partnerId);
        $('#indicator-form').data('outcome-id', outcomeId);

        // Setup model and form
        $('#indicator-modal .modal-title').text('Add an indicator');
        $('#indicator-form').attr('action', URLS.addIndicator);

        $('button.kpi-cat.selected').click();

        // Show the user the modal.
        $('#indicator-modal').modal('show');
    });

    // EDIT an indicator
    $('#partner-accordion').on('click', '.edit-indicator', function () {
        var indicatorPk = $(this).data('id');
        // Reset form
        $('#indicator-form').trigger("reset");

        // Get data from server
        var url = URLS.editIndicator.replace(/0$/, indicatorPk);

        $.get(url, "", function (data) {
            if (data.success) {
                // Update form url
                $('#indicator-form').attr('action', url);
                $('#indicator-modal .modal-title').text('Edit indicator');

                $('#indicator-form button.kpi-cat-' + data.kpi_group).click();
                // Add data to form
                $('#indicator-form select[name="kpi"]').val(data.kpi);
                $('#indicator-form select[name="kpi"]').change();
                $('#indicator-form input[name="name"]').val(data.name);
                $('#indicator-form input[name="measure"]').val(data.measure);
                $('#indicator-form input[name="verification"]').val(data.verification);
                $('#indicator-form input[name="baseline"]').val(data.baseline);
                $('#indicator-form input[name="baseline_date"]').val(data.date);

                // display the modal
                $('#indicator-modal').modal('show');
            } else {
                window.scrollTo(0, 0);
                setDecartAlertDiv('danger', 'Unable to get state details.');
            }

        }, "json").fail(function () {
            decartServerError();
        });
    });


    // DELETE an indicator handler - inline with each indicator.
    $('#partner-accordion').on('click', '.delete-indicator', function () {
        var result = confirm("Are you sure you want to remove this indicator?");
        if (result) {
            var tr = $(this).closest('tr');
            // indicator-<ID>
            var Id = $(this).data('id');

            // Contact the server to request the delete
            decartDeleteById(
                URLS.deleteIndicator,
                Id,
                function (data) {
                    $(tr).remove()
                },
                "Indicator"
            )
        }
    });

    // populate KPI dropdowns
    $('button.kpi-cat').click(function () {
        // change button style
        $('button.kpi-cat').not(this).removeClass('selected');
        $(this).addClass('selected');
        // update dropdown
        var group = $(this).data('group');
        var selectedValue = $('#id_kpi').val();
        $('#id_kpi').find("optgroup").remove();
        for (i in kpi_data[group]) {
            var heading = kpi_data[group][i]['heading'];
            var kpis = kpi_data[group][i]['kpis'];
            var optgroup = $('<optgroup></optgroup>').attr('label', heading);
            for (j in kpis) {
                var option = $('<option></option>')
                    .attr('value', kpis[j].id)
                    .text(kpis[j].name)
                    .data('desc', kpis[j].desc);
                $(optgroup).append(option);
            }
            $('#id_kpi').append(optgroup);
        }
        if (0 != $('#id_kpi option[value="' + selectedValue + '"]').length) {
            $('#id_kpi').val(selectedValue);
        } else {
            $('#id_kpi').val('');
        }
        $('#id_kpi').change();
    });

    $('select#id_kpi').change(function () {
        // desc
        if ($(this).val() != '' && $('select#id_kpi option:selected').data('desc')) {
            $('#indicator-table div.example-info').show();
            $('#indicator-table p.desc').text($('select#id_kpi option:selected').data('desc'));
        } else {
            $('#indicator-table div.example-info').hide();
            $('#indicator-table p.desc').text('');
        }

        // other option
        if ($('select#id_kpi option:selected').text() == 'Other') {
            $('#indicator-table div.other-info').removeClass('d-none');
            $('#indicator-table input[name="name"]').attr('type', 'text');
        } else {
            $('#indicator-table div.other-info').addClass('d-none');
            $('#indicator-table input[name="name"]').attr('type', 'hidden');
        }
    });

    // ----------------------------------------------------------------------------------------
    // Progress Marker //

    // DELETE a marker - inline with each progress marker.
    $('#progress-markers').on('click', 'tr button.delete-marker', function () {
        var result = confirm("Are you sure you want to remove this progress marker?");
        if (result) {
            var tr = $(this).closest('tr');
            var Id = tr[0].id;
            var pk = Id.substr(7, Id.length);

            decartDeleteById(
                URLS.deleteProgressMarker,
                pk,
                function (data) {
                    $(tr).remove()
                },
                "Progress Marker"
            )
        }
    });

    // EDIT a marker - inline with each marker.
    // This fetches and displays the form while the inner function handles the submission
    // >> This uses a bit of a hack to modify the edit marker url.
    // TODO :: Remove this hack by parsing the `action` out of the form and passing it along
    //         in the call.
    $('#progress-markers').on('click', 'tr button.edit-marker', function () {
        var tr = $(this).closest('tr');
        var Id = tr[0].id;
        var pk = Id.substr(7, Id.length);
        var url = URLS.editProgressMarker.replace(/0$/, pk);

        $.get(url, "", function (data) {
            if (data['success']) {
                // Add in the new modal
                $('#edit-modal-placeholder').html(data['html']);
                // Bind the sumbit handler
                $('#marker-edit-form').submit(function (event) {
                    var formData = $(this).serializeArray();
                    handleMarkerEdit(formData, url, pk)

                    // Cancel the default submission handling
                    event.preventDefault();
                });
                // Display the modal
                $('#marker-edit-modal').modal('show');
            } else {
                window.scrollTo(0, 0)
                setDecartAlertDiv('danger', 'Unable to get marker details.')
            }
        }, "json").fail(function () {
            decartServerError()
        });
    });
}


/*
 * Main jQuery handler function for page animations/form actions etc.
 */
$(document).ready(function () {
    // Set up the CSRF token details for validating AJAX requests.
    setCSRFHeader();

    // ----------------------------------------------------------------------------------------
    // Bind the Outcome buttons //

    // Add/Edit outcome
    $('#outcome-form').submit(function (event) {
        var formData = $(this).serializeArray();

        $.post($('#outcome-form').attr('action'), formData, function (data) {
            if (data['success']) {
                var outcomePk = data['outcomePk'];
                var outcome = $('#outcome-' + outcomePk);
                if (outcome.length > 0) {
                    //edit
                    $('#outcome-' + outcomePk + ' .collapse>p i').text(data['description']);
                } else {
                    //add
                    var partnerPk = data['partnerPk'];
                    var outcomePk = data['outcomePk'];
                    var description = data['description'];
                    var partnerName = data['boundary_partner'];
                    var outcomeNum = data['outcomeNum'];
                    var html = getOutcomeHTML(partnerPk, outcomePk, description, outcomeNum);

                    $('#accordion-' + partnerPk).append(html);

                    // Add the outcome to the Progress marker select box
                    $('#id_outcome').append(
                        $('<option>', {
                            value: outcomePk,
                            text: partnerName + ': ' + description
                        }));

                    // Remove the placeholder if it is there
                    $('#no-outcomes-' + partnerPk).remove();
                }
                setDecartAlertDiv('success', 'Outcome saved')
            } else {
                setDecartAlertDiv('danger', 'Unable to save outcome: please try again later.')
            }

        }, "json").fail(function () {
            decartServerError()
        });

        // Hide the modal again
        $('#outcome-modal').modal('hide');

        // Cancel the default submission handling
        event.preventDefault();
    });


    // ----------------------------------------------------------------------------------------
    // Add a Progress marker //
    $('#marker-form').submit(function (event) {
        var formData = $(this).serializeArray();
        $.post(
            URLS.addProgressMarker,
            formData,
            updateProgressMarkerTable,
            "json"
        ).fail(function () {
            decartServerError()
        });

        // Hide the modal again
        $('#marker-modal').modal('hide');

        // Remove the placeholder if it is there
        $('#no-markers').remove();

        // Cancel the default submission handling
        event.preventDefault();
    });


    // Catch the submission of the modal and inject the table ID from the button.
    $('#indicator-form').submit(function (event) {
        var formData = $(this).serializeArray();
        var partnerPk = $(this).data('partner-id');
        var outcomePk = $(this).data('outcome-id');
        formData.push({
            "name": "partner-id",
            "value": partnerPk
        });
        formData.push({
            "name": "outcome-id",
            "value": outcomePk
        });

        $.post(
            $('#indicator-form').attr('action'),
            formData,
            function (data) {
                if (data['success']) {
                    var pk = data['pk'];
                    var indicator = $('#indicator-' + pk);

                    var kpi = $('#id_kpi option:selected').text();
                    if (kpi == 'Other') {
                        kpi += ' - ' + formData[2].value
                    }
                    var measure = formData[3].value;
                    var verification = formData[4].value;
                    var baseline = formData[5].value;
                    var date = formData[6].value;
                    if (indicator.length > 0) {
                        // edit
                        $(indicator).children(":nth(0)").text(kpi);
                        $(indicator).children(":nth(1)").text(measure);
                        $(indicator).children(":nth(2)").text(verification);
                        $(indicator).children(":nth(3)").text(baseline);
                        $(indicator).children(":nth(4)").text(moment(date).format('DD/MM/YYYY'));
                    } else {
                        // add
                        $('#no-indicators-' + outcomePk).remove();
                        var tmpContent = '<tr id=indicator-' + pk + '>' +
                            '<td>' + kpi + '</td>' +
                            '<td>' + measure + '</td>' +
                            '<td>' + verification + '</td>' +
                            '<td>' + baseline + '</td>' +
                            '<td>' + moment(date).format('DD/MM/YYYY') + '</td>' +
                            '<td class="option-2">' +
                            '<div class="btn-group btn-group-sm" role="group">' +
                            '<button class="btn btn-success edit-indicator" title="Edit this indicator" type="button" data-id="' + pk + '">' +
                            '<i class="far fa-edit"></i>' +
                            '</button>' +
                            '<button class="btn btn-danger delete-indicator" title="Delete this indicator" type="button" data-id="' + pk + '">' +
                            '<i class="far fa-trash-alt"></i>' +
                            '</button>' +
                            '</div>' +
                            '</td>' +
                            '</tr>';
                        $("#indicators-" + partnerPk + '-' + outcomePk).append(tmpContent);
                    }
                    setDecartAlertDiv('success', 'Indicator saved')
                } else {
                    setDecartAlertDiv('danger', 'Unable to save indicator: please try again later.')
                }
            }, "json"
        ).fail(function () {
            decartServerError()
        });
        // hide the modal again
        $('#indicator-modal').modal('hide');

        // Cancel the default submission handling
        event.preventDefault();
    });

    // ----------------------------------------------------------------------------------------
    // Finally, bind all of the event handlers
    bindHandlers()
});