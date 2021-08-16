from django import template

register = template.Library()


@register.filter(name="star")
def range_tag(num, color="hotpink"):
    text = ""
    for i in range(int(num)):
        text += "<i class=\"bi bi-star-fill\" style=\"color: hotpink\"></i>"

    if num-int(num) > 0:
        text += "<i class=\"bi bi-star-half\" style=\"color: hotpink\"></i>"

    return text


@register.filter(name="shield")
def shield_tag(num, max_count=5):
    text = ""
    for i in range(num):
        text += "<i class=\"bi bi-shield-fill\" style=\"color:limegreen; margin-right: 2px\"></i>"
    for i in range(max_count-num):
        text += "<i class=\"bi bi-shield-fill\" style=\"color:rgba(0, 0, 0, 0.2); margin-right: 2px\"></i>"

    return text


@register.filter(name="heart")
def heart_tag(num, max_count=5):
    text = ""
    for i in range(num):
        text += "<i class=\"bi bi-heart-fill\" style=\"color:hotpink; margin-right: 2px\"></i>"

    for i in range(max_count-num):
        text += "<i class=\"bi bi-heart-fill\" style=\"color:rgba(0, 0, 0, 0.2); margin-right: 2px\"></i>"

    return text
