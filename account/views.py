from django.http import request
from django.shortcuts import render,redirect
from django.views import View
from .forms import UserRigsterationForm ,UserLoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login ,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation


class RegisterView(View):
    form_class = UserRigsterationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request , *args , **kwargs)


    def get(self , request):
        form = self.form_class
        return render(request ,'account/register.html',{'form':form})

    def post(self , request):
        form =self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['name'],cd['email'],cd['password1'])
            messages.success(request , 'your register is successfully' , 'success')
            return redirect('home:home')
        return render(request ,'account/register.html',{'form':form})


class LoginView(View):
    form_class = UserLoginForm


    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request , *args , **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request , *args , **kwargs)

    def get(self , request):
        form = self.form_class
        return render(request , 'account/login.html' , {'form':form})


    def post(self , request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request , username=cd['name'] , password = cd['password'])
            if user is not None:
                login(request ,user)
                messages.success(request , ' login is successfully' , 'success')

                if self.next :
                    return redirect(self.next)

                return redirect('home:home')
            messages.error(request , 'name or password is wrong' , 'warning')
        return render(request , 'account/login.html' ,{'form':form})


class LogoutView( LoginRequiredMixin , View):

    def get(self , request):
        logout(request)
        messages.success(request , 'logout is succssfully' , 'success')
        return redirect('home:home')


class ProfileView(LoginRequiredMixin,View):

    def get(self , request , user_id):
        is_following = False
        user = User.objects.get(pk=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user = request.user, to_user = user)
        if relation.exists():
            is_following = True

        return render(request , 'account/profile.html' , {'user':user  , 'posts':posts , 'is_following':is_following })



class UserPasswordResetView(auth_views.PasswordResetView):
    template_name =  'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = 'account/password_reset_email.html'




class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
       template_name = 'account/password_reset_done.html'



class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account/password_reset_complete')




class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin , View):
    def get(self ,request , user_id):
        user = User.objects.get(id = user_id)
        relation = Relation.objects.filter(from_user = request.user , to_user = user)
        if relation.exists():
            messages.error(request , 'you are already following this user' , 'success')
        else :
            Relation(from_user = request.user , to_user = user).save()
            messages.success(request , ' you followed this user')
        return redirect ('account:user_profile', user.id)





class UserUnfollowView(LoginRequiredMixin ,View):
    def get(self ,request , user_id):
        user = User.objects.get(id = user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request , 'you are unfollow this user ' , 'success')

        else:
            messages.error(request , ' you are not following this user', 'danger')
        return redirect('account:user_profile' , user.id)