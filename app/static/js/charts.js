// Charts for Analytics Dashboard

// Colors for charts
const colors = {
    primary: '#007bff',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    secondary: '#6c757d'
};

const chartColors = [
    colors.primary,
    colors.success,
    colors.warning,
    colors.danger,
    colors.info,
    colors.secondary
];

// Load analytics data and create charts
fetch('/api/analytics_data')
    .then(response => response.json())
    .then(data => {
        createCategoryChart(data.categories);
        createStatusChart(data.statuses);
        createFoodDayChart(data.food_days);
    })
    .catch(error => {
        console.error('Error loading analytics data:', error);
    });

function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: chartColors.slice(0, data.labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Distribution of Complaints by Category'
                }
            }
        }
    });
}

function createStatusChart(data) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    const backgroundColors = data.labels.map(label => {
        switch(label.toLowerCase()) {
            case 'pending': return colors.warning;
            case 'resolved': return colors.success;
            case 'rejected': return colors.danger;
            default: return colors.secondary;
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Number of Complaints',
                data: data.data,
                backgroundColor: backgroundColors,
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Complaint Status Distribution'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createFoodDayChart(data) {
    const ctx = document.getElementById('foodDayChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Food Complaints',
                data: data.data,
                borderColor: colors.danger,
                backgroundColor: colors.danger + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: colors.danger,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Food Complaints by Day of Week'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}