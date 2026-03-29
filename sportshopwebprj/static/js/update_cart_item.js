$(document).on('click', '.update-item', function() {
    
    let btn = $(this)
    let url = btn.data('url')
    
    let product_id = btn.data('item')
    let product_quantity = $('.product-quantity-' + product_id).val()

    console.log('Product ID:', product_id)
    console.log('Product QTY:', product_quantity)

    $.ajax({
        url: url,
        data: {
            'id': product_id,
            'qty': product_quantity,
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

// $(document).on('click', '.btn-num-product-up', function() {
//     let input = $(this).closest('.wrap-num-product').find('.num-product');
//     let current = parseInt(input.val()) || 0;
//     input.val(current + 1);
//     // input.trigger('change');
// });

// $(document).on('click', '.btn-num-product-down', function() {
//     let input = $(this).closest('.wrap-num-product').find('.num-product');
//     let current = parseInt(input.val()) || 0;
//     if (current > 1) input.val(current - 1);
//     // input.trigger('change');
// });
