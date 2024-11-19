from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import util
import random
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested entry does not exist."
        })
    html_content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get("q")
    entries = util.list_entries()
    matching_entries = [entry for entry in entries if query.lower() in entry.lower()]
    
    if query in entries:
        return redirect('entry', title=query)
    
    return render(request, "encyclopedia/search_result.html", {
        "query": query,
        "entries": matching_entries
    })

def new_page(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        
        if title in util.list_entries():
            return render(request, "encyclopedia/error.html", {
                "message": "An entry with this title already exists."
            })
        
        util.save_entry(title, content)
        return redirect('entry', title=title)

    return render(request, "encyclopedia/new_page.html")

def edit(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested entry does not exist."
        })
    
    if request.method == "POST":
        new_content = request.POST.get("content")
        util.save_entry(title, new_content)
        return redirect('entry', title=title)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })

def random_page(request):
    entries = util.list_entries()
    random_title = random.choice(entries)
    return redirect('entry', title=random_title)