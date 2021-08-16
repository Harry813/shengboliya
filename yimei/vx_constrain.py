# from django.shortcuts import HttpResponseRedirect, Http404
#
#
# class Constrainer:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#         print(response.user_agent)
#         # if response.META['HTTP_USER_AGENT'] != 'MicroMessenger':
#         #     return Http404
#         # else:
#         #     return request
