// Function to fetch new data and update the chart
// Function to fetch new data and update the chart
// Function to fetch new data and update the chart
function fetchDataAndUpdateChart() {
    var productType = document.getElementById('product-info').getAttribute('data-product-type');
    fetch(`/get-product-data/${productType}/`)
        .then(response => response.json())
        .then(data => {
            // Get the local timezone offset in milliseconds

            var timezoneOffset = new Date().getTimezoneOffset() * 60 * 1000;

            // Adjust timestamps to local time by adding the timezone offset
            var localTimestamps = data['timestamps'].map(function (timestamp) {
                // Convert to local time by adjusting with timezone offset
                return new Date(new Date(timestamp).getTime() - timezoneOffset).toISOString();
            });

            var localTimerange = data["time_range"].map(function (timestamp) {
                // Convert to local time by adjusting with timezone offset
                return new Date(new Date(timestamp).getTime() - timezoneOffset).toISOString();
            });
            var timestamps = data['timestamps'];
            var openPrices = data['open_prices'];
            var highPrices = data['high_prices'];
            var lowPrices = data['low_prices'];
            var closePrices = data['close_prices'];

            // Update the chart
            var trace = {
                x: localTimestamps,  // Use localTimestamps for x-axis
                high: highPrices,
                low: lowPrices,
                open: openPrices,
                close: closePrices,
                decreasing: { line: { color: '#dc3545' } },
                increasing: { line: { color: '#28a745' } },
                line: { 
                    color: 'rgba(31,119,180,1)', 
                    width: 1,
                },
                type: 'candlestick',
                xaxis: 'x',
                yaxis: 'y'
            };

            var layout = {
                dragmode: 'zoom',
                margin: {
                    r: 10,
                    t: 25,
                    b: 40,
                    l: 60
                },
                showlegend: false,
                xaxis: {
                    autorange: false,
                    domain: [0, 1],
                    range: localTimerange,
                    type: 'date',
                    fixedrange: true,
                    rangeslider: {
                        visible: false,
                        range: localTimerange
                    },
                },
                yaxis: {
                    autorange: false,
                    domain: [0, 1],
                    range: data["price_range"],
                    type: 'linear',
                    fixedrange: true  // Prevent zooming on y-axis
                },
            };

            var lineData = {
                x: localTimestamps,  // Use localTimestamps for x-axis
                y: data['close_prices'],
                line: { 
                    color: 'rgb(46, 60, 255)', 
                    width: 1,
                },
                type: 'scatter',
                mode: 'lines',
                name: '即時走勢'
            };

            var config = {
                displayModeBar: false
            };

            Plotly.react('chart', [trace, lineData], layout, config);

            // Update the latest prices
            updateLatestPrices(closePrices, data['timestamps']);
            updateTransactionInfo(
                closePrices[closePrices.length - 1].toFixed(2),
                data['current_time'],
                data['tag_price'].toFixed(2),
                data['tag_time'],
                data['next_settlement_time'],
                data['order_deadline_time'],
            )
        });
}

function fetchOrderData() {
    var productType = document.getElementById('product-info').getAttribute('data-product-type');
    var page = document.getElementById('product-info').getAttribute('data-current-page');
    var current_price = document.getElementById('product-info').getAttribute('data-current-price');

    fetch(`/get-order-data/${productType}/?page=${page}&current_price=${current_price}`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector("table tbody");
            if (tableBody) {
                tableBody.innerHTML = "";  // Clear current table rows

                data.orders.forEach(order => {
                    if (order) {
                        const row = document.createElement("tr");
                        // Check profit value and apply color
                        let profitColor = order.profit > 0 ? 'red' : (order.profit < 0 ? 'green' : 'black');

                        // If order status is "Completed", set row background to gray
                        if (order.status === "Completed") {
                            row.style.backgroundColor = "gray";
                        }

                        row.innerHTML = `
                            <td>${order.id}</td>
                            <td>${order.product}</td>
                            <td>$${order.price.toFixed(2)}</td>
                            <td>${order.direction}</td>
                            <td>${order.created_at}</td>
                            <td>${order.settled_at || "N/A"}</td>
                            <td>${order.settled_price || "N/A"}</td>
                            <td>${order.status}</td>
                            <td style="color: ${profitColor}">${order.profit !== null ? `$${order.profit.toFixed(2)}` : "<span class='text-muted'>N/A</span>"}</td>
                        `;
                        tableBody.appendChild(row);
                    }
                });

                // Update pagination controls (if applicable)
                document.querySelector("#next-page").disabled = !data.has_next;
                document.querySelector("#previous-page").disabled = !data.has_previous;
            }
        })
        .catch(error => console.error("Error fetching order data:", error));
}



