
# =====================
# Импорт необходимых библиотек и глобальные объекты
# =====================
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import os
import mimetypes

# Создание blueprint для админки
admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

# Декоратор для проверки авторизации администратора
def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================
# View-функции (маршруты)
# =====================

@admin_bp.route('/documents/delete/<int:doc_id>', methods=['POST'])
@admin_required
def delete_document(doc_id):
    """Delete a document by id"""
    try:
        from models import Document
        from models import db
        document = Document.query.get(doc_id)
        if document:
            document.is_active = False
            db.session.commit()
            flash('Документ удалён', 'success')
        else:
            flash('Документ не найден', 'error')
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {str(e)}")
        flash('Ошибка при удалении документа', 'error')
    return redirect(url_for('admin.documents'))

@admin_bp.route('/documents/upload', methods=['POST'])
@admin_required
def upload_document():
    """Upload a new document"""
    try:
        from models import Document
        from models import db
        file = request.files.get('file')
        logger.info("[UPLOAD] Получен запрос на загрузку документа")
        if not file or file.filename == '':
            logger.warning("[UPLOAD] Файл не выбран")
            flash('Файл не выбран', 'error')
            return redirect(url_for('admin.documents'))
        filename = secure_filename(file.filename)
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        logger.info(f"[UPLOAD] Файл сохранён: {file_path}")
        file_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        file_type = file_type[:50]
        admin_id = session.get('admin_id')
        if not admin_id:
            logger.warning("[UPLOAD] Не найден admin_id в сессии")
            flash('Ошибка авторизации администратора', 'error')
            return redirect(url_for('admin.documents'))
        # --- Автоматическая обработка документа ---
        from document_processor import DocumentProcessor
        processor = DocumentProcessor(upload_folder=upload_folder)
        content_text = ""
        is_processed = False
        logger.info(f"[PROCESS] Начинаю обработку файла: {filename} ({file_type})")
        try:
            if file_type.startswith('text'):
                content_text = processor.process_text_file(file_path)
                is_processed = True if content_text else False
                logger.info(f"[PROCESS] Текстовый файл обработан: {is_processed}")
            elif file_type == 'application/pdf':
                content_text = processor.process_pdf_file(file_path)
                is_processed = True if content_text else False
                logger.info(f"[PROCESS] PDF обработан: {is_processed}")
            elif file_type == 'application/msword':
                content_text = processor.process_doc_file(file_path)
                is_processed = True if content_text else False
                logger.info(f"[PROCESS] DOC обработан: {is_processed}")
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                content_text = processor.process_docx_file(file_path)
                is_processed = True if content_text else False
                logger.info(f"[PROCESS] DOCX обработан: {is_processed}")
            elif file_type == 'text/html':
                content_text = processor.process_html_file(file_path)
                is_processed = True if content_text else False
                logger.info(f"[PROCESS] HTML обработан: {is_processed}")
            else:
                logger.warning(f"[PROCESS] Неизвестный тип файла: {file_type}")
        except Exception as e:
            logger.error(f"[PROCESS] Ошибка при обработке {filename}: {str(e)}")
            content_text = ""
            is_processed = False

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
        title = request.form.get('title', '').strip() or filename
        logger.info(f"[DB] Сохраняю документ в БД: {title}, размер: {file_size}, обработан: {is_processed}")
        document = Document(
            title=title,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            content_text=content_text,
            is_processed=is_processed,
            is_active=True,
            created_at=datetime.utcnow(),
            uploaded_by=admin_id
        )
        db.session.add(document)
        db.session.commit()
        logger.info(f"[DB] Документ успешно сохранён: {document.id}")
        flash('Документ успешно загружен и обработан' if is_processed else 'Документ загружен, но не обработан', 'success')
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        flash('Ошибка при загрузке документа', 'error')
    return redirect(url_for('admin.documents'))


