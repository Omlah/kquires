# Role-Based Floating Chatbot Implementation

## Overview

This implementation adds a role-based floating chatbot widget that appears at the bottom right of every page for authenticated users. The chatbot provides personalized article recommendations and assistance based on the user's role within the organization.

## Features

### 🤖 **Floating Chatbot Widget**
- Appears on every page for authenticated users
- Positioned at bottom-right corner
- Responsive design that works on mobile and desktop
- Smooth animations and modern UI

### 👥 **Role-Based Functionality**
- **Admin**: Access to all articles, system administration guides
- **Approval Manager**: Pending articles, content review guidelines
- **Article Writer**: Writing guidelines, draft articles, publishing workflow
- **Manager**: Team management, department procedures, leadership resources
- **Employee**: Getting started guides, common procedures, FAQ

### 🎯 **Smart Article Filtering**
- Articles are filtered based on user's role and department
- Personalized quick suggestions for each role
- Context-aware responses from AI assistant

### 💬 **Interactive Features**
- Real-time messaging with typing indicators
- Quick suggestion buttons for common queries
- Referenced articles with direct links
- Chat history persistence

## Files Created/Modified

### New Files
1. **`kquires/chatbot/role_based_service.py`** - Core service for role-based article filtering
2. **`kquires/templates/chatbot/floating_widget.html`** - Floating chatbot widget template
3. **`kquires/chatbot/migrations/0002_add_role_based_fields.py`** - Database migration

### Modified Files
1. **`kquires/chatbot/models.py`** - Added role-based fields to ChatSession
2. **`kquires/chatbot/views.py`** - Added role-based API endpoints
3. **`kquires/chatbot/urls.py`** - Added new URL patterns
4. **`kquires/chatbot/ai_service.py`** - Enhanced AI service (already updated)
5. **`kquires/templates/base.html`** - Included floating widget
6. **`kquires/users/models.py`** - Added role helper methods

## API Endpoints

### Role-Based Endpoints
- `POST /chatbot/api/send-role-based-message/` - Send message with role context
- `GET /chatbot/api/role-suggestions/` - Get role-specific quick suggestions
- `GET /chatbot/api/role-articles/` - Get popular/recent articles for user's role

## Database Schema Changes

### ChatSession Model
```python
# New fields added:
user_role = CharField(max_length=100, blank=True)
department = ForeignKey('departments.Department', null=True, blank=True)
```

## Role-Based Article Access Logic

### Administrator
- **Access**: All articles regardless of status
- **Suggestions**: System administration, user management, security policies
- **Focus**: Technical documentation, system configuration

### Approval Manager
- **Access**: All approved articles + pending articles for review
- **Suggestions**: Content review guidelines, approval workflows, quality standards
- **Focus**: Content management and quality control

### Article Writer
- **Access**: Approved articles + their own drafts
- **Suggestions**: Writing guidelines, content creation best practices, publishing workflow
- **Focus**: Content creation and writing resources

### Manager
- **Access**: Department-specific articles + general approved articles
- **Suggestions**: Team management, department procedures, leadership resources
- **Focus**: Management and leadership content

### Employee
- **Access**: Approved public articles, department-specific content
- **Suggestions**: Getting started guides, common procedures, FAQ
- **Focus**: Day-to-day operational information

## Usage Instructions

### For Users
1. **Access**: The chatbot icon appears automatically at the bottom-right corner
2. **Interaction**: Click the robot icon to open the chat window
3. **Quick Actions**: Use the suggested buttons for common queries
4. **Custom Queries**: Type any question in the input field
5. **Article Links**: Click on referenced articles to read full content

### For Developers
1. **Customization**: Modify `role_based_service.py` to adjust role-based filtering
2. **Styling**: Update CSS in `floating_widget.html` for visual customization
3. **Suggestions**: Edit `get_role_specific_suggestions()` method to change quick actions
4. **AI Responses**: Modify AI service prompts for different response styles

## Installation Steps

1. **Apply Migration**:
   ```bash
   python manage.py migrate chatbot
   ```

2. **Collect Static Files** (if needed):
   ```bash
   python manage.py collectstatic
   ```

3. **Test the Implementation**:
   - Login as different user roles
   - Verify role-specific suggestions appear
   - Test article filtering based on roles
   - Ensure chatbot appears on all pages

## Configuration

### Environment Variables
The chatbot uses existing OpenAI configuration:
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.3
```

### Role Suggestions Customization
Edit the `get_role_specific_suggestions()` method in `role_based_service.py`:

```python
suggestions = {
    'admin': [
        "Your custom admin suggestions",
        # Add more...
    ],
    # Add other roles...
}
```

## Troubleshooting

### Common Issues

1. **Chatbot not appearing**:
   - Ensure user is authenticated
   - Check if `floating_widget.html` is included in base template
   - Verify CSS is loading correctly

2. **Role-based filtering not working**:
   - Check user role assignments in admin panel
   - Verify `get_primary_role()` method returns correct role
   - Ensure articles have proper visibility settings

3. **AI responses not working**:
   - Verify OpenAI API key is configured
   - Check AI service logs for errors
   - Ensure sufficient API credits

4. **Database errors**:
   - Run migrations: `python manage.py migrate chatbot`
   - Check if departments app is properly configured

### Debug Mode
Enable debug logging in Django settings to see detailed chatbot operations:

```python
LOGGING = {
    'loggers': {
        'kquires.chatbot': {
            'level': 'DEBUG',
        },
    },
}
```

## Future Enhancements

### Potential Improvements
1. **Multi-language Support**: Extend chatbot to support multiple languages
2. **Voice Integration**: Add voice input/output capabilities
3. **Advanced Analytics**: Track chatbot usage and effectiveness
4. **Custom Training**: Train AI on organization-specific content
5. **Integration**: Connect with external knowledge bases or APIs
6. **Mobile App**: Extend functionality to mobile applications

### Performance Optimizations
1. **Caching**: Implement Redis caching for frequent queries
2. **Pagination**: Add pagination for large article sets
3. **Lazy Loading**: Load chat history on demand
4. **CDN**: Use CDN for static assets

## Security Considerations

1. **User Authentication**: All endpoints require authentication
2. **Role Validation**: Server-side role validation for all requests
3. **Input Sanitization**: All user inputs are sanitized
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints
5. **Data Privacy**: Chat messages are stored securely with user association

## Support

For technical support or questions about this implementation:
1. Check the troubleshooting section above
2. Review Django and OpenAI documentation
3. Contact the development team for custom modifications

---

**Implementation completed successfully!** 🎉

The role-based floating chatbot is now ready for use across your Kquires knowledge base system.
