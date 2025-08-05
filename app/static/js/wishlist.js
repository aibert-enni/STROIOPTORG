async function addToWishlist(product_id, element = null) {
    const response = await api('/api/v1/wishlist/add/' + product_id + '/', {
        method: 'POST',
    })

    const data = await response.json()

    if (element) {
        const color = '#186FD4';
        element.style.color = color;
        element.querySelector('svg').style.fill = color;
    }

    console.log(data)

    return data
}

async function removeFromWishlist(product_id, element) {
    const response = await api('/api/v1/wishlist/remove/' + product_id + '/', {
        method: 'DELETE',
    })

    if (element) {
        element.style.color = 'black';
        element.querySelector('svg').style.fill = 'none';
    }
    if (!response.ok) {
        const error = await response.json()
        console.log(error)
        return error
    }

    console.log("Удалено")
}