# Главная страница админки с общей статистикой
@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    try:
        # Импорт моделей и базы данных (отложенный импорт для избежания циклов)
        from models import UserQuery, Document, WebSource, KnowledgeBase, AgentKnowledgeBase, db

        # Получение статистики
        total_queries = UserQuery.query.count()
        total_documents = Document.query.filter_by(is_active=True).count()
        total_web_sources = WebSource.query.filter_by(is_active=True).count()
        total_kb_chunks = KnowledgeBase.query.filter_by(is_active=True).count()
        total_agent_knowledge = AgentKnowledgeBase.query.filter_by(is_active=True).count()

        # Последние 10 запросов пользователей
        recent_queries = UserQuery.query.order_by(UserQuery.created_at.desc()).limit(10).all()

        # Статистика по дням за последнюю неделю
        week_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(UserQuery.created_at).label('date'),
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.created_at >= week_ago
        ).group_by(
            func.date(UserQuery.created_at)
        ).all()

        # Среднее время ответа
        avg_response_time = db.session.query(
            func.avg(UserQuery.response_time)
        ).scalar() or 0

        # Статистика оценок
        total_ratings = db.session.query(func.count(UserQuery.id)).filter(
            UserQuery.user_rating.isnot(None)
        ).scalar() or 0

        total_likes = db.session.query(func.count(UserQuery.id)).filter(
            UserQuery.user_rating == 'like'
        ).scalar() or 0

        satisfaction_rate = round((total_likes / total_ratings * 100) if total_ratings > 0 else 0, 1)

        return render_template('admin/dashboard.html',
                             total_queries=total_queries,
                             total_documents=total_documents,
                             total_web_sources=total_web_sources,
                             total_kb_chunks=total_kb_chunks,
                             total_agent_knowledge=total_agent_knowledge,
                             recent_queries=recent_queries,
                             daily_stats=daily_stats,
                             avg_response_time=round(avg_response_time, 2),
                             total_ratings=total_ratings,
                             total_likes=total_likes,
                             satisfaction_rate=satisfaction_rate)
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        flash('Ошибка при загрузке панели управления', 'error')
        return render_template('admin/dashboard.html')
# ...existing code...

# ...existing code...

@admin_bp.route('/queries')
@admin_required
def queries():
    """View user queries"""
    try:
        from models import UserQuery

        page = request.args.get('page', 1, type=int)
        language = request.args.get('language')

        query = UserQuery.query
        if language:
            query = query.filter_by(language=language)

        queries_list = query.order_by(UserQuery.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )

        return render_template('admin/queries.html', 
                             queries=queries_list,
                             selected_language=language)
    except Exception as e:
        logger.error(f"Error in queries page: {str(e)}")
        flash('Ошибка при загрузке запросов', 'error')
        return render_template('admin/queries.html', queries=None)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        from models import AdminUser, db
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if username and password:
            admin = AdminUser.query.filter_by(username=username, is_active=True).first()
            if admin and admin.check_password(password):
                session['admin_id'] = admin.id
                admin.last_login = datetime.utcnow()
                db.session.commit()
                flash('Добро пожаловать в панель администратора', 'success')
                return redirect(url_for('admin.dashboard'))

        flash('Неверное имя пользователя или пароль', 'error')

    return render_template('admin/login.html')

# Knowledge Management Routes (simplified for now)

@admin_bp.route('/documents')
@admin_required
def documents():
    """Manage documents"""
    try:
        from models import Document

        page = request.args.get('page', 1, type=int)
        documents_list = Document.query.filter_by(is_active=True).order_by(
            Document.created_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)

        return render_template('admin/documents.html', documents=documents_list)
    except Exception as e:
        logger.error(f"Error in documents page: {str(e)}")
        flash('Ошибка при загрузке документов', 'error')
        return render_template('admin/documents.html', documents=None)

@admin_bp.route('/web-sources')
@admin_required
def web_sources():
    """Manage web sources"""
    try:
        from models import WebSource

        page = request.args.get('page', 1, type=int)
        sources_list = WebSource.query.filter_by(is_active=True).order_by(
            WebSource.created_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)

        return render_template('admin/web_sources.html', sources=sources_list)
    except Exception as e:
        logger.error(f"Error in web sources page: {str(e)}")
        flash('Ошибка при загрузке веб-источников', 'error')
        return render_template('admin/web_sources.html', sources=None)

# Добавление веб-источника
@admin_bp.route('/web-sources/add', methods=['POST'])
@admin_required
def add_web_source():
    """Add new web source"""
    try:
        from models import WebSource
        from models import db
        title = request.form.get('title', '').strip()
        url = request.form.get('url', '').strip()
        if not title or not url:
            flash('Название и URL обязательны', 'error')
            return redirect(url_for('admin.web_sources'))
        admin_id = session.get('admin_id')
        web_source = WebSource(
            title=title,
            url=url,
            is_active=True,
            added_by=admin_id,
            created_at=datetime.utcnow()
        )
        db.session.add(web_source)
        db.session.commit()
        flash('Веб-источник успешно добавлен', 'success')
    except Exception as e:
        logger.error(f"Error adding web source: {str(e)}")
        flash('Ошибка при добавлении веб-источника', 'error')
    return redirect(url_for('admin.web_sources'))
    
