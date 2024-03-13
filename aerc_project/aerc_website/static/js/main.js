document.addEventListener("DOMContentLoaded", function() {
    const stock_verify = document.getElementById("stock_verify");
    const stock_info = document.getElementById("stock_info");
    const crypto_verify = document.getElementById("crypto_verify");
    const crypto_info = document.getElementById("crypto_info");

    if (crypto_verify != null && crypto_info != null) {
        crypto_verify.addEventListener("click", function() {
            crypto_verify.innerHTML = "Loading...";
            crypto_verify.disabled = true;
            const crypto_ticker = document.getElementById("crypto_ticker");
            if (crypto_ticker.value === "") {
                crypto_verify.innerHTML = "Verify";
                crypto_verify.disabled = false;
                alert("Please enter a cryptocurrency ticker.");
            }
            else {
                htmx.ajax('GET', '/crypto_search/' + crypto_ticker.value, crypto_info).then(
                function() {
                    crypto_verify.innerHTML = "Verify";
                    crypto_verify.disabled = false;
                });
            }
        });
    }

    if (stock_verify != null && stock_info != null) {
        stock_verify.addEventListener("click", function() {
            stock_verify.innerHTML = "Loading...";
            stock_verify.disabled = true;
            const stock_ticker = document.getElementById("stock_ticker");
            if (stock_ticker.value === "") {
                stock_verify.innerHTML = "Verify";
                stock_verify.disabled = false;
                alert("Please enter a stock ticker.");
            }
            else {
                htmx.ajax('GET', '/stock_search/' + stock_ticker.value, stock_info).then(
                function() {
                    stock_verify.innerHTML = "Verify";
                    stock_verify.disabled = false;
                });
            } 
        });
    } 

    const currentPage = window.location.pathname; // Get current page path
    document.querySelectorAll('.navbar-item').forEach(item => {
        if (currentPage.includes(item.getAttribute('href'))) {
            item.classList.add('is-active');
        }
    });
});
