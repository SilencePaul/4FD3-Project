document.addEventListener("DOMContentLoaded", function() {
    stock_verify = document.getElementById("stock_verify");
    stock_info = document.getElementById("stock_info");

    stock_verify.addEventListener("click", function() {
        stock_verify.innerHTML = "Loading...";
        stock_verify.disabled = true;
        stock_ticker = document.getElementById("stock_ticker");
        stock_ticker = stock_ticker.value;
        htmx.ajax('GET', '/stock_search/' + stock_ticker, stock_info).then(
            function() {
                stock_verify.innerHTML = "Verify";
                stock_verify.disabled = false;
            });
    });
});
