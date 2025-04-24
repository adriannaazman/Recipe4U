#!/usr/bin/env python3
import cgi, os, http.cookies

print("Content-Type: text/html")
print()  

cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
tags_cookie = cookie.get("tags")
if tags_cookie:
    tags = tags_cookie.value.split(',')
else:
    tags = []

form = cgi.FieldStorage()
new = form.getfirst("ingredient") 

if new and new not in tags:
    tags.append(new)


cookie['tags'] = ",".join(tags)
print(cookie.output()) 

with open('index.html') as f:
    html = f.read()

# 7. Generate the <li> elements for each tag
items = "".join(f"<li>{tag}</li>" for tag in tags)

html = html.replace(
    "<!-- The server will inject <li> elements here for each tag -->",
    items
)

print(html)
