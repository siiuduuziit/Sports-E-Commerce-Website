$(document).ready(function(){
    $('#price-filter-btn').on('click', function(){
        
        let url = $(this).data('url');
        let filter_objects = {};
        
        // Lấy giá trị min từ thuộc tính min của slider (thường là 0 hoặc giá thấp nhất)
        let min_price = $('#range_slider').attr('min'); 
        
        // Lấy giá trị max hiện tại từ ô input ẩn (ô này thay đổi khi bạn kéo slider)
        let max_price = $('#max_price').val();

        filter_objects.min_price = min_price;
        filter_objects.max_price = max_price;

        // Hiệu ứng chờ (Optional) - Giúp người dùng biết web đang xử lý
        $('#filter-products').css('opacity', '0.5');

        $.ajax({
            url: url,
            data: filter_objects,
            dataType: 'json',
            beforeSend: function(){
                console.log("Đang lọc với giá tối đa là:", max_price);
            },
            success: function(response){
                // Cập nhật danh sách sản phẩm
                $('#filtered-product').html(response.data);
                
                // Trả lại độ hiển thị bình thường
                $('#filtered-product').css('opacity', '1');
                
                // Nếu bạn có dùng hiệu ứng AOS hay Isotope của template, 
                // bạn cần khởi tạo lại chúng ở đây nếu sản phẩm bị mất hiệu ứng.
            },
            error: function(xhr, status, error) {
                console.error("Lỗi AJAX:", error);
                $('#filtered-product').css('opacity', '1');
            }
        });
    });
});