$(document).on('click', '.delete-item', function() {
    
    let btn = $(this)
    let url = btn.data('url')
    
    let product_id = btn.data('item')

    console.log('Product ID:', product_id)

    $.ajax({
        url: url,
        data: {
            'id': product_id
        },
        dataType: 'json',
        success: function(response){
            $('#cart-items-count').attr('data-notify', response.total_cart_item);
            $('#shopping-cart').html(response.data)
            $('#cart_sub_total_amount').text(response.cart_sub_total_amount)
            $('#cart_total_amount').text(response.cart_total_amount)
        }
    })

})
