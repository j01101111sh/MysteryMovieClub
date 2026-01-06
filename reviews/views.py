from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import MysteryContent, Review
from .forms import ReviewForm

def mystery_list(request):
    """
    Displays a list of all mystery content, annotated with their average rating.
    """
    # Optimized query: Prefetch related info if needed, or just aggregate
    contents = MysteryContent.objects.annotate(
        avg_rating=Avg('reviews__overall_quality')
    ).order_by('title')
    
    context = {
        'contents': contents
    }
    return render(request, 'reviews/mystery_list.html', context)

def mystery_detail(request, pk):
    """
    Displays details for a specific mystery title and its reviews.
    """
    content = get_object_or_404(MysteryContent, pk=pk)
    reviews = content.reviews.select_related('user').all()
    
    # Calculate averages for this specific item to display in the template
    averages = content.reviews.aggregate(
        avg_quality=Avg('overall_quality'),
        avg_difficulty=Avg('difficulty')
    )

    context = {
        'content': content,
        'reviews': reviews,
        'avg_quality': averages['avg_quality'],
        'avg_difficulty': averages['avg_difficulty'],
    }
    return render(request, 'reviews/mystery_detail.html', context)

@login_required
def add_review(request, pk):
    """
    Handles the submission of a new review for a specific mystery title.
    """
    content = get_object_or_404(MysteryContent, pk=pk)

    # Check if user already reviewed this to prevent duplicates (optional but recommended)
    existing_review = Review.objects.filter(content=content, user=request.user).first()
    if existing_review:
        # You might want to redirect to an 'edit' view or just show the detail page
        return redirect('reviews:mystery_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.content = content
            review.user = request.user
            review.save()
            return redirect('reviews:mystery_detail', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'content': content
    }
    return render(request, 'reviews/add_review.html', context)