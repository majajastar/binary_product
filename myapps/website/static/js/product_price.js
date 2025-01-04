// Utility Functions
function getTickFontSize() {
    return window.innerWidth < 992 ? 8 : 12;
}

function adjustToLocalTime(timestamps) {
    const timezoneOffset = new Date().getTimezoneOffset() * 60 * 1000;
    return timestamps.map(ts => new Date(new Date(ts).getTime() - timezoneOffset).toISOString());
}

function formatTick(digit) {
    return digit >= 3 && digit <= 8 ? `.${digit}f` : '.2f';
}

// Chart Update Functions
async function fetchDataAndUpdateChart() {
    var productType = document.getElementById('product-info').getAttribute('data-product-type');
    fetch(`/get-product-data/${productType}/`)
        .then(response => response.json())
        .then(data => {
            // Get the local timezone offset in milliseconds

            var timezoneOffset = new Date().getTimezoneOffset() * 60 * 1000;

            // Adjust timestamps to local time by adding the timezone offset
            var localTimestamps = adjustToLocalTime(data['timestamps']);
            var localSecondTimestamps = adjustToLocalTime(data['time_60_seconds']);
            var localTimeRange = adjustToLocalTime(data['time_range']);
            var localTimeSecondRange = adjustToLocalTime(data['time_second_range']);

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

// Order Data Update Functions
async function fetchOrderData() {
    const productType = document.getElementById('product-info').getAttribute('data-product-type');
    const page = document.getElementById('product-info').getAttribute('data-current-page');
    const currentPrice = document.getElementById('product-info').getAttribute('data-current-price');
    try {
        const response = await fetch(`/get-order-data/${productType}/?page=${page}&current_price=${currentPrice}`);
        const data = await response.json();
        const userFundsElement = document.getElementById('user_funds').querySelector('span');
        userFundsElement.textContent = `$${data.funds.toFixed(6)}`; // Format to 6 decimal places
        // Update the buy-down limit
        const userBuyDownLimitElement = document.getElementById('user_buy_down_limit').querySelector('span');
        userBuyDownLimitElement.textContent = `$${data.buy_down_limit.toFixed(6)}`; // Format to 6 decimal places
        renderOrderTable(data.orders, data.has_next, data.has_previous, data.digit);
    } catch (error) {
        console.error("Error fetching order data:", error);
    }
}

function renderOrderTable(orders, hasNext, hasPrevious, digit) {
    const tableBody = document.querySelector("table tbody");
    if (!tableBody) return;

    tableBody.innerHTML = ""; // Clear existing rows

    orders.forEach(order => {
        const row = document.createElement("tr");
        row.style.backgroundColor = order.status === "completed" ? "#E3E3E3" : "white";

        // Determine the direction label and color
        let directionLabel = "";
        let directionColor = "";
        if (order.direction === "buy_up") {
            directionLabel = "買漲";
            directionColor = "red";
        } else if (order.direction === "buy_down") {
            directionLabel = "買跌";
            directionColor = "green";
        }

        // Set profit color
        const profitColor = order.profit > 0 ? 'red' : order.profit < 0 ? 'green' : 'black';

        // Convert created_at to local time zone
        const timezoneOffset = new Date().getTimezoneOffset() * 60;
        const createdAtLocal = new Date(new Date(order.created_at).getTime()).toLocaleTimeString();
        const settledAtLocal = new Date(new Date(order.settled_at).getTime()).toLocaleTimeString();
        row.innerHTML = `
            <td>${order.product}</td>
            <td>$${order.price.toFixed(digit)}</td>
            <td>${order.quantity}</td>
            <td style="color: ${directionColor}">${directionLabel}</td>
            <td>${createdAtLocal}</td>  <!-- Local timestamp here -->
            <td>${settledAtLocal || "N/A"}</td>
            <td>${order.settled_price ? order.settled_price.toFixed(digit) : "N/A"}</td>
            <td>${order.status === "completed" ? "訂單完成" : "訂單成立"}</td>  <!-- Display the correct status text -->
            <td style="color: ${profitColor}">${order.profit !== null ? `$${order.profit.toFixed(digit)}` : "-"}</td>
        `;

        tableBody.appendChild(row);
    });

    document.querySelector("#next-page").disabled = !hasNext;
    document.querySelector("#previous-page").disabled = !hasPrevious;
}

// UI Update Functions
function updateLatestPrices(prices, timestamps, current_time, digit) {
    const latestPricesList = document.getElementById('latest-prices');
    latestPricesList.innerHTML = '';

    const latestPrices = prices.slice(-5).reverse();
    const latestTimestamps = [...timestamps.slice(-4), current_time].reverse();

    latestPrices.forEach((price, index) => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        listItem.innerHTML = `
            <span>${new Date(latestTimestamps[index]).toLocaleString()}</span>
            <span class="badge bg-primary rounded-pill ms-2">$${price.toFixed(digit)}</span>
        `;
        latestPricesList.appendChild(listItem);
    });
}

function updateTransactionInfo(currentPrice, currentTime, settlementTime, orderDeadline, digit) {
    const formatTime = (time) => new Date(time).toLocaleTimeString();
    const calculateTimeDiff = (end, start) => Math.max(0, Math.floor((new Date(end) - new Date(start)) / 1000));
    const formatTimeDiff = (seconds) => `${Math.floor(seconds / 60)}:${seconds % 60 < 10 ? '0' : ''}${seconds % 60}`;
    document.getElementById('product-info').setAttribute('data-current-price', currentPrice);
    document.getElementById('product-info').setAttribute('data-current-price-digit', digit);
    document.getElementById('current-price').textContent = `$${currentPrice.toFixed(digit)}`;
    document.getElementById('current-time').textContent = formatTime(currentTime);
    document.getElementById('settlement-time').textContent = `${formatTime(settlementTime)} -- (${formatTimeDiff(calculateTimeDiff(settlementTime, currentTime))})`;
    document.getElementById('order-deadline').textContent = `${formatTime(orderDeadline)} -- (${formatTimeDiff(calculateTimeDiff(orderDeadline, currentTime))})`;
}

// Trade Type Handling
function updateTradeType() {
    const toggle = document.getElementById("tradeToggle");
    const label = document.getElementById("tradeTypeLabel");
    const expectedValue = document.getElementById("expected-value");
    const type = toggle.checked ? "buy_down" : "buy_up";

    // Update the text and color for the trade type label
    if (toggle.checked) {
        label.textContent = "買跌";
        label.style.color = "green"; // Set color to green for 買跌
        expectedValue.style.color = "green"; // Set expected value color to green for 買跌
    } else {
        label.textContent = "買漲";
        label.style.color = "red"; // Set color to red for 買漲
        expectedValue.style.color = "red"; // Set expected value color to red for 買漲
    }

    expectedValue.textContent = calculateExpectedValue(type);
}


function calculateExpectedValue(type) {
    const quantity = parseInt(document.getElementById("trade-quantity").value, 10) || 1000;
    const currentPrice = parseFloat(document.getElementById('current-price').innerText.replace('$', ''));
    return `$${(quantity * currentPrice).toFixed(6)}`;
}

// Handle the "Buy Up" button click
// Reusable function to handle "Buy" actions
function handleBuyAction(action) {
    const currentUser = "{{ user.username }}";  // Use Django template tag to pass current user
    const productType = document.getElementById('product-info').getAttribute('data-product-type');
    const currentPrice = document.getElementById('current-price').innerText.replace('$', ''); // Get the current price
    const quantity = parseInt(document.getElementById("trade-quantity").value, 10) || 1000;
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

function placeOrder() {
    const toggle = document.getElementById("tradeToggle");
    if (toggle.checked) {
        handleBuyAction('buy_down');
    } else {
        handleBuyAction('buy_up');
    }
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

// Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
    setInterval(fetchDataAndUpdateChart, 1000);
    setInterval(fetchOrderData, 1000);

    await fetchDataAndUpdateChart();
    await fetchOrderData();
    updateTradeType();
});
