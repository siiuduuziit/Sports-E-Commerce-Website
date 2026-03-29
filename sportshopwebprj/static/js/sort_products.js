// Khởi tạo Isotope 1 lần khi page load
var $grid = $('#filter-products').isotope({
    itemSelector: '.isotope-item',
    layoutMode: 'fitRows'
});

// Lưu filter hiện tại (mặc định show tất cả)
var currentFilter = '*';

// Category filter
$(document).on('click', '[data-filter]', function() {
    currentFilter = $(this).attr('data-filter');
    $grid.isotope({ filter: currentFilter });
});

// Sort button AJAX
$(".sort-btn").click(function(e) {
    e.preventDefault();

    let url = $(this).data("url");
    let sort_by = $(this).data("sort");

    $.ajax({
        url: url,
        data: { sort: sort_by },
        success: function(response) {
            // Thay HTML mới
            $("#filter-products").html(response.data);

            // Destroy instance cũ và bind lại Isotope
            $grid.isotope('destroy');
            $grid = $('#filter-products').isotope({
                itemSelector: '.isotope-item',
                layoutMode: 'fitRows',
                filter: currentFilter // giữ filter hiện tại
            });
        }
    });
});
