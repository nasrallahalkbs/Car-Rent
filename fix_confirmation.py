#!/usr/bin/env python3

with open('templates/confirmation.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Fix the confirmation page to handle pending reservations
content = content.replace("""<div class="card shadow mb-5">
        <div class="card-body text-center p-5">
            <div class="mb-4">
                <i class="fas fa-check-circle text-success fa-5x"></i>
            </div>
            <h1 class="mb-4">Thank You for Your Reservation!</h1>
            <p class="lead mb-4">Your reservation has been confirmed. We've sent a confirmation email to your registered email address.</p>
            <div class="d-flex justify-content-center">
                <a href="{% url 'my_reservations' %}" class="btn btn-primary btn-lg me-3">
                    <i class="fas fa-list-alt me-2"></i>View My Reservations
                </a>
                <a href="{% url 'index' %}" class="btn btn-outline-primary btn-lg">
                    <i class="fas fa-home me-2"></i>Return to Home
                </a>
            </div>
        </div>
    </div>""", """<div class="card shadow mb-5">
        <div class="card-body text-center p-5">
            <div class="mb-4">
                {% if reservation.status == 'pending' %}
                <i class="fas fa-clock text-warning fa-5x"></i>
                {% else %}
                <i class="fas fa-check-circle text-success fa-5x"></i>
                {% endif %}
            </div>
            
            <h1 class="mb-4">Thank You for Your Reservation!</h1>
            
            {% if reservation.status == 'pending' %}
            <p class="lead mb-4">Your reservation is pending approval. Our admin team will review your request shortly. We'll send a confirmation email once approved.</p>
            <div class="alert alert-info mb-4">
                <i class="fas fa-info-circle me-2"></i>
                <span>For direct bookings with credit card information, our team needs to verify your payment details before confirming the reservation.</span>
            </div>
            {% else %}
            <p class="lead mb-4">Your reservation has been confirmed. We've sent a confirmation email to your registered email address.</p>
            {% endif %}
            
            <div class="d-flex justify-content-center">
                <a href="{% url 'my_reservations' %}" class="btn btn-primary btn-lg me-3">
                    <i class="fas fa-list-alt me-2"></i>View My Reservations
                </a>
                <a href="{% url 'index' %}" class="btn btn-outline-primary btn-lg">
                    <i class="fas fa-home me-2"></i>Return to Home
                </a>
            </div>
        </div>
    </div>""")

# Fix badge colors for status display
content = content.replace("""                            <th>Status:</th>
                            <td>
                                <span class="badge bg-success">{{ reservation.status|title }}</span>
                            </td>""", """                            <th>Status:</th>
                            <td>
                                {% if reservation.status == 'pending' %}
                                <span class="badge bg-warning text-dark">{{ reservation.status|title }}</span>
                                {% else %}
                                <span class="badge bg-success">{{ reservation.status|title }}</span>
                                {% endif %}
                            </td>""")

content = content.replace("""                            <th>Payment Status:</th>
                            <td>
                                <span class="badge bg-success">{{ reservation.payment_status|title }}</span>
                            </td>""", """                            <th>Payment Status:</th>
                            <td>
                                {% if reservation.payment_status == 'pending' %}
                                <span class="badge bg-warning text-dark">{{ reservation.payment_status|title }}</span>
                                {% else %}
                                <span class="badge bg-success">{{ reservation.payment_status|title }}</span>
                                {% endif %}
                            </td>""")

with open('templates/confirmation.html', 'w', encoding='utf-8') as file:
    file.write(content)

print("Confirmation template updated successfully!")
