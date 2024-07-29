from django.urls import include, path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexPostsView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsView.as_view(), name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<str:cur_username>/', views.ProfileListView.as_view(),
         name='profile'),
    path('user/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('auth/', include('django.contrib.auth.urls')),
    
]
