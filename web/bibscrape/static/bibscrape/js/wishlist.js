function add_to_wishlist(hash, title, ean) {
    console.log("hello")
    $.post({'title' : title, 'ean' : ean, 'hash' : hash}, function(data,status){
        console.log(status)
    })
}