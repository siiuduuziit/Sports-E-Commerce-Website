function changeQty(step) {
    let qtyInput = document.getElementById('product-quantity');
    let currentVal = parseInt(qtyInput.value);
    if (!isNaN(currentVal)) {
        let newVal = currentVal + step;
        if (newVal >= 1) qtyInput.value = newVal;
    }
}