from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import TemplateView  # MAKE SURE THIS IS IMPORTED
from rest_framework import permissions

# Only import drf_yasg if available
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    DRF_YASG_AVAILABLE = True
except ImportError:
    DRF_YASG_AVAILABLE = False
    print("Warning: drf_yasg not installed. API documentation disabled.")

# Simple root view
def root_view(request):
    return HttpResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Poll API - Developed by Kopila Devkota</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
                .developer { color: #764ba2; font-weight: bold; font-size: 1.2em; }
                .subtitle {
                    color: #666;
                    margin: 30px 0 20px 0;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    font-size: 1.2em;
                }
                .quick-links {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .link-card {
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 20px;
                    border-radius: 15px;
                    transition: transform 0.3s;
                    text-decoration: none;
                    display: block;
                    text-align: center;
                }
                .link-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
                .link-card h3 { color: #333; margin-bottom: 10px; }
                .link-card .icon { font-size: 2em; margin-bottom: 10px; }
                .link-card p { color: #666; font-size: 0.9em; }
                .method {
                    display: inline-block;
                    padding: 3px 10px;
                    border-radius: 5px;
                    font-size: 0.8em;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { background: #61affe; color: white; }
                .post { background: #49cc90; color: white; }
                .endpoint {
                    background: #f5f5f5;
                    padding: 12px;
                    margin: 10px 0;
                    border-left: 3px solid #667eea;
                    font-family: monospace;
                }
                .badge {
                    display: inline-block;
                    background: #28a745;
                    color: white;
                    padding: 3px 10px;
                    border-radius: 20px;
                    font-size: 0.75em;
                    margin-left: 10px;
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e0e0e0;
                    color: #666;
                }
                a { color: #667eea; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🗳️ Poll Management API</h1>
                <p>Professional REST API for managing polls and votes</p>
                <p class="developer">Developed by <strong>Kopila Devkota</strong></p>
                
                <div class="subtitle">📌 Quick Navigation</div>
                <div class="quick-links">
                    <a href="/ui/" class="link-card">
                        <div class="icon">🎨</div>
                        <h3>Voting Interface</h3>
                        <p>User-friendly UI to vote and view charts</p>
                    </a>
                    <a href="/bulk/" class="link-card">
                        <div class="icon">📝</div>
                        <h3>Bulk Poll Creator</h3>
                        <p>Create multiple polls at once</p>
                    </a>
                    <a href="/bulk-vote/" class="link-card">
                        <div class="icon">🗳️</div>
                        <h3>Bulk Voting</h3>
                        <p>Vote for multiple polls at once</p>
                    </a>
                    <a href="/admin/" class="link-card">
                        <div class="icon">🔧</div>
                        <h3>Admin Panel</h3>
                        <p>Create polls, manage choices</p>
                    </a>
                    <a href="/api/v1/polls/" class="link-card">
                        <div class="icon">📡</div>
                        <h3>Polls API</h3>
                        <p>View raw JSON data</p>
                    </a>
                    <a href="/swagger/" class="link-card">
                        <div class="icon">📚</div>
                        <h3>API Documentation</h3>
                        <p>Interactive Swagger docs</p>
                    </a>
                </div>
                
                <div class="subtitle">🔗 API Endpoints</div>
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/polls/
                    <span class="badge">List polls</span>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/polls/
                    <span class="badge">Create poll</span>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/polls/bulk/create/
                    <span class="badge">Create multiple polls</span>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/polls/&lt;id&gt;/vote/
                    <span class="badge">Submit vote</span>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/polls/&lt;id&gt;/bulk-vote/
                    <span class="badge">Bulk vote in poll</span>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/polls/&lt;id&gt;/results/
                    <span class="badge">Get results</span>
                </div>
                
                <div class="footer">
                    <p>© 2026 - Developed by <strong>Kopila Devkota</strong></p>
                    <p>Poll API v1.0 | All Rights Reserved</p>
                </div>
            </div>
        </body>
        </html>
        """,
        content_type="text/html; charset=utf-8"
    )

# Configure URL patterns
urlpatterns = [
    path('', root_view, name='root'),
    path('ui/', TemplateView.as_view(template_name='polls/voting_ui.html'), name='voting-ui'),
    path('bulk/', TemplateView.as_view(template_name='polls/bulk_create.html'), name='bulk-create'),
    path('bulk-vote/', TemplateView.as_view(template_name='polls/bulk_vote.html'), name='bulk-vote-ui'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('polls.urls')),
]

# Add drf_yasg URLs only if available
if DRF_YASG_AVAILABLE:
    schema_view = get_schema_view(
        openapi.Info(
            title="Poll API",
            default_version='v1',
            description="Professional Poll Management API developed by Kopila Devkota",
            contact=openapi.Contact(email="kopila@example.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# Add debug toolbar
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass