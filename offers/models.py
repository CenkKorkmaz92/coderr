from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """
    Model representing a service offer on the Coderr platform.
    
    Business users create offers for their services, which can have multiple
    pricing tiers (basic, standard, premium) through related OfferDetail instances.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of the offer."""
        return self.title

    @property
    def min_price(self):
        """Get the minimum price among all offer details."""
        details = self.details.all()
        return min([d.price for d in details]) if details else None

    @property
    def min_delivery_time(self):
        """Get the minimum delivery time among all offer details."""
        details = self.details.all()
        return min([d.delivery_time_in_days for d in details]) if details else None


class OfferDetail(models.Model):
    """
    Model representing specific pricing tiers for an offer.
    
    Each offer can have multiple details (basic, standard, premium) with
    different pricing, features, and delivery times.
    """
    
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        """Return string representation of the offer detail."""
        return f"{self.offer.title} - {self.title} ({self.offer_type})"
