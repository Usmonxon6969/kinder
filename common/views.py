from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def websocket_test(request):
    """Test page for WebSocket connections"""
    return render(request, 'websocket_test.html')