$(document).on('click', '.make-default-address', function() {
    let btn = $(this);
    let url = btn.data('url');
    let address_id = btn.data('address-id');

    $.ajax({
        url: url,
        data: { 'id': address_id },
        dataType: 'json',
        success: function(response) {
            if (response.boolean === true) {
                // 1. Reset tất cả card về trạng thái bình thường
                $('.address-card').removeClass('border-primary'); // Bỏ viền xanh
                $('.status-text').addClass('d-none');           // Ẩn tất cả chữ "Mặc định"
                $('.make-default-btn').removeClass('d-none');   // Hiện lại tất cả nút "Thiết lập"

                // 2. Cập nhật card được chọn thành mặc định
                let currentCard = $('#address-card-' + address_id);
                currentCard.addClass('border-primary');         // Thêm viền xanh
                currentCard.find('.status-text').removeClass('d-none'); // Hiện chữ "Mặc định"
                btn.addClass('d-none');                         // Ẩn chính cái nút vừa bấm
                
                console.log("Đã đổi địa chỉ mặc định thành ID:", address_id);
            }
        }
    });
});