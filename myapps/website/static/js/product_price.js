// Function to determine tick font size based on screen width
function getTickFontSize() {
    return window.innerWidth < 992 ? 8 : 12; // Smaller font for screens narrower than 600px
}

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
            var localSecondTimestamps = data['time_60_seconds'].map(function (timestamp) {
                // Convert to local time by adjusting with timezone offset
                return new Date(new Date(timestamp).getTime() - timezoneOffset).toISOString();
            });

            var localTimeRange = data["time_range"].map(function (timestamp) {
                // Convert to local time by adjusting with timezone offset
                return new Date(new Date(timestamp).getTime() - timezoneOffset).toISOString();
            });

            var localTimeSecondRange = data["time_second_range"].map(function (timestamp) {
                // Convert to local time by adjusting with timezone offset
                return new Date(new Date(timestamp).getTime() - timezoneOffset).toISOString();
            });

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
            var tickformat = '.6f'
            if (data['digit'] === 8) {
                tickformat = '.8f'
            } else if (data['digit'] === 7) {
                tickformat = '.7f'
            } else if (data['digit'] === 6) {
                tickformat = '.6f'
            } else if (data['digit'] === 5) {
                tickformat = '.5f'
            } else if (data['digit'] === 4) {
                tickformat = '.4f'
            } else if (data['digit'] === 3) {
                tickformat = '.3f'
            } else {
                tickformat = '.2f'
            }
            var layout = {
                dragmode: 'zoom',
                margin: {
                    r: 10,
                    t: 15,
                    b: 30,
                    l: 80
                },
                showlegend: false,
                xaxis: {
                    autorange: false,
                    domain: [0, 1],
                    range: localTimeRange,
                    type: 'date',
                    fixedrange: true,
                    tickfont: {
                        size: getTickFontSize() // X-axis label font size
                    },
                    rangeslider: {
                        visible: false,
                        range: localTimeRange
                    },
                },
                yaxis: {
                    autorange: false,
                    domain: [0, 1],
                    range: data["price_range"],
                    type: 'linear',
                    fixedrange: true,  // Prevent zooming on y-axis
                    tickformat: tickformat,
                    ticks: 'outside',  // Optional: place ticks outside for better visibility
                    tickfont: {
                        size: getTickFontSize() // X-axis label font size
                    },
                    dtick: (data["price_range"][1] - data["price_range"][0]) / 6,  // Increase grid lines (10 grid lines)
                    type: 'linear',
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

            Plotly.react('chart-minute', [trace, lineData], layout, config);

            var lineDataInSeconds = {
                x: localSecondTimestamps,  // Use localTimestamps for x-axis
                y: data['price_60_second'],
                line: {
                    color: 'rgb(46, 60, 255)',
                    width: 1,
                },
                type: 'scatter',
                mode: 'lines',
                name: '即時走勢(秒)'
            };

            var layoutInSecond = {
                dragmode: 'zoom',
                margin: {
                    r: 10,
                    t: 15,
                    b: 30,
                    l: 80
                },
                showlegend: false,
                xaxis: {
                    autorange: false,
                    domain: [0, 1],
                    range: localTimeSecondRange,
                    type: 'date',
                    tickfont: {
                        size: getTickFontSize() // X-axis label font size
                    },
                    fixedrange: true,
                    rangeslider: {
                        visible: false,
                        range: localTimeSecondRange
                    },
                },
                yaxis: {
                    autorange: false,
                    domain: [0, 1],
                    range: data["price_second_range"],
                    tickformat: tickformat,
                    ticks: 'outside',  // Optional: place ticks outside for better visibility
                    dtick: (data["price_second_range"][1] - data["price_second_range"][0]) / 6,  // Increase grid lines (10 grid lines)
                    type: 'linear',
                    tickfont: {
                        size: getTickFontSize() // X-axis label font size
                    },
                    fixedrange: true,  // Prevent zooming on y-axis
                    showgrid: true,  // Ensure grid lines are visible
                },
            };

            Plotly.react('chart-second', [lineDataInSeconds], layoutInSecond, config);


            // Update the latest prices
            updateLatestPrices(closePrices, data['timestamps'], data['time_60_seconds'][data['time_60_seconds'].length - 1], data['digit']);
            updateTransactionInfo(
                closePrices[closePrices.length - 1],
                data['current_time'],
                data['next_settlement_time'],
                data['order_deadline_time'],
                data['digit'],
            )
        });
}

function fetchOrderData() {
    var productType = document.getElementById('product-info').getAttribute('data-product-type');
    var page = document.getElementById('product-info').getAttribute('data-current-page');
    var current_price = document.getElementById('product-info').getAttribute('data-current-price');
    var digit = document.getElementById('product-info').getAttribute('data-current-price-digit');

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
                            <td>$${order.price.toFixed(digit)}</td>
                            <td>${order.quantity}</td>
                            <td>${order.direction}</td>
                            <td>${order.created_at}</td>
                            <td>${order.settled_at || "N/A"}</td>
                            <td>${order.settled_price || "N/A"}</td>
                            <td>${order.status}</td>
                            <td style="color: ${profitColor}">${order.profit !== null ? `$${order.profit.toFixed(digit)}` : "<span class='text-muted'>N/A</span>"}</td>
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
function updateLatestPrices(prices, timestamps, current_time, digit) {
    const latestPricesList = document.getElementById('latest-prices');
    latestPricesList.innerHTML = ''; // Clear previous entries

    // Get the latest 5 prices
    const latestPrices = prices.slice(-5).reverse();
    var latestTimestamps = timestamps.slice(-4);
    latestTimestamps.push(current_time);
    latestTimestamps = latestTimestamps.reverse();
    latestPrices.forEach((price, index) => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        listItem.innerHTML = `
            <span>${new Date(latestTimestamps[index]).toLocaleString()}</span>
            <span class="badge bg-primary rounded-pill">$${price.toFixed(digit)}</span>
        `;
        latestPricesList.appendChild(listItem);
    });
}

// Function to update the transaction info card with current price, time, and deadlines
function updateTransactionInfo(currentPrice, currentTime, settlementTime, orderDeadline, digit) {
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
    document.getElementById('product-info').setAttribute('data-current-price-digit', digit);
    document.getElementById('current-price').textContent = `$${currentPrice.toFixed(digit)}`;
    document.getElementById('current-time').textContent = currentLocalTime;
    document.getElementById('settlement-time').textContent = `${settlementLocalTime} -- (${timeToSettleMent})`;
    document.getElementById('order-deadline').textContent = `${orderDeadlineLocalTime} -- (${timeToOrderDeadline})`;
}


// Handle the "Buy Up" button click
// Reusable function to handle "Buy" actions
function handleBuyAction(action) {
    const currentUser = "{{ user.username }}";  // Use Django template tag to pass current user
    const productType = "usd-eur";  // Adjust based on your product
    const currentPrice = document.getElementById('current-price').innerText.replace('$', ''); // Get the current price
    var quantity = 100; // Default quantity
    if (action === "buy_up") {
        // Get the quantity from the buy-up input field
        quantity = parseInt(document.getElementById("buy-up-quantity").value) || 100; // Default to 100 if the value is not a number
    } else if (action === "buy_down") {
        // Get the quantity from the buy-down input field
        quantity = parseInt(document.getElementById("buy-down-quantity").value) || 100; // Default to 100 if the value is not a number
    }
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
            quantity: quantity,
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
