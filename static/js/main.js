// ---------------------------
// Enable tooltip
// ---------------------------
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

// ---------------------------
// AJAX setup for CSRF in form
// ---------------------------
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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// ---------------------------
// Modal for seller update stock view
// ---------------------------
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

// ---------------------------
// Modal for seller update image view
// ---------------------------
$(function () {
    $('#updateImageModal').on('show.bs.modal', function() {
        var modal = $('#updateImageModal');
        var form = $('#updateImageForm');
        var error = $('#modalFormError');
        var button = $('#updateImageModalSave');
        // Remove any error message first
        error.addClass('hide');
        button.prop('disabled', false);
        button.click(function (event) {
            event.preventDefault();
            button.prop('disabled', true);
            var file = $('input:file');
            var data = new FormData(form[0]); // note: have to use "[0]" here since FormData expect a HTML element but not jQuery element
            $.ajax({
                url: button.data('update-image-url'),
                type: 'POST',
                data: data,
                processData: false,
                contentType: false,
                cache: false,
                timeout: 600000,
                success: function (json) {
                    // console.log(json);
                    // console.log('ajax success!');
                    location.reload();
                    // modal.modal('hide');
                },
                error: function (xhr, errmsg, err) {
                    // console.log(xhr.status + ": " + xhr.responseText);
                    error.removeClass('hide');
                    error.text(xhr.status + ": " + xhr.responseText);
                    button.prop('disabled', false);
                }
            });
        });
    });
});

$(function () {
    var countDownDate = parseFloat($('#expiration').text());
    var x = setInterval(function() {
        var now = new Date().getTime();
        var distance = countDownDate - now;
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
        $('#timer').text(minutes + " : " + seconds);
        if (distance < 60 * 1000) {
            $('#timer_class').removeClass('alert-info').addClass('alert-warning');
        }
        if (distance < 1000) {
            clearInterval(x);
            $('#timer_class').removeClass('alert-warning').addClass('alert-danger');
        }
    }, 1000);
});

function toggle_review_textarea(checkboxElem) {
    var review = $('#id_review_req_form');
    if (checkboxElem.checked) {
        review.show();
    } else {
        review.hide();
    }
}