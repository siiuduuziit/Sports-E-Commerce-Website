$(document).on("submit", "#commentForm", function (e) {
    e.preventDefault();
    
    // Đường dẫn ảnh mặc định (thay đúng path của bạn)
    let defaultProfileImage = "/static/images/default_profile_image.jpg"; 

    $.ajax({
        data: $(this).serialize(),
        method: $(this).attr("method"),
        url: $(this).attr("action"),
        dataType: "json",
        success: function (response) {
            if (response.bool === true) {
                $("#review-response").html("Thêm đánh giá thành công!");

                let rating = parseInt(response.context.rating);
                let _html = `
                    <div class="flex-w flex-t p-b-68">
                        <div class="wrap-pic-s size-109 bor0 of-hidden m-r-18 m-t-6">
                            <img src="${defaultProfileImage}" alt="AVATAR"/>
                        </div>
                        <div class="size-207">
                            <div class="flex-w flex-sb-m p-b-17">
                                <span class="mtext-107 cl2 p-r-20">
                                    ${response.context.user}
                                </span>
                                <span class="fs-18 cl11">`;

                // Vẽ lại sao vàng dựa trên số rating nhận về
                for (let i = 1; i <= rating; i++) {
                    _html += `<i class="zmdi zmdi-star"></i>`;
                }

                _html += `      </span>
                            </div>
                            <p class="stext-102 cl6">${response.context.review}</p>
                        </div>
                    </div>`;

                $(".review-list").prepend(_html);
                $("#commentForm")[0].reset(); 
            }
        }
    });
});
