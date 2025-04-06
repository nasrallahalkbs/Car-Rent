// Rental History Visualization 

// Function to initialize charts on the page
function initializeCharts(rentalData) {
    // Parse data from JSON format
    const data = typeof rentalData === 'string' ? JSON.parse(rentalData) : rentalData;

    // Initialize the category distribution chart
    initializeCategoryChart(data.categoryCounts);
    
    // Initialize the spending over time chart
    initializeSpendingChart(data.monthlySpending);
    
    // Initialize rental duration chart
    initializeDurationChart(data.durationDistribution);
    
    // Initialize rental status chart
    initializeStatusChart(data.statusDistribution);
}

// Function to initialize the category distribution chart
function initializeCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e',
                    '#e74a3b',
                    '#5a5c69'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: 'Car Categories You\'ve Rented',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Function to initialize the spending over time chart
function initializeSpendingChart(spendingData) {
    const ctx = document.getElementById('spendingChart').getContext('2d');
    
    const months = Object.keys(spendingData);
    const spending = Object.values(spendingData);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Rental Spending ($)',
                data: spending,
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderColor: 'rgba(78, 115, 223, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 5,
                pointHoverBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointHoverBorderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Your Rental Spending Over Time',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Function to initialize the rental duration chart
function initializeDurationChart(durationData) {
    const ctx = document.getElementById('durationChart').getContext('2d');
    
    const durations = Object.keys(durationData);
    const counts = Object.values(durationData);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: durations,
            datasets: [{
                label: 'Number of Rentals',
                data: counts,
                backgroundColor: 'rgba(28, 200, 138, 0.8)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Rental Duration Distribution',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

// Function to initialize the rental status chart
function initializeStatusChart(statusData) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    const statuses = Object.keys(statusData);
    const counts = Object.values(statusData);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: statuses,
            datasets: [{
                data: counts,
                backgroundColor: [
                    '#1cc88a', // completed
                    '#4e73df', // confirmed
                    '#f6c23e', // pending
                    '#e74a3b'  // cancelled
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: 'Reservation Status Distribution',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}
