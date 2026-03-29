// Hàm cập nhật giá trị hiển thị khi kéo thanh trượt (Real-time)
function updatePriceValue(val) {
  // Cập nhật ô input số
  $("#max_price").val(val);

  // Định dạng số có dấu chấm (Ví dụ: 1.000.000)
  let formatted = new Intl.NumberFormat("vi-VN").format(val);
  $("#price_val").text(formatted);
}

$(document).ready(function () {
  // 1. Khi kéo thanh slider (Dùng jQuery để đảm bảo đồng bộ thêm một lần nữa)
  $("#range").on("input", function () {
    updatePriceValue($(this).val());
  });

  // 2. Kiểm tra tính hợp lệ khi người dùng rời khỏi ô nhập liệu (nếu có hiện ô nhập)
  $("#max_price").on("blur", function () {
    let min_p = parseInt($(this).attr("min"));
    let max_p = parseInt($(this).attr("max"));
    let current_p = parseInt($(this).val());

    if (current_p < min_p || current_p > max_p) {
      alert(
        "Giá phải nằm trong khoảng từ " +
          min_p.toLocaleString() +
          " đến " +
          max_p.toLocaleString() +
          " VND"
      );

      // Reset về giá trị cao nhất
      $(this).val(max_p);
      $("#range").val(max_p);
      updatePriceValue(max_p);
      $(this).focus();
    } else {
      // Đồng bộ ngược lại thanh kéo nếu nhập tay hợp lệ
      $("#range").val(current_p);
      updatePriceValue(current_p);
    }
  });

  // 3. Xử lý nút Lọc (AJAX)
  $("#price-filter-btn").on("click", function () {
    let url = $(this).data("url");
    let filter_objects = {
      min_price: $("#range").attr("min"),
      max_price: $("#max_price").val(),
    };

    $.ajax({
      url: url,
      data: filter_objects,
      dataType: "json",
      beforeSend: function () {
        // Thêm hiệu ứng loading nếu cần
        $("#filtered-product").css("opacity", "0.5");
      },
      success: function (response) {
        $("#filtered-product").html(response.data);
        $("#filtered-product").css("opacity", "1");
      },
    });
  });
});
