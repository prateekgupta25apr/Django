from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms  import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .form import Todooform
from .models import Todoo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def ctodoo(request):
    if request.method =='GET':
        return render(request,'ctodoo.html',{'form':Todooform()})
    else:
        try:
            form=Todooform(request.POST)
            newtodoo=form.save(commit=False)
            newtodoo.user=request.user
            newtodoo.save()
            return redirect(current)
        except ValueError:
            return render(request, 'ctodoo.html', {'form': Todooform(),'error':'Bad data passed in.Try again.'})
@login_required
def current(request):
    todoos= Todoo.objects.filter(user=request.user, ended__isnull=True).order_by('-created')
    return render(request,'current.html',{'todoos':todoos})
@login_required
def completed(request):
    todoos= Todoo.objects.filter(user=request.user, ended__isnull=False).order_by('-ended')
    return render(request,'completed.html',{'todoos':todoos})
@login_required
def completetodoo(request,todoo_pk):
    todoo = get_object_or_404(Todoo, pk=todoo_pk, user=request.user)
    if request.method == 'POST':
        todoo.ended=timezone.now()
        todoo.save()
        return redirect(current)
@login_required
def deletetodoo(request,todoo_pk):
    todoo = get_object_or_404(Todoo, pk=todoo_pk, user=request.user)
    if request.method == 'POST':
        todoo.delete()
        return redirect(current)
@login_required
def viewtodoo(request,todoo_pk):
    todoo=get_object_or_404(Todoo,pk=todoo_pk,user=request.user)
    if request.method == 'GET':
        form = Todooform(instance=todoo)
        return render(request, 'viewtodoo.html', {'todoos': todoo, 'form': form})
    else:
        try:
            form = Todooform(request.POST,instance=todoo)
            form.save()
            return redirect(current)
        except ValueError:
            return render(request, 'ctodoo.html', {'form': Todooform(),'error':'Bad info'})

def home(request):
    return render(request,'home.html',{})
def lin(request):
    if request.method =='GET':
        return render(request,'lin.html',{'form':AuthenticationForm()})
    else:
        user=authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request, 'lin.html', {'form': AuthenticationForm(),'error':"Username and password didn't match"})
        else:
            login(request, user)
            return redirect(current)
def lout(request):
    if request.method=='POST':
        logout(request)
        return redirect(home)
def sign(request):
    if request.method =='GET':
        return render(request,'sign.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1']==request.POST['password2']:
            try:
             user=User.objects.create_user(request.POST['username'],password=request.POST['password1'])
             user.save()
             login(request,user)
             return redirect('current')
            except IntegrityError:
                return render(request, 'sign.html', {'form': UserCreationForm(),
                                                     'error': "User name is in use already.Please use a new user name"})

        else:
            return render(request, 'sign.html', {'form': UserCreationForm(),'error':"Passwords didn't matched"})