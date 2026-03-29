$('#contact-form').submit(function(e){
    e.preventDefault();
    var url = $(this).data('url');
    $.ajax({
        type: 'POST',
        url: url,
        data: $(this).serialize(),
        success: function(response){
            if(response.bool){
                alert("Tin nhắn đã gửi thành công!");
                $('#contact-form')[0].reset();
            } else {
                alert("Có lỗi xảy ra!");
            }
        }
    });
});
