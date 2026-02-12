## Here is the current code for the Accounts url sidebar entry:

```html
<li>
        <a href="{% url 'financial:accounts-index' %}"
           class="is-drawer-close:tooltip is-drawer-close:tooltip-right flex items-center gap-2"
           data-tip="Accounts">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0 1 15.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 0 1 3 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 0 0-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 0 1-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 0 0 3 15h-.75M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm3 0h.008v.008H18V10.5Zm-12 0h.008v.008H6V10.5Z" />
            </svg>

            <span class="is-drawer-close:hidden">Accounts</span>
        </a>
      </li>
```

###  I want to make this a Menu with a title of Financial and Accounts as a sub-item using the following template:

```html
<ul class="menu bg-base-200 rounded-box w-56">
  <li class="menu-title">Financial</li>
  <li><a>Accounts</a></li>
</ul>
```

### While preserving the drawer functionality. This is so when I add future apps to Homemanage project, they will each have their own menu item per app.

### What would be way to accomplish this?