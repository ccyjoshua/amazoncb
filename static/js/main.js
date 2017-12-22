$(function () {
    $('#stockModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var stock = button.attr('data-stock');  //somehow if use button.data it won't update after change, not sure why
        var limit = button.attr('data-limit');
        var modal = $(this);
        var form = modal.find('form');
        var error = $('#modalFormError');
        // Remove any error message first
        error.addClass('hide');
        // Pre-populate form
        modal.find('#stock').val(stock);
        modal.find('#limit').val(limit);
        $('#stockModalSave').click(function () {
            // Check for validity by HTML5 constraint validation API (no JQuery)
            var stockInput = document.getElementById('stock');
            var limitInput = document.getElementById('limit');
            if (stockInput.validity.valid && limitInput.validity.valid) {
                var stockElement = button.parent().prev();
                var newStock = modal.find('#stock').val();
                var newLimit = modal.find('#limit').val();
                $.ajax({
                    url: button.data('update-stock-url'),
                    type: 'POST',
                    data: form.serialize(),
                    success: function (json) {
                        // console.log(json);
                        // console.log('ajax success!');
                        stockElement.find('span').first().text(newStock);
                        stockElement.find('span').last().text(newLimit);
                        button.attr('data-stock', newStock);
                        button.attr('data-limit', newLimit);
                        modal.modal('hide');
                    },
                    error: function (xhr, errmsg, err) {
                        // console.log(xhr.status + ": " + xhr.responseText);
                        error.removeClass('hide');
                        error.text(xhr.status + ": " + xhr.responseText);
                    }
                });
            } else {
                error.removeClass('hide');
            }
        });
    });
});