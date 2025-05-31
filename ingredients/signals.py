from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ingredient
from reports.tasks import check_low_ingredients


@receiver(post_save, sender=Ingredient)
def check_ingredient_threshold(sender, instance, **kwargs):
    """
    Signal handler to check if an ingredient is below threshold when saved
    This will trigger the check_low_ingredients task
    """
    if instance.is_below_threshold:
        # Run the task asynchronously
        check_low_ingredients.delay()