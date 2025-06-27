from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """
    Model representing customer reviews for business users.
    
    Allows customers to rate and review business users based on their service quality.
    Each customer can only review a business user once (unique constraint).
    """
    
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')
        ordering = ['-updated_at']

    def __str__(self):
        """Return string representation of the review."""
        return f"Review {self.id} for {self.business_user.username} by {self.reviewer.username}"
