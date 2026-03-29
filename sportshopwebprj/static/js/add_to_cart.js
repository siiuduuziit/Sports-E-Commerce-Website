$(document).on('click', '#add-to-cart-btn', function() {
    let btn = $(this);
    let url = btn.data('url');
    let cart = btn.data('cart');

    // Lấy dữ liệu
    let product_id = $('.product-id-' + cart).val();
    let product_pid = $('.product-pid-' + cart).val();
    let product_title = $('.product-title-' + cart).val();
    let product_quantity = $('.product-quantity-' + cart).val();
    let product_price = $('.current-product-price-' + cart).data('price');
    let product_image = $('.product-image-' + cart).val();

    // --- UX TRƯỚC KHI GỬI: Đổi trạng thái nút ---
    let originalHtml = btn.html();
    btn.html('<i class="fa fa-spinner fa-spin"></i>').prop('disabled', true);

    $.ajax({
        url: url,
        data: {
            'id': product_id,
            'pid': product_pid,
            'title': product_title,
            'qty': product_quantity,
            'price': product_price,
            'image': product_image,
        },
        dataType: 'json',
        success: function(response) {
            // --- UX KHI THÀNH CÔNG ---
            
            // 1. Hiệu ứng bay (Flying Animation)
            let cartIcon = $(".js-show-cart"); // Selector của icon giỏ hàng trên header
            let flyingImg = $('<img src="' + product_image + '" style="position:fixed; z-index:9999; width:50px; height:50px; object-fit:cover; border-radius:50%; transition: all 0.8s cubic-bezier(0.42, 0, 0.58, 1);">');
            
            $("body").append(flyingImg);
            flyingImg.css({
                top: btn.offset().top - $(window).scrollTop(),
                left: btn.offset().left
            }).animate({
                top: cartIcon.offset().top - $(window).scrollTop(),
                left: cartIcon.offset().left,
                width: 20,
                height: 20,
                opacity: 0
            }, 800, function() {
                flyingImg.remove();
                
                // 2. Cập nhật số lượng và mini-cart sau khi ảnh bay xong
                $('#cart-items-count').attr('data-notify', response.total_cart_items);
                $('.js-show-cart').attr('data-notify', response.total_cart_items); // Cập nhật cả icon mobile nếu có
                $('#mini-cart').html(response.mini_cart_html);
            });

            // 3. Thông báo Toast (Tự ẩn sau 1.5s)
            swal({
                title: "Thành công!",
                text: "Đã thêm " + product_title + " vào giỏ hàng",
                icon: "success",
                timer: 1500,
                buttons: false,
            });

            // 4. Trả lại trạng thái nút (Dấu tích xanh như ý bạn muốn)
            btn.html("&#10004;").prop('disabled', false);
            setTimeout(function() {
                btn.html(originalHtml); // Sau 2s trả lại chữ "Add to cart" gốc
            }, 2000);
        },
        error: function() {
            btn.html(originalHtml).prop('disabled', false);
            swal("Lỗi", "Không thể thêm vào giỏ hàng", "error");
        }
    });
});