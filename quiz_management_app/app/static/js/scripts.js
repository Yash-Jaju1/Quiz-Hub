// Payment Gateway Integration (Stripe)
document.addEventListener('DOMContentLoaded', function() {
    // Handle quiz purchase
    const purchaseButtons = document.querySelectorAll('.purchase-quiz');
    purchaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const quizId = this.getAttribute('data-quiz-id');
            alert(`Purchase quiz ${quizId} - Redirecting to payment...`);
            // Integrate Stripe payment here
        });
    });

    // Handle subscription
    const subscribeButtons = document.querySelectorAll('.subscribe-btn');
    subscribeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const plan = this.getAttribute('data-plan');
            alert(`Subscribing to ${plan} plan - Redirecting to payment...`);
            // Integrate Stripe subscription here
        });
    });
});