// static/script.js

document.getElementById('fetchButton').addEventListener('click', function () {
    var stockSymbol = document.getElementById('stockSymbol').value;

    // Send an AJAX request to fetch data
    fetch('/fetch_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'stockSymbol=' + stockSymbol,
    })
    .then(response => response.json())
    .then(data => {
        // Use the data to update the chart
        updateChart(data.labels, data.actual_prices, data.fitted_values, data.forecasted_prices);
    })
    .catch(error => console.error('Error:', error));
});

function updateChart(labels, actualPrices, fittedValues, forecastedPrices) {
    var ctx = document.getElementById('stockChart').getContext('2d');
    var stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Prices',
                    borderColor: 'blue',
                    data: actualPrices,
                },
                {
                    label: 'Fitted Values',
                    borderColor: 'red',
                    data: fittedValues,
                },
                {
                    label: 'Forecasted Prices',
                    borderColor: 'green',
                    data: forecastedPrices,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
        },
    });
}