@admin_bp.route('/knowledge-base')
@admin_required
def knowledge_base():
    """View knowledge base"""
    try:
        from models import KnowledgeBase

        page = request.args.get('page', 1, type=int)
        source_type = request.args.get('source_type', '')

        query = KnowledgeBase.query.filter_by(is_active=True)
        if source_type:
            query = query.filter_by(source_type=source_type)

        kb_entries = query.order_by(KnowledgeBase.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )

        # Get statistics
        total_chunks = KnowledgeBase.query.filter_by(is_active=True).count()
        doc_chunks = KnowledgeBase.query.filter_by(is_active=True, source_type='document').count()
        web_chunks = KnowledgeBase.query.filter_by(is_active=True, source_type='web').count()

        stats = {
            'total': total_chunks,
            'documents': doc_chunks,
            'web': web_chunks
        }

        return render_template('admin/knowledge_base.html', 
                             entries=kb_entries, 
                             stats=stats,
                             selected_source_type=source_type)
    except Exception as e:
        logger.error(f"Error in knowledge base page: {str(e)}")
        flash('Ошибка при загрузке базы знаний', 'error')
        return render_template('admin/knowledge_base.html', entries=None, stats={})

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_id', None)
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/api/analytics/agents')
@admin_required
def agent_analytics():
    """Get agent usage analytics"""
    try:
        from models import UserQuery
        from models import db

        # Get agent usage statistics
        agent_stats = db.session.query(
            UserQuery.agent_type,
            UserQuery.agent_name,
            func.count(UserQuery.id).label('total_queries'),
            func.avg(UserQuery.response_time).label('avg_response_time'),
            func.avg(UserQuery.agent_confidence).label('avg_confidence')
        ).filter(
            UserQuery.agent_type.isnot(None)
        ).group_by(
            UserQuery.agent_type, UserQuery.agent_name
        ).all()

        # Get language distribution by agent
        language_stats = db.session.query(
            UserQuery.agent_type,
            UserQuery.language,
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.agent_type.isnot(None)
        ).group_by(
            UserQuery.agent_type, UserQuery.language
        ).all()

        # Get daily usage for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        daily_stats = db.session.query(
            func.date(UserQuery.created_at).label('date'),
            UserQuery.agent_type,
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.created_at >= thirty_days_ago,
            UserQuery.agent_type.isnot(None)
        ).group_by(
            func.date(UserQuery.created_at), UserQuery.agent_type
        ).all()

        # Format data for frontend
        result = {
            'agent_stats': [
                {
                    'agent_type': stat.agent_type,
                    'agent_name': stat.agent_name,
                    'total_queries': stat.total_queries,
                    'avg_response_time': round(stat.avg_response_time or 0, 2),
                    'avg_confidence': round(stat.avg_confidence or 0, 2)
                }
                for stat in agent_stats
            ],
            'language_stats': [
                {
                    'agent_type': stat.agent_type,
                    'language': stat.language,
                    'count': stat.count
                }
                for stat in language_stats
            ],
            'daily_stats': [
                {
                    'date': stat.date.isoformat(),
                    'agent_type': stat.agent_type,
                    'count': stat.count
                }
                for stat in daily_stats
            ]
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting agent analytics: {str(e)}")
        return jsonify({'error': 'Failed to get analytics data'}), 500


@admin_bp.route('/api/analytics/summary')
@admin_required
def analytics_summary():
    """Get summary analytics for dashboard"""
    try:
        from models import UserQuery
        from models import db

        # Get agent usage data
        agent_usage = db.session.query(
            UserQuery.agent_name,
            func.count(UserQuery.id).label('count'),
            func.avg(UserQuery.response_time).label('avg_response_time'),
            func.avg(UserQuery.agent_confidence).label('avg_confidence')
        ).filter(
            UserQuery.agent_name.isnot(None)
        ).group_by(
            UserQuery.agent_name
        ).all()

        # Get language distribution
        language_distribution = db.session.query(
            UserQuery.language,
            func.count(UserQuery.id).label('count')
        ).group_by(
            UserQuery.language
        ).all()

        # Get daily activity for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_activity = db.session.query(
            func.date(UserQuery.created_at).label('date'),
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.created_at >= thirty_days_ago
        ).group_by(
            func.date(UserQuery.created_at)
        ).order_by(
            func.date(UserQuery.created_at)
        ).all()

        # Get rating statistics
        total_ratings = db.session.query(func.count(UserQuery.id)).filter(
            UserQuery.user_rating.isnot(None)
        ).scalar() or 0

        likes = db.session.query(func.count(UserQuery.id)).filter(
            UserQuery.user_rating == 'like'
        ).scalar() or 0

        dislikes = db.session.query(func.count(UserQuery.id)).filter(
            UserQuery.user_rating == 'dislike'
        ).scalar() or 0

        # Rating distribution by agent
        rating_by_agent = db.session.query(
            UserQuery.agent_name,
            UserQuery.user_rating,
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.user_rating.isnot(None),
            UserQuery.agent_name.isnot(None)
        ).group_by(
            UserQuery.agent_name, UserQuery.user_rating
        ).all()

        # Daily rating trends for last 30 days
        daily_ratings = db.session.query(
            func.date(UserQuery.created_at).label('date'),
            UserQuery.user_rating,
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.created_at >= thirty_days_ago,
            UserQuery.user_rating.isnot(None)
        ).group_by(
            func.date(UserQuery.created_at), UserQuery.user_rating
        ).order_by(
            func.date(UserQuery.created_at)
        ).all()

        result = {
            'agent_usage': [
                {
                    'name': stat.agent_name or 'Неизвестный агент',
                    'count': stat.count,
                    'avg_response_time': round(stat.avg_response_time or 0, 2),
                    'avg_confidence': round(stat.avg_confidence or 0, 2)
                }
                for stat in agent_usage
            ],
            'language_distribution': [
                {
                    'language': stat.language,
                    'count': stat.count
                }
                for stat in language_distribution
            ],
            'daily_activity': [
                {
                    'date': stat.date.isoformat() if stat.date else '',
                    'count': stat.count
                }
                for stat in daily_activity
            ],
            'rating_stats': {
                'total_ratings': total_ratings,
                'likes': likes,
                'dislikes': dislikes,
                'satisfaction_rate': round((likes / total_ratings * 100) if total_ratings > 0 else 0, 1)
            },
            'rating_by_agent': [
                {
                    'agent_name': stat.agent_name or 'Неизвестный агент',
                    'rating': stat.user_rating,
                    'count': stat.count
                }
                for stat in rating_by_agent
            ],
            'daily_ratings': [
                {
                    'date': stat.date.isoformat() if stat.date else '',
                    'rating': stat.user_rating,
                    'count': stat.count
                }
                for stat in daily_ratings
            ]
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        return jsonify({'error': 'Failed to get summary data'}), 500


# =====================
# Управление базами знаний агентов
# =====================

@admin_bp.route('/agent-knowledge')
@admin_required
def agent_knowledge():
    """Manage agent knowledge bases"""
    try:
        from models import AgentKnowledgeBase, AgentType
        from models import db

        # Получение параметров фильтрации
        agent_type = request.args.get('agent_type')
        status = request.args.get('status')
        priority = request.args.get('priority')
        page = request.args.get('page', 1, type=int)

        # Строим запрос с фильтрами
        query = AgentKnowledgeBase.query
        
        if agent_type:
            query = query.filter_by(agent_type=agent_type)
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        elif status == 'featured':
            query = query.filter_by(is_featured=True)
        if priority:
            query = query.filter_by(priority=int(priority))

        # Пагинация
        knowledge_entries = query.order_by(
            AgentKnowledgeBase.priority.asc(),
            AgentKnowledgeBase.updated_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)

        # Статистика
        total_entries = AgentKnowledgeBase.query.count()
        active_entries = AgentKnowledgeBase.query.filter_by(is_active=True).count()
        featured_entries = AgentKnowledgeBase.query.filter_by(is_featured=True).count()
        agent_types_count = AgentType.query.count()

        return render_template('admin/agent_knowledge.html',
                             knowledge_entries=knowledge_entries.items,
                             total_entries=total_entries,
                             active_entries=active_entries,
                             featured_entries=featured_entries,
                             agent_types_count=agent_types_count,
                             pagination=knowledge_entries)

    except Exception as e:
        logger.error(f"Error in agent knowledge page: {str(e)}")
        flash('Ошибка при загрузке базы знаний агентов', 'error')
        return render_template('admin/agent_knowledge.html',
                             knowledge_entries=[],
                             total_entries=0,
                             active_entries=0,
                             featured_entries=0,
                             agent_types_count=0)


@admin_bp.route('/api/knowledge', methods=['POST'])
@admin_required
def add_knowledge():
    """Add new knowledge entry via API"""
    try:
        from models import AgentKnowledgeBase
        from models import db

        data = request.get_json()

        # Валидация данных
        if not all([data.get('title'), data.get('agent_type'), 
                   data.get('content_ru'), data.get('content_kz')]):
            return jsonify({'success': False, 'error': 'Обязательные поля не заполнены'})

        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({'success': False, 'error': 'Ошибка авторизации администратора'})

        # Создание новой записи
        knowledge = AgentKnowledgeBase(
            title=data['title'].strip(),
            agent_type=data['agent_type'],
            content_ru=data['content_ru'].strip(),
            content_kz=data['content_kz'].strip(),
            content_en=data.get('content_en', '').strip(),
            keywords=data.get('keywords', '').strip(),
            priority=int(data.get('priority', 2)),
            category=data.get('category', '').strip(),
            is_featured=bool(data.get('is_featured', False)),
            is_active=bool(data.get('is_active', True)),
            created_by=admin_id,  # <---- ОБЯЗАТЕЛЬНО
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(knowledge)
        db.session.commit()

        logger.info(f"Added knowledge entry: {knowledge.title} for {knowledge.agent_type}")
        return jsonify({'success': True, 'id': knowledge.id})

    except Exception as e:
        logger.error(f"Error adding knowledge entry: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка сервера'})

@admin_bp.route('/api/knowledge/<int:knowledge_id>/toggle-featured', methods=['PUT'])
@admin_required
def toggle_featured(knowledge_id):
    """Toggle featured status of knowledge entry"""
    try:
        from models import AgentKnowledgeBase
        from models import db

        knowledge = AgentKnowledgeBase.query.get_or_404(knowledge_id)
        knowledge.is_featured = not knowledge.is_featured
        knowledge.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'is_featured': knowledge.is_featured})

    except Exception as e:
        logger.error(f"Error toggling featured status for knowledge {knowledge_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка обновления'})


@admin_bp.route('/api/knowledge/<int:knowledge_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_active(knowledge_id):
    """Toggle active status of knowledge entry"""
    try:
        from models import AgentKnowledgeBase
        from models import db

        knowledge = AgentKnowledgeBase.query.get_or_404(knowledge_id)
        knowledge.is_active = not knowledge.is_active
        knowledge.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'is_active': knowledge.is_active})

    except Exception as e:
        logger.error(f"Error toggling active status for knowledge {knowledge_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка обновления'})


@admin_bp.route('/api/knowledge/<int:knowledge_id>', methods=['DELETE'])
@admin_required
def delete_knowledge(knowledge_id):
    """Delete knowledge entry"""
    try:
        from models import AgentKnowledgeBase
        from models import db

        knowledge = AgentKnowledgeBase.query.get_or_404(knowledge_id)
        db.session.delete(knowledge)
        db.session.commit()
        
        logger.info(f"Deleted knowledge entry: {knowledge.title}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error deleting knowledge {knowledge_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка удаления'})


@admin_bp.route('/api/knowledge/<int:knowledge_id>', methods=['GET'])
@admin_required
def get_knowledge(knowledge_id):
    """Get knowledge entry details for editing"""
    try:
        from models import AgentKnowledgeBase

        knowledge = AgentKnowledgeBase.query.get_or_404(knowledge_id)
        
        return jsonify({
            'success': True,
            'id': knowledge.id,
            'title': knowledge.title or '',
            'agent_type': knowledge.agent_type or '',
            'content_ru': knowledge.content_ru or '',
            'content_kz': knowledge.content_kz or '',
            'content_en': knowledge.content_en or '',
            'keywords': knowledge.keywords or '',
            'priority': knowledge.priority or 1,
            'category': knowledge.category or '',
            'is_featured': knowledge.is_featured or False,
            'is_active': knowledge.is_active or True
        })

    except Exception as e:
        logger.error(f"Error getting knowledge {knowledge_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка получения данных'})


@admin_bp.route('/api/knowledge/<int:knowledge_id>', methods=['PUT'])
@admin_required
def update_knowledge(knowledge_id):
    """Update knowledge entry"""
    try:
        from models import AgentKnowledgeBase
        from models import db

        knowledge = AgentKnowledgeBase.query.get_or_404(knowledge_id)
        data = request.get_json()
        
        # Валидация данных
        if not all([data.get('title'), data.get('agent_type'), 
                   data.get('content_ru'), data.get('content_kz')]):
            return jsonify({'success': False, 'error': 'Обязательные поля не заполнены'})

        # Обновление полей
        knowledge.title = data['title'].strip()
        knowledge.agent_type = data['agent_type']
        knowledge.content_ru = data['content_ru'].strip()
        knowledge.content_kz = data['content_kz'].strip()
        knowledge.content_en = data.get('content_en', '').strip()
        knowledge.keywords = data.get('keywords', '').strip()
        knowledge.priority = int(data.get('priority', 2))
        knowledge.category = data.get('category', '').strip()
        knowledge.is_featured = bool(data.get('is_featured', False))
        knowledge.is_active = bool(data.get('is_active', True))
        knowledge.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Updated knowledge entry: {knowledge.title}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error updating knowledge {knowledge_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ошибка обновления'})
