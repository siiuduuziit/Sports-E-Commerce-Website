$(document).on('click', '.add-to-wishlist', function(e) {
    e.preventDefault();
    let btn = $(this);
    let url = btn.data('url');
    let product_id = btn.data('product-item');
    let heartIcon = btn.find('.heart-icon');

    btn.css('opacity', '0.5');

    $.ajax({
        url: url,
        data: { 'id': product_id },
        dataType: 'json',
        success: function(response) {
            btn.css('opacity', '1');

            if (response.status === 'success') {
                // Cập nhật số lượng wishlist header
                $('#wishlist-header-icon').attr('data-notify', response.total_wishlist_items);

                // Toggle màu tim
                if (response.added) {
                    heartIcon.css('color', '#ee4d2d'); // tim đỏ
                    swal("Added!", response.message, "success");
                } else {
                    heartIcon.css('color', '#000000ff'); // tim trống
                    swal("Removed!", response.message, "info");
                }
            }
        },
        error: function() {
            btn.css('opacity', '1');
            swal("Error", "Cannot connect to server.", "error");
        }
    });
});
