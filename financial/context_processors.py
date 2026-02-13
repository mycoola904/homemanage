from financial.services.households import get_user_households, resolve_current_household


def household_context(request):
    if not request.user.is_authenticated:
        return {
            "current_household": None,
            "available_households": [],
        }

    context = resolve_current_household(request)
    return {
        "current_household": context.household,
        "available_households": get_user_households(request.user),
    }
