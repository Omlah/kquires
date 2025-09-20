# Multi-Language Article System - User Guide

## Overview

This guide explains the multi-language article system that automatically creates and manages English and Arabic versions of articles. The system uses AI to detect the language of your content and automatically generates translations.

## 🚀 Getting Started

### Prerequisites

- Django application with the article system installed
- PostgreSQL database configured
- AI services configured for language detection and translation

### Installation

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## 📝 How to Use the Multi-Language Article System

### Creating a New Article

1. **Navigate to Articles:**
   - Go to the Articles section in your dashboard
   - Click the "New Article" button

2. **Fill in Article Details:**
   - **Title**: Enter your article title in either English or Arabic
   - **Category**: Select the appropriate category (required)
   - **Short Description**: Provide a brief summary
   - **Brief Description**: Add the main content using the rich text editor
   - **Attachment**: Optionally upload a file attachment

3. **Automatic Language Detection:**
   - The system automatically detects the language of your content
   - AI creates both English and Arabic versions automatically
   - You'll see a success message indicating both versions were created

4. **Save the Article:**
   - Click "Save" to create the article
   - Both language versions are saved simultaneously

### Editing Existing Articles

1. **Open Article for Editing:**
   - Find your article in the articles list
   - Click the "Edit" button

2. **Language Switching:**
   - Use the language dropdown (🌐 Language) in the modal header
   - Switch between:
     - 🇺🇸 English
     - 🇸🇦 العربية (Arabic)

3. **Edit Content:**
   - Make your changes in the current language
   - The system remembers which language version you're editing

4. **Save Changes:**
   - Click "Save" to update the specific language version
   - Changes are saved only to the language you were editing

### Language Switching Features

#### Available Language Options

- **English (🇺🇸)**: View and edit the English version
- **Arabic (🇸🇦)**: View and edit the Arabic version
- **Create Translation (+ symbol)**: If a translation doesn't exist, you'll see a "+" symbol to create it

#### How Language Switching Works

1. **Viewing Different Languages:**
   - Click the language dropdown
   - Select your desired language
   - The content automatically switches to that language version

2. **Editing in Different Languages:**
   - Switch to the desired language
   - Make your edits
   - Save - only that language version is updated

3. **Creating Missing Translations:**
   - If you see a "+" next to a language option, click it
   - The system will generate a translation using AI
   - Wait for the translation to complete

## 🔧 Technical Implementation Details

### What Was Fixed

The language switching issue has been resolved with the following improvements:

#### Frontend Changes

1. **Language Tracking:**
   - Added `current_language` hidden field to track which language is being edited
   - Enhanced JavaScript to store both main article ID and current article ID

2. **Improved Language Switching:**
   - Modified `switchArticleLanguage()` function to use main article ID
   - Enhanced form state management for proper language context

3. **Better User Experience:**
   - Language dropdown shows current language
   - Clear indication when translations need to be created
   - Proper form reset when switching languages

#### Backend Changes

1. **Language-Aware Updates:**
   - Modified `ArticleCreateOrUpdateView.post()` to determine correct article record
   - System now updates the right language version based on current language

2. **Enhanced API Response:**
   - `article_detail_api` returns both specific language article ID and main article ID
   - Proper article selection for language-specific content

3. **Improved Data Management:**
   - Correct record selection for updates
   - Proper handling of main articles vs translations

### Database Structure

The system uses the following key fields in the Article model:

- `language`: The language of the current article version
- `parent_article`: Links translation articles to their main article
- `original_language`: The language the article was originally written in
- `translation_status`: Tracks the status of translations
- `ai_translated`: Indicates if the content was AI-generated

## 🎯 Best Practices

### Content Creation

1. **Write Naturally:**
   - Write your content in your preferred language
   - The system will detect the language automatically
   - Don't worry about mixing languages - the AI handles it

2. **Review Translations:**
   - Always review AI-generated translations
   - Edit translations if needed for accuracy
   - Save changes to the specific language version

3. **Consistent Categories:**
   - Use the same categories for both language versions
   - This ensures proper organization

### Editing Workflow

1. **Language-Specific Edits:**
   - Make edits in the language you want to update
   - Switch languages to edit different versions
   - Each language version is independent

2. **Content Synchronization:**
   - Major content changes should be made in both languages
   - Use the language switcher to ensure consistency
   - Review both versions before publishing

## 🐛 Troubleshooting

### Common Issues

1. **Language Not Switching:**
   - Refresh the page and try again
   - Check browser console for JavaScript errors
   - Ensure the article has both language versions

2. **Translation Not Created:**
   - Check if AI services are properly configured
   - Verify database connectivity
   - Check server logs for error messages

3. **Content Not Saving:**
   - Ensure you're editing the correct language version
   - Check if the category is selected (required field)
   - Verify form validation passes

### Debug Information

The system provides console logging for debugging:
- Language switching events
- Article fetching details
- Translation creation status

## 📊 System Requirements

### Server Requirements

- Python 3.8+
- Django 4.0+
- PostgreSQL database
- AI service integration (for translations)

### Browser Requirements

- Modern web browser with JavaScript enabled
- Support for ES6+ features
- Bootstrap 5 compatibility

## 🔄 Migration Notes

If you're upgrading from a previous version:

1. **Backup Your Database:**
   ```bash
   python manage.py dumpdata > backup.json
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Test Language Switching:**
   - Create a test article
   - Verify language switching works
   - Check that edits save to correct language versions

## 📞 Support

If you encounter issues:

1. Check the browser console for JavaScript errors
2. Review Django server logs
3. Verify database connectivity
4. Ensure AI services are properly configured

## 🎉 What's New

### Recent Improvements

- ✅ Fixed language switching issue
- ✅ Enhanced article update logic
- ✅ Improved user interface for language selection
- ✅ Better error handling and user feedback
- ✅ Optimized database queries for language-specific content

### Future Enhancements

- Real-time translation preview
- Bulk translation operations
- Advanced language detection
- Translation quality scoring

---

**Last Updated:** $(date)
**Version:** 1.0.0
**Author:** Development Team
