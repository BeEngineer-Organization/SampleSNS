from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, DeleteView # FormViewを追加
from django.urls import reverse_lazy # 追加
from django.shortcuts import render, get_object_or_404 # 追加
from django.db.models import OuterRef, Exists, Count

from .models import Post, Like, CustomUser # Likeを追加
from .forms import LikeForm, FollowUnfollowForm # 追加

# Create your views here.
def index(request):
    return render(request, "main/index.html")

def post_list(request):
    return render(request, "main/post_list.html")

class PostList(LoginRequiredMixin, ListView):
    """全投稿を表示"""
    model = Post
    template_name = "main/post_list.html"
    context_object_name = "post_objects"

class MyPost(LoginRequiredMixin, ListView):
    """自分の投稿のみ表示"""

    model = Post
    template_name = "main/mypost.html"
    context_object_name = "post_objects"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).annotate(
            likes_count=Count("likes_received")
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = CustomUser.objects.filter(id=self.request.user.id).annotate(
            follower_count=Count("followed_by", distinct=True),
            posts_count=Count("posted_by"),
        )
        return context

class OtherUserPostList(LoginRequiredMixin, ListView):
    model = Post
    template_name = "main/other_user_post_list.html"
    context_object_name = "post_objects"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(user=self.request.user)

        queryset = queryset.select_related("user")
        queryset = queryset.prefetch_related("tags")  # 追加

        likes = Like.objects.filter(user=self.request.user, target=OuterRef("pk"))
        following = CustomUser.objects.filter(
            followed_by=self.request.user, id=OuterRef("user")
        )
        queryset = queryset.annotate(
            is_liked=Exists(likes),
            is_followed=Exists(following)
        )
        return queryset


        
class LikeCreate(LoginRequiredMixin, FormView):
    template_name = "other_user_post_list.html"
    form_class = LikeForm
    success_url = reverse_lazy("other_user_post_list")

    def form_valid(self, form):
        target = get_object_or_404(Post, pk=self.kwargs["pk"])
        like = Like(target=target, user=self.request.user)
        like.save()
        return super().form_valid(form)

class LikeDelete(LoginRequiredMixin, DeleteView):
    model = Like
    success_url = reverse_lazy("other_user_post_list")

    def get_object(self, queryset=None):
        target = get_object_or_404(Post, pk=self.kwargs["pk"])
        return get_object_or_404(Like, target=target, user=self.request.user)

class Follow(LoginRequiredMixin, FormView):
    template_name = "main/other_user_post_list.html"
    form_class = FollowUnfollowForm
    success_url = reverse_lazy("other_user_post_list")

    def form_valid(self, form):
        user_to_follow = CustomUser.objects.get(pk=self.kwargs["pk"]) # User→CustomUser
        self.request.user.following.add(user_to_follow)
        return super().form_valid(form)


class Unfollow(LoginRequiredMixin, FormView):
    template_name = "main/other_user_post_list.html"
    form_class = FollowUnfollowForm
    success_url = reverse_lazy("other_user_post_list")

    def form_valid(self, form):
        user_to_unfollow = CustomUser.objects.get(pk=self.kwargs["pk"]) # User→CustomUser
        self.request.user.following.remove(user_to_unfollow)
        return super().form_valid(form)