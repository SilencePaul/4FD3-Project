document.addEventListener("DOMContentLoaded", function() {
    const stock_verify = document.getElementById("stock_verify");
    const stock_info = document.getElementById("stock_info");

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
