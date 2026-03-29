$(document).on('click', '.remove-from-wishlists', function (e) {
    e.preventDefault();

    let btn = $(this);
    let url = btn.data('url');
    let wishlist_id = btn.data('id');

    $.ajax({
        url: url,
        type: 'POST',
        data: {
            id: wishlist_id,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        },
        dataType: 'json',
        success: function (response) {
            if (response.status === 'success') {
                $('.wishlist-item-' + wishlist_id).fadeOut(300, function () {
                    $(this).remove();
                });

                $('#wishlist-items-count').attr(
                    'data-notify',
                    response.total_wishlist_items
                );
            }
        }
    });
});