// Function to update the latest 5 prices in the second card
function updateLatestPrices(prices, timestamps) {
    const latestPricesList = document.getElementById('latest-prices');
    latestPricesList.innerHTML = ''; // Clear previous entries

    // Get the latest 5 prices
    const latestPrices = prices.slice(-5).reverse();
    const latestTimestamps = timestamps.slice(-5).reverse();

    latestPrices.forEach((price, index) => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        listItem.innerHTML = `
            <span>${new Date(latestTimestamps[index]).toLocaleString()}</span>
            <span class="badge bg-primary rounded-pill">$${price.toFixed(2)}</span>
        `;
        latestPricesList.appendChild(listItem);
    });
}

// Function to update the transaction info card with current price, time, and deadlines
function updateTransactionInfo(currentPrice, currentTime, tagPrice, tagTime, settlementTime, orderDeadline) {
    const settlementLocalTime = new Date(settlementTime).toLocaleTimeString();
    const orderDeadlineLocalTime = new Date(orderDeadline).toLocaleTimeString();
    const currentLocalTime = new Date(currentTime).toLocaleTimeString();

    // Calculate the time difference to settlement in seconds
    const timeToSettleMentDiff = Math.max(0, Math.floor((new Date(settlementTime) - new Date(currentTime)) / 1000)); // in seconds
    // Convert time difference to minute:second format for settlement time
    const minutesToSettleMent = Math.floor(timeToSettleMentDiff / 60);
    const secondsToSettleMent = timeToSettleMentDiff % 60;
    const timeToSettleMent = `${minutesToSettleMent}:${secondsToSettleMent < 10 ? '0' + secondsToSettleMent : secondsToSettleMent}`;

    // Calculate the time difference to order deadline in seconds
    const timeToOrderDeadlineDiff = Math.max(0, Math.floor((new Date(orderDeadline) - new Date(currentTime)) / 1000)); // in seconds
    // Convert time difference to minute:second format for order deadline
    const minutesToOrderDeadline = Math.floor(timeToOrderDeadlineDiff / 60);
    const secondsToOrderDeadline = timeToOrderDeadlineDiff % 60;
    const timeToOrderDeadline = `${minutesToOrderDeadline}:${secondsToOrderDeadline < 10 ? '0' + secondsToOrderDeadline : secondsToOrderDeadline}`;

    // Update the transaction info card
    document.getElementById('product-info').setAttribute('data-current-price', currentPrice);
    document.getElementById('current-price').textContent = `$${currentPrice}`;
    document.getElementById('current-time').textContent = currentLocalTime;
    document.getElementById('settlement-time').textContent = `${settlementLocalTime} -- (${timeToSettleMent})`;
    document.getElementById('order-deadline').textContent = `${orderDeadlineLocalTime} -- (${timeToOrderDeadline})`;
}


// Handle the "Buy Up" button click
// Reusable function to handle "Buy" actions
function handleBuyAction(action) {
    const currentUser = "{{ user.username }}";  // Use Django template tag to pass current user
    const productType = "productA";  // Adjust based on your product
    const currentPrice = document.getElementById('current-price').innerText.replace('$', ''); // Get the current price
    // Make the AJAX request to create an order
    fetch('/create-order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        body: JSON.stringify({
            user: currentUser,
            product_type: productType,
            price: currentPrice,
            action: action,  // Dynamically pass 'buy_up' or 'buy_down'
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("订单创建成功！");  // Order created successfully in simplified Chinese
                window.location.href = data.redirect_url;  // Redirect to the product page
            } else {
                alert(`创建订单时出错：${data.error}`);  // Error creating order in simplified Chinese
            }
        })
        .catch(error => console.error('错误:', error));  // Error in simplified Chinese
}

function fetchOrderDataByPrevPage() {
    var page = parseInt(document.getElementById('product-info').getAttribute('data-current-page'), 10);
    document.getElementById('product-info').setAttribute('data-current-page', page - 1);
    // Call the AJAX function
    fetchOrderData();
}
function fetchOrderDataByNextPage() {
    var page = parseInt(document.getElementById('product-info').getAttribute('data-current-page'), 10);
    document.getElementById('product-info').setAttribute('data-current-page', page + 1);
    // Call the AJAX function
    fetchOrderData();
}

document.addEventListener('DOMContentLoaded', () => {
    // Set interval to update the chart and latest prices every second
    setInterval(fetchDataAndUpdateChart, 1000);
    setInterval(fetchOrderData, 1000)

    // Call initially to render the chart and prices immediately
    fetchDataAndUpdateChart();

});
