$(document).ready(function () {
    // Set up the CSRF token details for validating AJAX requests.
    setCSRFHeader();

    $('.create-org').click(function(){
        //clear form
        $('#org-form').trigger("reset");
        $('#org-form').attr('action',  URLS.newOrg);
        $('#org-modal').modal('show');

        $('#org-modal .modal-title').text('Create A New Organisation');
    });

    $('.edit-org').click(function(){
        var orgId = $(this).closest('tr').data('id');
        var url = URLS.editOrg.replace(/0$/, orgId);

        $('#org-modal .modal-title').text('Edit Organisation');

        $.get(url, "", function (data) {
            if (data.success) {
                //update form URL (might not needed)
                $('#org-form').attr('action', url);

                // Add data to form
                $('#org-form').trigger("reset");

                $('#org-form input[name="name"]').val(data.name);
                $('#org-form select[name="scale"]').val(data.scale).trigger('change');
                $('#org-form select[name="organisation_type"]').val(data.type).trigger('change');
                $('#org-form input[name="email"]').val(data.email);
                $('#org-form input[name="phone"]').val(data.phone);
                $('#org-form input[name="website"]').val(data.website);
                $('#org-form input[name="location"]').val(data.location);
                $('#org-form textarea[name="other_info"]').val(data.other_info);
                console.log(data)
                
                $('#org-modal .modal-title').text('Edit Organisation');

                // Display the modal
                $('#org-modal').modal('show');
            } else {
                window.scrollTo(0, 0);
                setDecartAlertDiv('danger', 'Unable to get organisation details.');
            }
        }, "json").fail(function() { decartServerError(); });

    });

    $('#org-form').submit(function (event) {
        var formData = $(this).serializeArray();

        $.post(
            $('#org-form').attr('action'),
            formData,
            function(data) {
                if (data.success) {
                    location.reload();
                } else {
                    setDecartAlertDiv('warning', 'Unable to create a new organisation: ' + data.errors);
                }
            }, "json"
        ).fail(function() { decartServerError(); });

        // Hide the modal
        // $('#org-creator-modal').modal('hide');
        $("#org-modal .close").click();

        // Cancel the default submission handling
        event.preventDefault();
    });
});
